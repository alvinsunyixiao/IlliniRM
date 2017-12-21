#include <caffe/caffe.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/higgui/highgui.hpp>

using namespace cv;

const int[3] lower_red_1 = {0, 4, 210};
const int[3] upper_red_1 = {25, 255, 255};
const int[3] lower_red_2 = {155, 4, 210};
const int[3] upper_red_2 = {179, 255, 255};

int* find_contour_bound(bool = false);
bool filterRects(bool = false);

Mat pad_diggit(Mat *img){
    int w = img.shape[1];
    int h = img.shape[0]
    int length = static_cast<int>(h * 1.4);
    int v_pad = (length - h) / 2;
    int h_pad = (length - w) / 2;
    Mat new_img = copyMakeBorder(img, v_pad, v_pad, h_pad, h_pad, BORDER_CONSTANT, 0);
    return resize(new_img, (28, 28));
}

int* rank(int *dig_ids, int *contours_array){}
Mat* mask_process(Mat *mask, int *points){}
int* sort_points(int *points){}
int* find_contour_bound(int* cont, bool raw_cont){}
bool filterRects(int* rect, bool pure_cont){}
Mat* pre_process(Mat* img){}
int* find_and_filter_contour(Mat* thresh){}
int* four_poly_approx(int* contours){}
Mat* pad_white_digit(int* contours, Mat* gray){}
Mat* red_color_binarization(Mat* org_img){}
Mat* red_number_bound(Mat* mask){}

int main(void){
    cout << "test";
    cout << endl;
}
