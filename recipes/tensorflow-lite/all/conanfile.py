from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.env import VirtualBuildEnv
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, rm, save, apply_conandata_patches, copy
from conan.errors import ConanInvalidConfiguration
from os.path import join
import textwrap


required_conan_version = ">=1.51.3"


class TensorflowLiteConan(ConanFile):
    name = "tensorflow-lite"
    license = "Apache-2.0"
    homepage = "https://www.tensorflow.org/lite/guide"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("TensorFlow Lite is a set of tools that enables on-device machine learning "
                   "by helping developers run their models on mobile, embedded, and IoT devices.")
    topics = ("machine-learning", "neural-networks", "deep-learning")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ruy": [True, False],
        "with_nnapi": [True, False],
        "with_mmap": [True, False],
        "with_xnnpack": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ruy": False,
        "with_nnapi": False,
        "with_mmap": True,
        "with_xnnpack": True
    }

    short_paths = True

    @property
    def _minimum_cpp_standard(self):
        return 17 if Version(self.version) >= "2.9.1" else 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "Visual Studio": "15.8",
            "clang": "5",
            "msvc": "1900",
            "apple-clang": "5.1",
        }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_nnapi
            del self.options.with_mmap
        if self.settings.os == "Macos":
            del self.options.with_nnapi

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("abseil/20220623.0")
        self.requires("eigen/3.4.0")
        self.requires("farmhash/cci.20190513")
        self.requires("fft/cci.20061228")
        self.requires("flatbuffers/2.0.5")
        self.requires("gemmlowp/cci.20210928")
        if self.settings.arch in ("x86", "x86_64"):
            self.requires("intel-neon2sse/cci.20210225")
        self.requires("ruy/cci.20220628")
        if self.options.with_xnnpack:
            self.requires("xnnpack/cci.20220621")
        if self.options.with_xnnpack or self.options.get_safe("with_nnapi", False):
            self.requires("fp16/cci.20210320")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(f"{self.name} requires C++{self._minimum_cpp_standard}. Your compiler is unknown. Assuming it supports C++{self._minimum_cpp_standard}.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.name} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")

    def build_requirements(self):
        self.tool_requires("cmake/3.24.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["TFLITE_ENABLE_RUY"] = self.options.with_ruy
        tc.variables["TFLITE_ENABLE_NNAPI"] = self.options.get_safe("with_nnapi", False)
        tc.variables["TFLITE_ENABLE_GPU"] = False
        tc.variables["TFLITE_ENABLE_XNNPACK"] = self.options.with_xnnpack
        tc.variables["TFLITE_ENABLE_MMAP"] = self.options.get_safe("with_mmap", False)
        tc.variables["FETCHCONTENT_FULLY_DISCONNECTED"] = True
        tc.variables["clog_POPULATED"] = True
        if self.settings.arch == "armv8":
            # INFO: Not defined by Conan for Apple Silicon. See https://github.com/conan-io/conan/pull/8026
            tc.cache_variables["CMAKE_SYSTEM_PROCESSOR"] = "arm64"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=join("tensorflow", "lite"))
        cmake.build()

    @staticmethod
    def _create_cmake_module_alias_target(self, module_file):
        aliased = "tensorflowlite::tensorflowlite"
        alias = "tensorflow::tensorflowlite"
        content = textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file(self):
        return join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package(self):
        copy(self, "LICENSE", self.source_folder, join(self.package_folder, "licenses"))
        copy(self, "*.h", join(self.source_folder, "tensorflow", "lite"), join(self.package_folder, "include", "tensorflow", "lite"))
        copy(self, "*.a", self.build_folder, join(self.package_folder, "lib"))
        copy(self, "*.so*", self.build_folder, join(self.package_folder, "lib"))
        copy(self, "*.dylib*", self.build_folder, join(self.package_folder, "lib"))
        copy(self, "*.lib", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll*", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        self._create_cmake_module_alias_target(self, join(self.package_folder, self._module_file))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tensorflowlite")
        self.cpp_info.set_property("cmake_target_name", "tensorflow::tensorflowlite")

        self.cpp_info.names["cmake_find_package"] = "tensorflowlite"
        self.cpp_info.names["cmake_find_package_multi"] = "tensorflowlite"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file]

        defines = []
        if not self.options.shared:
            defines.append("TFL_STATIC_LIBRARY_BUILD")
        if self.options.with_ruy:
            defines.append("TFLITE_WITH_RUY")

        self.cpp_info.defines = defines
        self.cpp_info.libs = ["tensorflow-lite"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")
