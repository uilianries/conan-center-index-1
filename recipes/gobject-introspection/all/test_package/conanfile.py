import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        glib_shared = self.dependencies["glib"].options.shared
        tc.variables["GLIB_INTROSPECTION_DATA_AVAILABLE"] = glib_shared
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_basic")
            self.run(bin_path, env="conanrun")

            bin_path = os.path.join(self.cpp.build.bindir, "test_girepository")
            if os.path.exists(bin_path):
                self.run(bin_path, env="conanrun")
