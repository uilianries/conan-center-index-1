cmake_minimum_required(VERSION 3.1)

project(GifLib)

set(sources
    "source_subfolder/dgif_lib.c"
    "source_subfolder/egif_lib.c"
    "source_subfolder/gifalloc.c"
    "source_subfolder/gif_err.c"
    "source_subfolder/gif_font.c"
    "source_subfolder/gif_hash.c"
    "source_subfolder/openbsd-reallocarray.c"
)

add_library(gif ${sources})
target_include_directories(gif PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder")

if(BUILD_SHARED_LIBS)
    target_compile_definitions(gif PUBLIC -DBUILD_GIF_DLL)
else()
    target_compile_definitions(gif PUBLIC -DUSE_GIF_LIB)
endif()

if(MSVC)
    target_link_libraries(gif PUBLIC -NODEFAULTLIB)
endif()

install(TARGETS gif ARCHIVE DESTINATION "lib" LIBRARY DESTINATION "lib" RUNTIME DESTINATION "bin")
install(FILES "source_subfolder/gif_lib.h" DESTINATION "include")
