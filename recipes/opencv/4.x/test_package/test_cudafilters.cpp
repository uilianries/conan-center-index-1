#include <cstdlib>
#include <iostream>
#include <opencv2/cudafilters.hpp>
#include <opencv2/core/cuda.hpp>

int main(void) {
    // Create small CPU matrix (8x8)
    cv::Mat h_src(8, 8, CV_32FC1, cv::Scalar(1.0f));

    // Upload to GPU
    cv::cuda::GpuMat d_src, d_dst;
    d_src.upload(h_src);

    // Create Gaussian filter
    auto gaussian = cv::cuda::createGaussianFilter(
        CV_32FC1,    // source type
        CV_32FC1,    // dest type
        cv::Size(3, 3), // kernel size
        1.0          // sigma
    );

    // Apply filter
    gaussian->apply(d_src, d_dst);

    // Download result
    cv::Mat h_dst;
    d_dst.download(h_dst);

    // Print center pixel
    std::cout << "Center pixel value: " << h_dst.at<float>(4,4) << std::endl;

    return EXIT_SUCCESS;
}