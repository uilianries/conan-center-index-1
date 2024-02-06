from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import get, replace_in_file
from conan.tools.scm import Version
import os


required_conan_version = ">=1.60.0"


class UpCpp(ConanFile):
    name = "up-cpp"
    package_type = "shared-library"
    license = "Apache-2.0"
    url = "https://github.com/eclipse-uprotocol/up-cpp"
    description = "This module contains the data model structures as well as core functionality for building uProtocol"
    topics = ("utransport-sdk", "transport")
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15.7",
            "msvc": "191",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("spdlog/1.13.0", transitive_headers=True)
        self.requires("fmt/10.2.1")
        self.requires("protobuf/3.21.12", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def build_requirements(self):
        if not self._is_legacy_one_profile:
            self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if self._is_legacy_one_profile:
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        # INFO: Do not include unit tests. https://github.com/eclipse-uprotocol/up-cpp/pull/46
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "add_subdirectory(test)", "")

    def build(self):
        # TODO: Need to configure up-core-api before building.
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["up-cpp"]
