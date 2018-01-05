#include "num_recog.h"

//bool _DEBUG = false;
int one_threshold = 170;
int on_threshold = 10;

std::array<bool, 7> digit_match[10];
//stupid but quick way to initialize digit_match

namespace num_recog{
    int digit_recog(cv::Mat unpadded_num){
        for(int i = 0; i < 10; i++){
            if(i == 0){
                std::array<bool, 7> temp={true, true, true, true, true, false, true}; // 0
                digit_match[i] = temp;
            }
            if(i == 1){
                std::array<bool, 7> temp={false, false, true, true, false, false, false}; // 1
                digit_match[i] = temp;
            }
            if(i == 2){
                std::array<bool, 7> temp={false, true, true, false, true, true, true}; // 2
                digit_match[i] = temp;
            }
            if(i == 3){
                std::array<bool, 7> temp={false, false, true, true, true, true, true}; // 3
                digit_match[i] = temp;
            }
            if(i == 4){
                std::array<bool, 7> temp={true, false, true, true, false, true, false}; // 4
                digit_match[i] = temp;
            }
            if(i == 5){
                std::array<bool, 7> temp={true, false, false, true, true, true, true}; // 5
                digit_match[i] = temp;
            }
            if(i == 6){
                std::array<bool, 7> temp={true, true, false, true, true, true, true}; // 6
                digit_match[i] = temp;
            }
            if(i == 7){
                std::array<bool, 7> temp={false, false, true, true, true, false, false}; // 7
                digit_match[i] = temp;
            }
            if(i == 8){
                std::array<bool, 7> temp={true, true, true, true, true, true, true}; // 8
                digit_match[i] = temp;
            }
            if(i == 9){
                std::array<bool, 7> temp={true, false, true, true, true, true, true}; // 9
                digit_match[i] = temp;
            }
        }

        cv::Rect segments[7];
        for(int i = 0; i < 7; i++){
            if(i == 0){
                cv::Rect temp(0, 3, 3, 4);
                segments[i] = temp;
            }
            if(i == 1){
                cv::Rect temp(0, 11, 3, 4);
                segments[i] = temp;
            }
            if(i == 2){
                cv::Rect temp(7, 3, 3, 4);
                segments[i] = temp;
            }
            if(i == 3){
                cv::Rect temp(7, 11, 3, 4);
                segments[i] = temp;
            }
            if(i == 4){
                cv::Rect temp(4, 0, 3, 4);
                segments[i] = temp;
            }
            if(i == 5){
                cv::Rect temp(4, 7, 3, 4);
                segments[i] = temp;
            }
            if(i == 6){
                cv::Rect temp(4, 14, 3, 4);
                segments[i] = temp;
            }
        }
        std::array<bool, 7> on;
        double img_avg;
        img_avg = sum(cv::mean(unpadded_num))[0];
        if(img_avg >= one_threshold) return 1; //too much red pixel
        if(unpadded_num.size().width < 6) return 1; //too slim
        cv::Mat proc_img;
        cv::threshold(unpadded_num, proc_img, 240, 255, cv::THRESH_BINARY);
        //int tube_width = 2;
        //int tube_height = tube_width;
        //int on_threshold = 5;
        cv::resize(proc_img, proc_img, cv::Size(10, 18), 0, 0, cv::INTER_NEAREST);
        cv::imwrite("debug.jpg", proc_img);
        //bool on_test[7];
        std::array<bool, 7> on_test={false, false, false, false, false, false, false};
        for(int i = 0; i < 7; i++){
            int cur_seg_pixel = cv::countNonZero(proc_img(segments[i]));
            if(cur_seg_pixel >= on_threshold){
                on_test[i] = true;
            } else {
                on_test[i] = false;
            }
        }
        for(int i = 0; i < 10; i++){
            if(on_test == digit_match[i]){
                return i;
            }
        }
        return -1; //not found
    }
}
