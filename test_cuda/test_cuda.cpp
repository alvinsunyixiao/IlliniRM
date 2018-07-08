#include <opencv2/opencv.hpp>
#include <iostream>
//#include "opencv2/cudaarithm.hpp"
//#include "opencv2/cuda.hpp"

using namespace std;

int main(void) {
    int dv_cnt = cv::cuda::getCudaEnabledDeviceCount();
    std::cout << "Available GPU(s): " << dv_cnt << std::endl;
    cv::Mat src_host = cv::imread("file.png", CV_LOAD_IMAGE_GRAYSCALE);
    cv::cuda::GpuMat dst, src;
    src.upload(src_host);

    cv::cuda::threshold(src, dst, 128.0, 255.0, CV_THRESH_BINARY);

    for (int i = 0; i < 20000; ++i) {
	cv::cuda::threshold(dst, dst, 128, 255, CV_THRESH_BINARY);
    }

    cv::Mat result_host;
    dst.download(result_host);

    //for (int i = 0; i < 20000; ++i) cv::threshold(src_host, src_host, 128, 255, CV_THRESH_BINARY);
    return 0;
}
