#include <cstdlib>
#include <iostream>
#include <opencv2/cudaimgproc.hpp>
#include <opencv2/core/cuda.hpp>

int main() {

    if (cv::cuda::getCudaEnabledDeviceCount()) {
        cv::cuda::setDevice(0);
        cv::Mat h_source(480, 640, CV_8UC3, cv::Scalar(200, 100, 50));

        cv::cuda::GpuMat d_source;
        d_source.upload(h_source);

        cv::cuda::GpuMat d_result;
        cv::cuda::cvtColor(d_source, d_result, cv::COLOR_BGR2GRAY);

        cv::Mat h_result;
        d_result.download(h_result);

        std::cout << "Original size: " << h_source.size() << ", channels: " << h_source.channels() << "\n";
        std::cout << "Result size: " << h_result.size() << ", channels: " << h_result.channels() << "\n";

        cv::Vec3b sourcePixel = h_source.at<cv::Vec3b>(0,0);
        uchar resultPixel = h_result.at<uchar>(0,0);
        std::cout << "First source pixel (BGR): " << (int)sourcePixel[0] << ", "
                    << (int)sourcePixel[1] << ", " << (int)sourcePixel[2] << "\n";
        std::cout << "First result pixel (Gray): " << (int)resultPixel << "\n";
    }

    return EXIT_SUCCESS;
}