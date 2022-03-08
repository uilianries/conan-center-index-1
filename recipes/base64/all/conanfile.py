import os
from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain, CMakeDeps
from conan.tools.files import get, patch, copy, chdir, apply_conandata_patches
from conan.tools.microsoft import is_msvc


class Base64Conan(ConanFile):
    name = "base64"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aklomp/base64"
    description = "Fast Base64 stream encoder/decoder"
    topics = ("base64", "codec")
    exports_sources = "patches/**", "CMakeLists.txt"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False]
    }
    default_options = {
        "fPIC": True
    }

    def generate(self):
        if is_msvc(self):
            toolchain = CMakeToolchain(self)
            toolchain.generate()
            deps = CMakeDeps(self)
            deps.generate()
        else:
            toolchain = AutotoolsToolchain(self)
            env = toolchain.environment()
            if self.settings.arch == "x86" or self.settings.arch == "x86_64":
                env.define("AVX2_CFLAGS", "-mavx2")
                env.define("SSSE3_CFLAGS", "-mssse3")
                env.define("SSE41_CFLAGS", "-msse4.1")
                env.define("SSE42_CFLAGS", "-msse4.2")
                env.define("AVX_CFLAGS", "-mavx")
            toolchain.generate(env)
            deps = AutotoolsDeps(self)
            deps.generate()

    def layout(self):
        if is_msvc(self):
            cmake_layout(self)
        else:
            self.folders.build = os.path.join("build", str(self.settings.build_type))
            self.folders.generators = os.path.join(self.folders.build, "conan")
        self.folders.source = "src"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def build(self):
        if is_msvc(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build(target="base64")
        else:
            # for local flow: there is no configure so the "Makefile" is not generated in build is still at source
            with chdir(self, self.source_folder):
                Autotools(self).make(target="lib/libbase64.a")

    def package(self):
        copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        # As the Makefile lives in source, the artifacts are built there.
        origin_lib_folder = self.build_folder if is_msvc(self) else self.source_folder
        copy(self, "*.a", origin_lib_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.lib", origin_lib_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["base64"]
