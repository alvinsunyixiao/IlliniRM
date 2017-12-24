#include <caffe/caffe.hpp>
#include <opencv2/opencv.hpp>
/*
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/shape.hpp>*/

/*
TODO:
    - Python-like max, min, sort
    - Try passing reference for results
*/

const bool _DEBUG = false;

using namespace cv;
using namespace std;

Scalar lower_red_1(0, 4, 210);
Scalar upper_red_1(25, 255, 255);
Scalar lower_red_2(155, 4, 210);
Scalar upper_red_2(179, 255, 255);

//Net nn("./model/lenet.prototxt", "./model/mnist_iter_200000.caffemodel", TEST);

int* find_contour_bound(bool = false);
bool filterRects(bool = false);

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
}

int* rank(int* dig_ids, int* contours_array){}

static Mat mask_process(Mat mask, int* points){
    Mat kernel1 = Mat::ones(5, 4, CV_8UC1);
    Mat kernel2 = Mat::ones(4, 4, CV_8UC1);
    morphologyEx(mask, mask, MORPH_CLOSE, kernel1);
    morphologyEx(mask, mask, MORPH_OPEN, kernel2);
    //use python-like sort here
    int y_min;
    int x_min1;
    int x_min2;
    int w = mask.size().width;
    int h = mask.size().height;
    Mat ftr = Mat::ones(w, h, CV_8UC1);
    for(int i = y_min; i < h; i++){
        for(int j = 0; j < w; j++){
            ftr[i][j] = 0;
        }
    }
    for(int i = 0; i < y_min; i++){
        for(int j = 0; j < x_min1; j++){
            ftr[i][j] = 0;
        }
    }
    for(int i = 0; i < y_min; i++){
        for(int j = x_min2; j < w; j++){
            ftr[i][j] = 0;
        }
    }
    Mat ret;
    bitwise_and(mask, mask, ret, ftr);
    return ret;
}

int* sort_points(int *points){}

int* find_contour_bound(int* cont, bool raw_cont){}

bool filterRects(int* rect, bool pure_cont){}

static Mat pre_process(Mat img){
    Mat ret_img;
    GaussianBlur(img, ret_img, Size(3, 3), 0);
    threshold(ret_img, ret_img, 0, 255, THRESH_BINARY + THRESH_OTSU);
    Mat kernel = Mat::ones(4, 8, CV_8UC1);
    morphologyEx(ret_img, ret_img, MORPH_CLOSE, kernel);
    return ret_img;
}

static void find_and_filter_contour(Mat thresh, OutputArrayOfArrays desired_ref){
    vector<vector<Point> > contours;
    vector<vector<Point> > ret[0];
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
        if(filterRects(contours[i]) & area >= img_width_range_lower * img_height_range_lower & area <= img_width_range_higher * img_height_range_higher){
            ret.resize(ret.size() + 1);
            ret[ret.size() - 1] = cnt;
        }
    }
    desired_ref = ret;
}

static void four_poly_approx(vector<vector<Point> > contours, vector<vector<Point> >* desired_ref){
    vector<vector<Point> > tmp[contours.size()];
    vector<vector<Point> > ret[0];
    for(size_t i = 0; i < contours.size(); i++){
        approxPolyDP(contours[i], tmp[i], 0.05 * arcLength(contours[i], true), true);
        if((sizeof(tmp[i]) == 4) & (isContourConvex(tmp[i]))){
            ret.resize(ret.size() + 1);
            ret[ret.size() - 1] = tmp[i];
        }
    }
    desired_ref = *ret;
}

Mat* pad_white_digit(int* contours, Mat* gray){}

Mat red_color_binarization(Mat org_img){
    Mat mask1, mask2, ret, hsv;
    cvtColor(org_img, hsv, COLOR_BGR2HSV);
    inRange(hsv, Scalar(0, 4, 210), Scalar(25, 255, 255), mask1);
    inRange(hsv, Scalar(155, 4, 210), Scalar(179, 255, 255), mask2);
    bitwise_or(mask1, mask2, ret);
    return ret;
}

//return bound
vector<vector<Point> > bound_red_number(Mat mask){
    vector<vector<Point> > contours;
    vector<vector<Point> > ret[0];
    vector<Vec4i> hierarchy;
    findContours(mask, contours, hierarchy, RETR_TREE, CHAIN_APPROX_SIMPLE);
    for(size_t i = 0; i < contours.size(); i++){
        Rect rec = boundingRect(contours[i]);
        //Rest of the filter process
    }
}

int main(void){
    VideoCapture cap;
    while(true){
        UMat frame;
        Mat img, img_cp, thresh, gray, org_mask, mask;
        cap.read(frame);
        resize(frame, img, Size(640, 360));
        img.copyTo(img_cp);
        cvtColor(img, gray, COLOR_BGR2GRAY);
        thresh = pre_process(gray);
        vector<vector<Point> > contours = find_and_filter_contour(thresh);
        vector<vector<Point> > contours = four_poly_approx(contours);
        if(contours.size() == 0){
            continue;
        }
        if(_DEBUG){
            stringstream output_stream;
            output_stream << "This is the len of contours" << contours.size() << "\n" << "This is the len of tmp" << tmp.size();
        }
        drawContours(img, contours, -1, Scalar(0, 255, 0), 3);
        int digit_height;
        bbox, digit_height, points = pad_white_digit(contours, gray); //what are the types of these variables; probably should pass their reference instead of returning
        //Feed neural network here
        for(int i = 0; i < sizeof(dig_ids); i++){
            putText(img, string(dig_ids[i]), Scalar(static_cast<int>(points[i][0,0]), static_cast<int>(points[i][0,1]-20)), FONT_HERSHEY_SIMPLEX, 0.9, Scalar(0, 255, 255), 2, LINE_AA);
        }
        if(contours.size() == 9){
            std::cout << "update sequence to benchmark comm here";
        }
        mask = red_color_binarization(img_cp);
        mask.copyTo(org_mask);
        dilate(mask, mask, Size(static_cast<int>(digit_height / 10, 1));
        mask = mask_process(mask, points);
        org_mask = mask_process(org_mask, points);
        vector<vector<Point> > bounding_box = bound_red_number(mask);
        dilate(org_mask, org_mask, Size(2, 1));
        //Putting into recognition module or neural network for recognition
    }
}
