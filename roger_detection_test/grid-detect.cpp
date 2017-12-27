#include <caffe/caffe.hpp>
#include <opencv2/opencv.hpp>

/*
TODO:
    - Finish Main
        - NN for white digits
        - comm communication
        - CV-recog and NN for red digits
        - test demo
*/

const bool _DEBUG = false;

using namespace cv;
using namespace std;
using namespace caffe;

Scalar lower_red_1(0, 4, 210);
Scalar upper_red_1(25, 255, 255);
Scalar lower_red_2(155, 4, 210);
Scalar upper_red_2(179, 255, 255);

struct contours_and_dig{
    int dig_id;
    int x;
};

bool sort_by_x(contours_and_dig &i, contours_and_dig &j) { return i.x < j.x; }
bool sort_by_y(Point i, Point j) { return i.y < j.y; }
bool sort_by_zero(Rect i, Rect j) { return i.x < j.x; }
bool sort_by_first(Rect i, Rect j) { return i.y < j.y; }

static vector<int> get_cnt_x_vector(vector<Point> cnt){
    vector<int> ret;
    for(size_t i = 0; i < cnt.size(); i++){
        ret.push_back(cnt[i].x);
    }
    return ret;
}

static vector<int> get_cnt_y_vector(vector<Point> cnt){
    vector<int> ret;
    for(size_t i = 0; i < cnt.size(); i++){
        ret.push_back(cnt[i].y);
    }
    return ret;
}

static Mat pad_diggit(Mat img){
    int w = img.size().width;
    int h = img.size().height;
    int length = static_cast<int>(h * 1.4);
    int v_pad = (length - h) / 2;
    int h_pad = (length - w) / 2;
    Mat new_img;
    copyMakeBorder(img, new_img, v_pad, v_pad, h_pad, h_pad, BORDER_CONSTANT, 0);
    Size mnist_size(28, 28);
    Mat ret_img;
    resize(new_img, ret_img, mnist_size);
    return ret_img;
}

vector<Point> extract_nth_point_from_contours(vector<vector<Point> > points, int pos){
    vector<Point> ret;
    for(size_t i = 0; i < points.size(); i++){
        ret.push_back(points[i][pos]);
    }
    return ret;
}

//expect length of input array is greater than 9
static vector<int> rank(vector<int> dig_ids, vector<vector<Point> > contours_array){
    vector<vector<contours_and_dig> > unranked;
    for(int i = 0; i < 9; i++){
        contours_and_dig pack;
        pack.dig_id = dig_ids[i];
        pack.x = contours_array[i][0].x;
        unranked[2 - (i / 3)].push_back(pack);
    }
    vector<int> ret;
    for(int i = 0; i < unranked.size(); i++){
        sort(unranked[i].begin(), unranked[i].end(), sort_by_x);
        for(int j = 0; j < 3; j++){
            ret.push_back(unranked[i][j].dig_id);
        }
    }
    return ret;
}

static Mat mask_process(Mat mask, vector<vector<Point> > points){
    Mat kernel1 = Mat::ones(5, 4, CV_8UC1);
    Mat kernel2 = Mat::ones(4, 4, CV_8UC1);
    morphologyEx(mask, mask, MORPH_CLOSE, kernel1);
    morphologyEx(mask, mask, MORPH_OPEN, kernel2);
    //use python-like sort here
    vector<int> y_min_vector = get_cnt_y_vector(extract_nth_point_from_contours(points, 0));
    vector<int> x_min_vector_1 = get_cnt_x_vector(extract_nth_point_from_contours(points, 1));
    vector<int> x_min_vector_2 = get_cnt_x_vector(extract_nth_point_from_contours(points, 0));
    int y_min = *min_element(y_min_vector.begin(), y_min_vector.end());
    int x_min1 = *min_element(x_min_vector_1.begin(), x_min_vector_1.end());
    int x_min2 = *max_element(x_min_vector_1.begin(), x_min_vector_2.end());
    int w = mask.size().width;
    int h = mask.size().height;
    Mat ftr = Mat::ones(w, h, CV_8UC1);
    for(int i = y_min; i < h; i++){
        for(int j = 0; j < w; j++){
            ftr.at<uchar>(i, j) = 0; //not very efficient
        }
    }
    for(int i = 0; i < y_min; i++){
        for(int j = 0; j < x_min1; j++){
            ftr.at<uchar>(i, j) = 0;
        }
    }
    for(int i = 0; i < y_min; i++){
        for(int j = x_min2; j < w; j++){
            ftr.at<uchar>(i, j) = 0;
        }
    }
    Mat ret;
    bitwise_and(mask, mask, ret, ftr);
    return ret;
}

