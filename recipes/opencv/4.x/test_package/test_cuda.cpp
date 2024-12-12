#include <cstdlib>
#include <iostream>
#include <opencv2/core/cuda.hpp>

int main(void) {
    if (cv::cuda::getCudaEnabledDeviceCount()) {
        cv::cuda::setDevice(0);
        cv::cuda::printShortCudaDeviceInfo(cv::cuda::getDevice());
    }

    return EXIT_SUCCESS;
}
