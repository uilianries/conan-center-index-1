import os
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def requirements(self):
        self.requires("protobuf/{}".format(self.requires["protoc"].ref.version))

    def build(self):
        cmake = CMake(self)
        cmake.definitions["protobuf_VERBOSE"] = True
        cmake.definitions["protobuf_MODULE_COMPATIBLE"] = True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("protoc --version", run_environment=True)
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

        assert os.path.isfile(os.path.join(self.build_folder, "addressbook.pb.cc"))
        assert os.path.isfile(os.path.join(self.build_folder, "addressbook.pb.h"))
