/*
 * Copyright (c) 2017, NVIDIA CORPORATION. All rights reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 */

#include "opencv2/opencv.hpp"

#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <vector>

#include "cudaNormalize.h"
#include "LeNet.h"

int main( int argc, char** argv )
{
	/*
	 * create imageNet
	 */
	LeNet* net = LeNet::create("/home/nvidia/mnist_with_fire/lenet.prototxt",
            "/home/nvidia/mnist_with_fire/mnist_iter_75000.caffemodel");
	
	if( !net )
	{
		printf("imagenet-console: failed to initialize imageNet\n");
		return 0;
	}

	float confidence = 0.0f;
	
    cv::cuda::GpuMat gmat1, gmat2;
    gmat1.upload(cv::imread("/home/nvidia/jetson-inference/data/images/four.jpg"));
    gmat2.upload(cv::imread("/home/nvidia/jetson-inference/data/images/four.jpg"));
    cv::cuda::cvtColor(gmat1, gmat1, cv::COLOR_BGR2GRAY);
    cv::cuda::cvtColor(gmat2, gmat2, cv::COLOR_BGR2GRAY);
    cv::cuda::resize(gmat1, gmat1, cv::Size(28, 28));
    cv::cuda::resize(gmat2, gmat2, cv::Size(28, 28));

    std::vector<cv::cuda::GpuMat> inputs;
    inputs.push_back(gmat1);
    inputs.push_back(gmat2);

    std::vector<uint8_t> rs;
    std::vector<float>  conf;

    net->predict(inputs, &rs, &conf);

    printf("class: %u, confidence: %f\n", rs[0], conf[0]);
    printf("class: %u, confidence: %f\n", rs[1], conf[1]);

	return 0;
}

