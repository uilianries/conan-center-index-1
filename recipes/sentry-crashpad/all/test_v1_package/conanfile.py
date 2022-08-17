from conans import ConanFile, CMake
from conan.tools.files import mkdir
from conan.tools.build import cross_building
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if cross_building(self):
            test_env_dir = "test_env"
            mkdir(test_env_dir)
            bin_path = os.path.join("test_package", "bin")
            handler_exe = "crashpad_handler.exe" if self.settings.os == "Windows" else "crashpad_handler"
            handler_bin_path = os.path.join(self.deps_cpp_info["sentry-crashpad"].rootpath, handler_exe)
            db_path = os.path.join(test_env_dir, "db")
            self.run(f"{bin_path} {db_path} {handler_bin_path}", run_environment=True)
