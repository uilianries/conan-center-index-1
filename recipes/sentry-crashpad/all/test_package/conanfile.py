from conan import ConanFile
from conan.tools.files import mkdir
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            test_env_dir = "test_env"
            mkdir(test_env_dir)
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            handler_exe = "crashpad_handler.exe" if self.settings.os == "Windows" else "crashpad_handler"
            handler_bin_path = os.path.join(self.dependencies["sentry-crashpad"].bindirs[0], handler_exe)
            db_path = os.path.join(test_env_dir, "db")
            self.run(f"{bin_path} {db_path} {handler_bin_path}", env="conanrun")
