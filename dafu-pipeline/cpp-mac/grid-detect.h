#ifndef GRID_DETECT_H
#define GRID_DETECT_H

#include <caffe/caffe.hpp>
#include <opencv2/opencv.hpp>
#include <caffe/blob.hpp>
#include <caffe/util/io.hpp>
#include <stdio.h>
#include <stdlib.h>

using namespace cv;
using namespace std;
using namespace caffe;

struct contours_and_dig{
    int dig_id;
    int x;
};

static vector<int> get_cnt_x_vector(vector<Point> cnt);
static vector<int> get_cnt_y_vector(vector<Point> cnt);
static void pad_diggit(Mat &img, Mat &ret_img);
vector<Point> extract_nth_point_from_contours(vector<vector<Point> > points, int pos);
static vector<int> rank(vector<int> dig_ids, vector<vector<Point> > contours_array);
static int index_of_min_element_in_vector(vector<int> a_vector);
static int index_of_max_element_in_vector(vector<int> a_vector);
static void mask_process(Mat mask, vector<vector<Point> > points, Mat &ret_img);
static vector<Point> sort_points(vector<Point> points);
static void find_contour_bound(vector<Point> cont, bool raw_cont, int& left, int& right, int& lower, int& upper);
bool filterRects(vector<Point> rect, bool pure_cont);
static void pre_process(Mat &ret_img);
static void find_and_filter_contour(Mat thresh, queue<vector<Point> >& desired_ref);
static void four_poly_approx(queue<vector<Point> > contours, queue<vector<Point> > &desired_ref);
static void pad_white_digit(vector<vector<Point> > contours, Mat gray, vector<Mat>& bboxs, vector<vector<Point> >& points, int& digit_height);
static void red_color_binarization(Mat org_img, Mat &ret_img);
vector<Rect> bound_red_number(Mat mask);
static int Argmax(const vector<float>& v);
static int Argmax(const std::vector<float>& v, int N);
Mat process(Mat frame, Net<float> &net);

#endif
