from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.errors import ConanInvalidConfiguration
from conan import Version
import os


required_conan_version = ">=1.53.0"


class FastGLTFConan(ConanFile):
    name = "fastgltf"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/spnda/fastgltf"
    description = "A blazing fast C++17 glTF 2.0 library powered by SIMD."
    topics = ("gltf", "simd", "cpp17")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_small_vector": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_small_vector": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder='src')

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def requirements(self):
        self.requires("simdjson/3.1.7")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FASTGLTF_DOWNLOAD_SIMDJSON"] = False
        tc.variables["FASTGLTF_USE_SMALL_VECTOR"] = self.options.enable_small_vector
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["fastgltf"]
