import os

from conans import ConanFile, CMake, tools


class DetoolsTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self):
            return

        bin_path = os.path.join("bin", "test_package")
        old_path = os.path.join(self.source_folder, "old")
        patch_path = os.path.join(self.source_folder, "patch")
        patched_path = os.path.join(self.build_folder, "patched")

        self.run(f"{bin_path} {old_path} {patch_path} {patched_path}",
                 run_environment=True)
