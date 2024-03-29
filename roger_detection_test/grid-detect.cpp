#include <caffe/caffe.hpp>
#include <opencv2/opencv.hpp>
#include <caffe/blob.hpp>
#include <caffe/util/io.hpp>

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
static bool PairCompare(const std::pair<float, int>& lhs,
                        const std::pair<float, int>& rhs) {
  return lhs.first > rhs.first;
}

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

static int index_of_min_element_in_vector(vector<int> a_vector){
    if(a_vector.size() == 1){
        return 0;
    }
    int min[2] = {a_vector[0], 0};
    for(int i = 1; i < a_vector.size(); i++){
        if(a_vector[i] < min[0]){
            min[0] = a_vector[i];
            min[1] = i;
        }
    }
    return min[1];
}

static int index_of_max_element_in_vector(vector<int> a_vector){
    if(a_vector.size() == 1){
        return 0;
    }
    int min[2] = {a_vector[0], 0};
    for(int i = 1; i < a_vector.size(); i++){
        if(a_vector[i] > min[0]){
            min[0] = a_vector[i];
            min[1] = i;
        }
    }
    return min[1];
}

static Mat mask_process(Mat mask, vector<vector<Point> > points){
    //cout << "starting mask_process" << endl;
    Mat kernel1 = Mat::ones(5, 4, CV_8UC1);
    Mat kernel2 = Mat::ones(4, 4, CV_8UC1);
    morphologyEx(mask, mask, MORPH_CLOSE, kernel1);
    morphologyEx(mask, mask, MORPH_OPEN, kernel2);
    //cout << "morphological trans success" << endl;
    vector<int> y_min_vector = get_cnt_y_vector(extract_nth_point_from_contours(points, 0)); //TODO: DEBUG
    vector<int> x_min_vector_1 = get_cnt_x_vector(extract_nth_point_from_contours(points, 1));
    vector<int> x_min_vector_2 = get_cnt_x_vector(extract_nth_point_from_contours(points, 0));
    //cout << "obtained vectors" << endl;
    int y_min = y_min_vector[index_of_min_element_in_vector(y_min_vector)];
    /*
    vector<int> path = y_min_vector;
    cout << "y_min size " << y_min_vector.size();
    cout << "path size " << path.size();
    for (vector<int>::const_iterator i = path.begin(); i != path.end(); ++i)
        cout << *i << ' ';
    cout << "obtained min element" << y_min;
    */
    int x_min1 = x_min_vector_1[index_of_min_element_in_vector(x_min_vector_1)];
    int x_min2 = x_min_vector_2[index_of_max_element_in_vector(x_min_vector_2)];
    //cout << "maxmin elements obtained" << endl;
    int w = mask.size().width;
    int h = mask.size().height;
    Mat ftr = Mat::ones(h, w, CV_8UC1);
    //cout << "ftr mask size " << ftr.size() << endl;
    //cout << "mask mat size " << mask.size() << endl;;
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
    //cout << "processed ftr type" << ftr.type() << endl;
    //cout << "prepare for bit and" << endl;
    bitwise_and(mask, mask, ret, ftr);
    //cout << "BIT_AND success" << endl;
    return ret;
}

