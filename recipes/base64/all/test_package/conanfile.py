import os
from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.build import cross_building


class CppcodecTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self.settings):
            bin_path = os.path.join("bin", "example")
            self.run(bin_path)
