#ifndef NUM_RECOG_H
#define NUM_RECOG_H

#include <iostream>
#include <opencv2/opencv.hpp>
#include <array>
#include <vector>

namespace num_recog{
    int digit_recog(cv::Mat unpadded_num);
}

#endif
