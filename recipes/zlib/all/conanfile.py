from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import get, patch, chdir, load, save, rename, replace_in_file, copy
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.45.0"


class ZlibConan(ConanFile):
    name = "zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://zlib.net"
    license = "Zlib"
    description = ("A Massively Spiffy Yet Delicately Unobtrusive Compression Library "
                   "(Also Free, Not to Mention Unencumbered by Patents)")
    topics = ("zlib", "compression")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "CMakeDeps", "CMakeToolchain"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, pattern=patch["patch_file"], src=".", dst=".")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for it in self.conan_data.get("patches", {}).get(self.version, []):
            patch(self, **it)

        is_apple_clang12 = self.settings.compiler == "apple-clang" and Version(str(self.settings.compiler.version)) >= "12.0"
        if not is_apple_clang12:
            for filename in ['zconf.h', 'zconf.h.cmakein', 'zconf.h.in']:
                replace_in_file(self, filename,
                                        '#ifdef HAVE_UNISTD_H    '
                                        '/* may be set to #if 1 by ./configure */',
                                        '#if defined(HAVE_UNISTD_H) && (1-HAVE_UNISTD_H-1 != 0)')
                replace_in_file(self, filename,
                                        '#ifdef HAVE_STDARG_H    '
                                        '/* may be set to #if 1 by ./configure */',
                                        '#if defined(HAVE_STDARG_H) && (1-HAVE_STDARG_H-1 != 0)')

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["SKIP_INSTALL_ALL"] = False
        toolchain.variables["SKIP_INSTALL_LIBRARIES"] = False
        toolchain.variables["SKIP_INSTALL_HEADERS"] = False
        toolchain.variables["SKIP_INSTALL_FILES"] = True
        toolchain.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._source_subfolder)
        cmake.build()


    def _rename_libraries(self):
        if self.settings.os == "Windows":
            lib_path = os.path.join(self.package_folder, "lib")
            suffix = "d" if self.settings.build_type == "Debug" else ""

            if self.options.shared:
                if (self.is_msvc or self.settings.compiler == "clang") and suffix:
                    current_lib = os.path.join(lib_path, "zlib%s.lib" % suffix)
                    rename(self, current_lib, os.path.join(lib_path, "zlib.lib"))
            else:
                if self.is_msvc or self.settings.compiler == "clang":
                    current_lib = os.path.join(lib_path, "zlibstatic%s.lib" % suffix)
                    rename(self, current_lib, os.path.join(lib_path, "zlib.lib"))
                elif self.settings.compiler == "gcc":
                    if not self.settings.os.subsystem:
                        current_lib = os.path.join(lib_path, "libzlibstatic.a")
                        rename(self, current_lib, os.path.join(lib_path, "libzlib.a"))

    def _extract_license(self):
        with chdir(self, os.path.join(self.source_folder, self._source_subfolder)):
            tmp = load(self, "zlib.h")
            license_contents = tmp[2:tmp.find("*/", 1)]
            save(self, "LICENSE", license_contents)

    def package(self):
        self._extract_license()
        copy(self, "LICENSE", src=self._source_subfolder, dst="licenses")
        CMake(self).install()
        self._rename_libraries()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ZLIB")
        self.cpp_info.set_property("cmake_target_name", "ZLIB::ZLIB")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.libs = ["zlib" if self.settings.os == "Windows" and not self.settings.os.subsystem else "z"]

        self.cpp_info.names["cmake_find_package"] = "ZLIB"
        self.cpp_info.names["cmake_find_package_multi"] = "ZLIB"