static vector<Point> sort_points(vector<Point> points){
    vector<Point> ret = points; //deepcopy
    sort(points.begin(), points.end(), sort_by_y);
    if(points[0].x > points[1].x){
        int temp = points[1].x;
        points[1].x = points[0].x;
        points[0].x = temp;
    }
    if(points[2].x > points[3].x){
        int temp = points[3].x;
        points[3].x = points[2].x;
        points[2].x = temp;
    }
    return ret;
}

static void find_contour_bound(vector<Point> cont, bool raw_cont, int& left, int& right, int& lower, int& upper){
    vector<int> x_vector = get_cnt_x_vector(cont);
    vector<int> y_vector = get_cnt_y_vector(cont);
    left = cont[distance(x_vector.begin(), min_element(x_vector.begin(), x_vector.end()))].x;
    right = cont[distance(x_vector.begin(), max_element(x_vector.begin(), x_vector.end()))].x;
    lower = cont[distance(y_vector.begin(), min_element(y_vector.begin(), y_vector.end()))].y;
    upper = cont[distance(y_vector.begin(), max_element(y_vector.begin(), y_vector.end()))].y;
}

bool filterRects(vector<Point> rect, bool pure_cont){
    int left, right, lower, upper;
    find_contour_bound(rect, false, left, right, lower, upper);
    int x = right - left;
    float y = upper - lower;
    if((y / x >= 0.3) & (y / x <= 0.75)){
        return true;
    } else {
        return false;
    }
}

Mat pre_process(Mat img){
    Mat ret_img;
    GaussianBlur(img, ret_img, Size(3, 3), 0);
    threshold(ret_img, ret_img, 0, 255, THRESH_BINARY + THRESH_OTSU);
    Mat kernel = Mat::ones(4, 8, CV_8UC1);
    morphologyEx(ret_img, ret_img, MORPH_CLOSE, kernel);
    return ret_img;
}

static void find_and_filter_contour(Mat thresh, queue<vector<Point> >& desired_ref){
    vector<vector<Point> > contours;
    queue<vector<Point> > ret;
    vector<Vec4i> hierarchy;
    findContours(thresh, contours, hierarchy, RETR_TREE, CHAIN_APPROX_SIMPLE);
    int width = thresh.size().width;
    int height = thresh.size().height;
    int img_width_range_lower = static_cast<int>(0.1 * width);
    int img_width_range_higher = static_cast<int>(0.3 * width);
    int img_height_range_lower = static_cast<int>(0.08 * width);
    int img_height_range_higher = static_cast<int>(0.18 * width);
    for(size_t i = 0; i < contours.size(); i++){
        int area = contourArea(contours[i]);
        if((filterRects(contours[i], true)) & (area >= img_width_range_lower * img_height_range_lower) & (area <= img_width_range_higher * img_height_range_higher)){
            ret.push(contours[i]);
        }
    }
    desired_ref = ret;
}

static void four_poly_approx(queue<vector<Point> > contours, queue<vector<Point> > &desired_ref){
    queue<vector<Point> > ret;
    while(contours.size() > 0){
        vector<Point> cnt = contours.front();
        vector<Point> aprox;
        contours.pop();
        approxPolyDP(cnt, aprox, 0.05 * arcLength(cnt, true), true);
        if((aprox.size() == 4) & (isContourConvex(aprox))){
            ret.push(aprox);
        }
    }
    desired_ref = ret;
}

static void pad_white_digit(vector<vector<Point> > contours, Mat gray, vector<Mat>& bboxs, vector<vector<Point> >& points, int& digit_height){
    int BOX_LEN = 32;
    int offset = (BOX_LEN - 28) / 2;
    int dstpts_array[8] = {0 ,0, BOX_LEN, 0, 0, BOX_LEN, BOX_LEN, BOX_LEN};
    Mat dstpts = Mat(4, 2, CV_8UC1, dstpts_array);
    vector<int> dynamic_height;
    for(size_t i = 0; i < contours.size(); i++){
        vector<Point> cnt = contours[i];
        vector<Point> pts1 = sort_points(cnt);
        points.push_back(pts1);
        Mat m = getPerspectiveTransform(pts1, dstpts);
        Mat new_img, digit_img;
        warpPerspective(gray, new_img, m, Size(BOX_LEN, BOX_LEN));
        bitwise_not(new_img(Rect(offset, new_img.size().width - offset, offset, new_img.size().height - offset)), digit_img);
        bboxs.push_back(digit_img);
        int left, right, lower, upper;
        find_contour_bound(cnt, false, left, right, lower, upper);
        dynamic_height.push_back(upper - lower);
    }
    digit_height = static_cast<int>(dynamic_height[dynamic_height.size() / 2] * (0.58));
}

