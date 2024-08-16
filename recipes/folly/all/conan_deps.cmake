cmake_minimum_required(VERSION 3.17)
# Set the dependency flags expected by https://github.com/facebook/folly/blob/v2023.12.18.00/CMake/folly-deps.cmake

macro(custom_find_package package_name variable_prefix)
    find_package(${package_name} REQUIRED CONFIG ${ARGN}
        # Allow only Conan packages
        NO_DEFAULT_PATH
        PATHS ${CMAKE_PREFIX_PATH}
    )
    list(APPEND FROM FOUND VERSION VERSION_STRING INCLUDE_DIRS INCLUDE_DIR INCLUDE_DIR LIBRARIES LIBRARIES LIBRARIES DEFINITIONS)
    list(APPEND TO   FOUND VERSION VERSION_STRING INCLUDE_DIRS INCLUDE_DIR INCLUDE     LIB       LIBRARY   LIBRARIES DEFINITIONS)

    foreach (from_substr to_substr IN ZIP_LISTS FROM TO)
        set(src_var ${package_name}_${from_substr})
        set(dst_var ${variable_prefix}_${to_substr})
        if (NOT DEFINED ${src_var})
            continue()
        endif()
        if ((DEFINED ${dst_var}) AND ("${${dst_var}}" STREQUAL "${${src_var}}"))
            # if they're equal, skip
            continue()
        endif()
        message(DEBUG "custom_find_package definining ${dst_var} with ${src_var} contents: ${${src_var}}")
        set(${dst_var} ${${src_var}})
    endforeach()
endmacro()

custom_find_package(BZip2 BZIP2)
custom_find_package(DoubleConversion DOUBLE_CONVERSION REQUIRED)
custom_find_package(Gflags LIBGFLAGS)
custom_find_package(Glog GLOG)
custom_find_package(LZ4 LZ4)
custom_find_package(LibAIO LIBAIO)
custom_find_package(LibDwarf LIBDWARF)
custom_find_package(LibEvent LIBEVENT REQUIRED)
custom_find_package(LibLZMA LIBLZMA)
custom_find_package(LibUnwind LIBUNWIND)
custom_find_package(LibUring LIBURING)
custom_find_package(Libiberty LIBIBERTY)
custom_find_package(Libsodium LIBSODIUM)
custom_find_package(OpenSSL OPENSSL REQUIRED)
custom_find_package(Snappy SNAPPY)
custom_find_package(ZLIB ZLIB)
custom_find_package(Zstd ZSTD)
custom_find_package(fmt FMT REQUIRED)
