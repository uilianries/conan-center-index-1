from conan import ConanFile
from conan.tools import files, build
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class JfalcouEveConan(ConanFile):
    name = "jfalcou-eve"
    description = ("Expressive Velocity Engine - reimplementation of the old "
                   "Boost.SIMD on C++20"
                   )
    homepage = "https://jfalcou.github.io/eve/"
    topics = ("c++", "simd")
    license = ("BSL-1.0")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {"gcc": "11",
                "Visual Studio": "16.9",
                "clang": "13",
                "apple-clang": "13",
                }

    def configure(self):
        ll = self.version.strip("v")
        lv = [int(v) for v in ll.split(".")]
        info = lv[1:2]
        self.license = "BSL-1.0" if (info[0]>=2022 and info[1]>=9) else "MIT"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            build.check_min_cppstd(self, self._min_cppstd)
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("EVE does not support MSVC yet (https://github.com/jfalcou/eve/issues/1022).")
        if self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration("EVE does not support apple Clang due to an incomplete libcpp.")

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} {} requires C++20. Your compiler is unknown. Assuming it supports C++20.".format(self.name, self.version))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("{} {} requires C++20, which your compiler does not support.".format(self.name, self.version))

    def package_id(self):
        self.info.header_only()

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="include/*", src=self._source_subfolder)
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "eve"
        self.cpp_info.names["cmake_find_package_multi"] = "eve"
