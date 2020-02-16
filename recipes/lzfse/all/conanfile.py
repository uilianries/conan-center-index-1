import os

from conans import ConanFile, CMake, tools

class LzfseConan(ConanFile):
    name = "lzfse"
    description = "Lempel-Ziv style data compression algorithm using Finite State Entropy coding."
    license = "BSD-3-Clause"
    topics = ("conan", "lzfse", "compression", "decompression")
    homepage = "https://github.com/lzfse/lzfse"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{0}-{0}-{1}".format(self.name, self.version), self._source_subfolder)

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "POSITION_INDEPENDENT_CODE TRUE", "")
        cmake = CMake(self)
        cmake.definitions["LZFSE_BUNDLE_MODE"] = False
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build(target="lzfse")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("lzfse.h", dst="include", src=os.path.join(self._source_subfolder, "src"))
        build_lib_dir = os.path.join(self._build_subfolder, "lib")
        build_bin_dir = os.path.join(self._build_subfolder, "bin")
        self.copy(pattern="*.a", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.so", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=build_bin_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
