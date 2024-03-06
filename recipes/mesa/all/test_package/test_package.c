#include <stdlib.h>

#ifdef MESA_TEST_PACKAGE_HAS_EGL
#include <EGL/egl.h>
#include <EGL/eglmesaext.h>
#endif

int main(void) {
#if MESA_TEST_PACKAGE_HAS_EGL
    if (EGL_DRM_BUFFER_FORMAT_ARGB2101010_MESA <= 0) {
        return EXIT_FAILURE;
    }
#endif
    return EXIT_SUCCESS;
}
