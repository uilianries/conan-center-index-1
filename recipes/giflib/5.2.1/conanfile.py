from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

class GiflibConan(ConanFile):
    name = "giflib"
    description = "A library and utilities for reading and writing GIF images."
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "http://giflib.sourceforge.net"
    topics = ("conan", "giflib", "image", "multimedia", "format", "graphics")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt", "patches/*"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("%s-%s" % (self.name, self.version), self._source_subfolder)
        tools.patch(base_path=self._source_subfolder, patch_file="patches/%s.patch" % self.version, strip=1)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)

        self._cmake.configure()
        return self._cmake
    
    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if not self.options.shared:
            self.cpp_info.defines.append("USE_GIF_LIB")

