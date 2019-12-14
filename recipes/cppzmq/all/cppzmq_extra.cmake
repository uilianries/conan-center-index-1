# This script should only run when included in a FindXXX.cmake module
if(NOT cppzmq_LIB_DIRS)
    return()
endif()

if(NOT TARGET cppzmq)
    add_library(cppzmq INTERFACE IMPORTED)
    set_property(TARGET cppzmq PROPERTY INTERFACE_LINK_LIBRARIES cppzmq::cppzmq)
endif()
