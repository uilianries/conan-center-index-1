import os
from conans import ConanFile, tools


class CppZmqConan(ConanFile):
    name = "cppzmq"
    description = "C++ binding for 0MQ"
    homepage = "https://github.com/zeromq/cppzmq"
    license = "MIT"
    topics = ("conan", "cppzmq", "zmq-cpp", "zmq", "cpp-bind")
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["cppzmq_extra.cmake"]
    requires = "zeromq/4.3.2"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("cppzmq-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include", src=self._source_subfolder)
        self.copy("cppzmq_extra.cmake", dst=os.path.join("lib", "cmake", "cppzmq"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.builddir = [os.path.join("lib", "cmake", "cppzmq")]
        self.cpp_info.build_modules = [os.path.join("lib", "cmake", "cppzmq", "cppzmq_extra.cmake")]
