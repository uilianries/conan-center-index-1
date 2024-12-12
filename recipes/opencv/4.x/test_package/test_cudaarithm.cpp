#include <cstdlib>
#include <iostream>
#include <opencv2/cudaarithm.hpp>
#include <opencv2/core/cuda.hpp>


int main(void) {
    cv::Mat h_mat1(3, 3, CV_32FC1, cv::Scalar(5.0f));
    cv::Mat h_mat2(3, 3, CV_32FC1, cv::Scalar(3.0f));

    cv::cuda::GpuMat d_mat1, d_mat2, d_result;
    d_mat1.upload(h_mat1);
    d_mat2.upload(h_mat2);

    cv::cuda::add(d_mat1, d_mat2, d_result);

    cv::Mat h_result;
    d_result.download(h_result);

    std::cout << "5.0 + 3.0 = " << h_result.at<float>(0,0) << std::endl;

    return EXIT_SUCCESS;
}