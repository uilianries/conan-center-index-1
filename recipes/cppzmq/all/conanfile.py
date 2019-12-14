import os
from conans import ConanFile, CMake, tools


class CppZmqConan(ConanFile):
    name = "cppzmq"
    description = "C++ binding for 0MQ"
    homepage = "https://github.com/zeromq/cppzmq"
    license = "MIT"
    topics = ("conan", "cppzmq", "zmq-cpp", "zmq", "cpp-bind")
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "cppzmq_extra.cmake"]
    generators = "cmake", "cmake_find_package"
    requires = "zeromq/4.3.2"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("cppzmq-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CPPZMQ_BUILD_TESTS"] = False
        cmake.configure()
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))
        self.copy("cppzmq_extra.cmake", dst=os.path.join(self.package_folder, "lib", "cmake", "cppzmq"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.builddir = [os.path.join(self.package_folder, "lib", "cmake", "cppzmq")]
        self.cpp_info.build_modules = [os.path.join(self.package_folder, "lib", "cmake", "cppzmq", "cppzmq_extra.cmake")]
