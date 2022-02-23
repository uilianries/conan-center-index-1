import os
from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain, CMakeDeps
from conan.tools.files import get, patch, copy


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
        if self.settings.compiler == "Visual Studio":
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
            else:
                # ARM-specific instructions can be enabled here
                extra_env = {}
            toolchain.generate(env)
            deps = AutotoolsDeps(self)
            deps.generate()

    def layout(self):
        if self.settings.compiler == "Visual Studio":
            cmake_layout(self)
        else:
            self.folders.build = str(self.settings.build_type)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        for p in self.conan_data["patches"][self.version]:
            patch(self, **p)

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            cmake = CMake(self)
            cmake.configure()
            cmake.build(target="base64")
        else:
            Autotools(self).make(target="lib/libbase64.a")

    def package(self):
        copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        copy(self, "*.a", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.lib", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["base64"]