static Mat red_color_binarization(Mat org_img){
    Mat mask1, mask2, ret, hsv;
    cvtColor(org_img, hsv, COLOR_BGR2HSV);
    inRange(hsv, Scalar(0, 4, 210), Scalar(25, 255, 255), mask1);
    inRange(hsv, Scalar(155, 4, 210), Scalar(179, 255, 255), mask2);
    bitwise_or(mask1, mask2, ret);
    return ret;
}

//return bound
vector<Rect> bound_red_number(Mat mask){
    vector<vector<Point> > contours;
    vector<Rect> ret, true_ret;
    vector<Vec4i> hierarchy;
    findContours(mask, contours, hierarchy, RETR_TREE, CHAIN_APPROX_SIMPLE);
    for(size_t i = 0; i < contours.size(); i++){
        Rect rec = boundingRect(contours[i]);
        if(rec.width < rec.height){
            ret.push_back(rec);
        }
    }
    sort(ret.begin(), ret.end(), sort_by_zero);
    vector<Rect> y = ret; //deepcopy
    sort(y.begin(), y.end(), sort_by_first);
    int y_coord = y[y.size() / 2].y;
    for(size_t i = 0; i < ret.size(); i++){
        if((ret[i].y >= y_coord * 0.8) & (ret[i].y <= y_coord * 1.23)){
            true_ret.push_back(ret[i]);
        }
    }
    return true_ret;
}

//Mat process(Mat frame, Net<float> &net){
Mat process(Mat frame){
        Mat img, img_cp, thresh, gray, org_mask, mask;
        queue<vector<Point> > contours; //it's a queue!!!
        vector<vector<Point> > vector_contours;
        resize(frame, img, Size(640, 360));
        img.copyTo(img_cp);
        cvtColor(img, gray, COLOR_BGR2GRAY);
        thresh = pre_process(gray);
        find_and_filter_contour(thresh, contours);
        four_poly_approx(contours, contours);
        while(contours.size() > 0){
            vector_contours.push_back(contours.front());
            contours.pop();
        }
        if(vector_contours.size() == 0){
            return img;
        }
        if(_DEBUG){
            stringstream output_stream;
            output_stream << "This is the len of contours" << vector_contours.size();
            string debug_string = output_stream.str();
            cout << debug_string;
        }
        drawContours(img, vector_contours, -1, Scalar(0, 255, 0), 3);
        int digit_height;
        vector<vector<Point> >points;
        vector<Mat> bbox;
        pad_white_digit(vector_contours, gray, bbox, points, digit_height); //what are the types of these variables; probably should pass their reference instead of returning
        /*
        //Feed neural network here
        Blob<vector<Mat> > *input_ptr = net.input_blobs()[0];
        input_ptr->Blob::Reshape(bbox.size(), 1, 28, 28);
        Blob<vector<Mat> > *output_ptr = net.output_blobs()[0];
        output_ptr->Blob::Reshape(bbox.size(), 10, 1, 1);
        input_ptr->set_cpu_data(bbox*);
        net.Forward();
        const float* output_data = output_ptr->cpu_data();
        vector<int> dig_ids;
        for(int i = 0; i < bbox.size(); i++){
            int max_prob_index = 0;
            for(int j = 0; j < 10; j++){
                if(output_data[i][max_prob_index] < output_data[i][j]) { max_prob_index = j; }
            }
            dig_ids.push_back(max_prob_index);
        }
        cout << dig_ids;
        */
        /*
        for(int i = 0; i < sizeof(dig_ids); i++){
            putText(img, string(dig_ids[i]), Scalar(static_cast<int>(points[i][0,0]), static_cast<int>(points[i][0,1]-20)), FONT_HERSHEY_SIMPLEX, 0.9, Scalar(0, 255, 255), 2, LINE_AA);
        }
        */
        if(contours.size() == 9){
            std::cout << "update sequence to benchmark comm here";
        }
        mask = red_color_binarization(img_cp);
        mask.copyTo(org_mask);
        dilate(mask, mask, Mat::ones(static_cast<int>(digit_height / 10), 1, CV_8UC1));
        mask = mask_process(mask, points);
        org_mask = mask_process(org_mask, points);
        vector<Rect> bounding_box = bound_red_number(mask);
        dilate(org_mask, org_mask, Mat::ones(2, 1, CV_8UC1));
        //Putting into recognition module or neural network for recognition
        return img;
}

int main(void){
    VideoCapture cap(0);
    if(!cap.isOpened()) { return -1; }
    //Caffe::set_mode(Caffe::CPU);
    //Net<float> net("./model/lenet.prototxt", caffe::TEST);
    //net.CopyTrainedLayersFrom("./model/mnist_iter_200000.caffemodel");
    while(true){
        Mat frame;
        cap >> frame;
        Mat proc_img = process(frame);
        imshow("debug", proc_img);
        if(waitKey(30) >= 0) break;
    }
}
