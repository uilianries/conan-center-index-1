import os

from conans import ConanFile, tools


class IcecreamcppConan(ConanFile):
    name = "icecream-cpp"
    license = "MIT"
    url = "https://github.com/renatoGarcia/icecream-cpp"
    description = "A little library to help with the print debugging on C++11 and forward."
    topics = ("debug", "single-header-lib", "print")
    no_copy_source = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('icecream-cpp-{}'.format(self.version), 'icecream-cpp-src')

    def package(self):
        self.copy('icecream-cpp-src/icecream.hpp', 'include/', keep_path=False)