static vector<Point> sort_points(vector<Point> points){
    vector<Point> ret = points; //deepcopy
    sort(ret.begin(), ret.end(), sort_by_y);
    if(ret[0].x > ret[1].x){
        int temp = ret[1].x;
        ret[1].x = ret[0].x;
        ret[0].x = temp;
    }
    if(ret[2].x > ret[3].x){
        int temp = ret[3].x;
        ret[3].x = ret[2].x;
        ret[2].x = temp;
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
    int offset = (BOX_LEN - 28) / 2; //offset = 2
    Point2f dstpts[4];
    dstpts[0] = Point2f(0, 0);
    dstpts[1] = Point2f(BOX_LEN, 0);
    dstpts[2] = Point2f(0, BOX_LEN);
    dstpts[3] = Point2f(BOX_LEN, BOX_LEN);
    //Mat dstpts = (Mat_<cv::Point_<int> >(1, 4) << Point(0, 0), Point(BOX_LEN, 0), Point(0, BOX_LEN), Point(BOX_LEN, BOX_LEN));
    vector<int> dynamic_height;
    for(size_t i = 0; i < contours.size(); i++){
        vector<Point> cnt = contours[i];
        vector<Point> pts1 = sort_points(cnt);
        points.push_back(pts1);
        Point2f pts1_f[4];
        for(int i = 0; i < 4; i++){
            pts1_f[i] = Point2f(pts1[i]);
        }
        Mat m = getPerspectiveTransform(pts1_f, dstpts);
        Mat new_img, digit_img;
        warpPerspective(gray, new_img, m, Size(BOX_LEN, BOX_LEN));
        bitwise_not(new_img(Rect(offset, offset, new_img.size().width - offset, new_img.size().height - offset)), digit_img);
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
    //real
    //inRange(hsv, Scalar(0, 4, 210), Scalar(25, 255, 255), mask1);
    //inRange(hsv, Scalar(155, 4, 210), Scalar(179, 255, 255), mask2);
    //display parameters
    inRange(hsv, Scalar(0, 90, 70), Scalar(15, 255, 255), mask1);
    inRange(hsv, Scalar(155, 90, 70), Scalar(179, 255, 255), mask2);
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
        //cout << "This is rect " << i << rec << endl;
        if(rec.width < rec.height){
            ret.push_back(rec);
        }
    }
    if(ret.size() == 0){
        return vector<Rect>();
    }
    sort(ret.begin(), ret.end(), sort_by_zero);
    vector<Rect> y = ret; //deepcopy
    sort(y.begin(), y.end(), sort_by_first);
    //cout << "rect size" << y.size() << endl;
    int y_coord = y[y.size() / 2].y;
    //cout << "y coord obtained" << endl;
    for(size_t i = 0; i < ret.size(); i++){
        //cout << "evaluating" << endl;
        if((ret[i].y >= y_coord * 0.8) & (ret[i].y <= y_coord * 1.23)){
            //cout << "pushing " << endl;
            true_ret.push_back(ret[i]);
        }
    }
    //cout << "returning..." << endl;
    return true_ret;
}

static int Argmax(const std::vector<float>& v, int N) {
  std::vector<std::pair<float, int> > pairs;
  for (size_t i = 0; i < v.size(); ++i)
    pairs.push_back(std::make_pair(v[i], i));
  std::partial_sort(pairs.begin(), pairs.begin() + N, pairs.end(), PairCompare);

  std::vector<int> result;
  for (int i = 0; i < N; ++i)
    result.push_back(pairs[i].second);
  return result[0];
}

//Mat process(Mat frame, Net<float> &net){
Mat process(Mat frame, Net<float> &net){
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
            output_stream << "This is the len of contours" << vector_contours.size() << endl;
            string debug_string = output_stream.str();
            cout << debug_string << endl;
        }
        drawContours(img, vector_contours, -1, Scalar(0, 255, 0), 3);
        imwrite("latest_frame.jpg", img);
        int digit_height;
        vector<vector<Point> >points;
        vector<Mat> bbox;
        //cout << "prepare to pad white digit" << endl;
        pad_white_digit(vector_contours, gray, bbox, points, digit_height); //what are the types of these variables; probably should pass their reference instead of returning
        //Feed neural network here
        Blob<float> *input_layer = net.input_blobs()[0];
        //input_layer->Reshape(bboxs.size(), 1, 28, 28);
        input_layer->Reshape(1, 1, 28, 28);
        net.Reshape();
        vector<Mat> input_channels;
        float* input_data = input_layer->mutable_cpu_data();
        Mat channel(28, 28, CV_32FC1, input_data);
        input_channels.push_back(channel);
        vector<int> dig_ids;
        for(int i = 0; i < bbox.size(); i++){
            //split(bbox[i], *input_channels);
            input_channels.push_back(bbox[i]);
            net.Forward();
            Blob<float>* output_layer = net.output_blobs()[0];
            const float* begin = output_layer->cpu_data();
            const float* end = begin + output_layer->channels();
            vector<float> prob_ = vector<float>(begin, end);
            dig_ids.push_back(Argmax(prob_, 1));
        }
        for (vector<int>::const_iterator i = dig_ids.begin(); i != dig_ids.end(); ++i)
            cout << *i << ' ';
        /*
        for(int i = 0; i < sizeof(dig_ids); i++){
            putText(img, string(dig_ids[i]), Scalar(static_cast<int>(points[i][0,0]), static_cast<int>(points[i][0,1]-20)), FONT_HERSHEY_SIMPLEX, 0.9, Scalar(0, 255, 255), 2, LINE_AA);
        }
        */
        if(contours.size() == 9){
            std::cout << "update sequence to benchmark comm here" << endl;
        }
        mask = red_color_binarization(img_cp);
        imwrite("debug.jpg", mask);
        mask.copyTo(org_mask);
        dilate(mask, mask, Mat::ones(static_cast<int>(digit_height / 10), 1, CV_8UC1));
        imwrite("debug_dilate.jpg", mask);
        mask = mask_process(mask, points);
        //cout << "mask process success" << endl;
        org_mask = mask_process(org_mask, points);
        //cout << "org_mask_process success" << endl;
        vector<Rect> bounding_box = bound_red_number(mask);
        //cout << "Bounding box size" << bounding_box.size() << endl;
        for(int i = 0; i < bounding_box.size(); i++){
            rectangle(img, bounding_box[i], Scalar(0, 0, 255), 3);
        }
        dilate(org_mask, org_mask, Mat::ones(2, 1, CV_8UC1)); //improve accuracy
        //Putting into recognition module or neural network for recognition
        return img;
}

int main(void){
    VideoCapture cap(0);
    if(!cap.isOpened()) { return -1; }
    //Caffe::set_phase(Caffe::TEST);
    Caffe::set_mode(Caffe::CPU);
    Net<float> net("./model/lenet.prototxt", caffe::TEST);
    net.CopyTrainedLayersFrom("./model/mnist_iter_200000.caffemodel");
    while(true){
        Mat frame;
        cap >> frame;
        Mat proc_img = process(frame, net);
        imshow("debug", proc_img);
        if(waitKey(30) >= 0) break;
    }
}
