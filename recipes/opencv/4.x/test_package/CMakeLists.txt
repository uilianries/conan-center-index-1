cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

enable_testing()

find_package(OpenCV REQUIRED core CONFIG)
find_package(CUDAToolkit REQUIRED)

set(TESTED_MODULES
    # Main modules
    "calib3d" "core" "cuda" "dnn" "features2d" "flann" "gapi" "highgui" "imgcodecs"
    "imgproc" "ml" "objdetect" "photo" "stitching" "video"
    # Extra modules
    "alphamat" "aruco" "bgsegm" "bioinspired" "ccalib" "datasets" "dnn_superres"
    "face" "freetype" "fuzzy" "hdf" "hfs" "img_hash" "intensity_transform"
    "line_descriptor" "mcc" "optflow" "phase_unwrapping" "plot" "quality" "reg"
    "rgbd" "saliency" "sfm" "shape" "structured_light" "superres"
    "surface_matching" "text" "tracking" "wechat_qrcode" "xfeatures2d"
    "ximgproc" "xobjdetect" "xphoto" "cudaimgproc" "cudaarithm" "cudafilters"
)

foreach(_module ${TESTED_MODULES})
    message(STATUS "Testing module: ${_module}")
    string(TOUPPER ${_module} _module_upper)
    if(OPENCV_WITH_${_module_upper})
        message(STATUS "Module ${_module} is enabled")
        set(_test_target test_${_module})
        set(_module_target opencv_${_module})
        add_executable(${_test_target} ${_test_target}.cpp)
        if(${_module} STREQUAL "cuda")
            # INFO: OpenCV CUDA is embedded in opencv_core only.
            target_link_libraries(${_test_target} PRIVATE opencv_core)
        else()
            target_link_libraries(${_test_target} PRIVATE ${_module_target})
        endif()
        if (MSVC AND NOT OPENCV_BUILD_SHARED_LIBS AND OPENCV_WITH_CUDA)
            # INFO: The cuda-toolkit package does not model its package_info, intead, we consume the official FindCUDAToolkit
            # When building with MSVC and static OpenCV, we need to link against the CUDA libraries manually
            target_link_libraries(${_test_target} PRIVATE CUDA::cuda_driver CUDA::cublas CUDA::cudart CUDA::cufft CUDA::curand CUDA::cusolver CUDA::cusparse CUDA::nppial CUDA::nppicc CUDA::nppist CUDA::nppidei CUDA::nppig CUDA::nppif CUDA::nppim)
        endif()
        if(NOT ${_module} STREQUAL "highgui")
            add_test(NAME ${_test_target} COMMAND ${_test_target})
        endif()
    endif()
endforeach()
