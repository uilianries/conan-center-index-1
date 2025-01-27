from conan import ConanFile

from conan.tools.microsoft import is_msvc, NMakeToolchain
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.files import copy, rm, rmdir, get
import os

required_conan_version = ">=2.0.9"


class LibTomMathConan(ConanFile):
    name = "libtommath"
    description = "LibTomMath is a free open source portable number theoretic multiple-precision integer library written entirely in C."
    topics = "libtommath", "math", "multiple", "precision"
    license = "Unlicense"
    homepage = "https://www.libtom.net/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "patches/*"


    @property
    def _makefile(self):
        if is_msvc(self):
            return "makefile.msvc"
        if self.settings.os == "Windows":
            return "makefile.mingw"
        if self.options.shared:
            return "makefile.shared"
        return "makefile.unix"

    @property
    def _debug_args(self):
        return "COMPILE_DEBUG=1" if self.settings.build_type == "Debug" else ""

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if not is_msvc(self) and self.settings_build.os == "Windows" and not self.conf.get("tools.gnu:make_program"):
            self.build_requires("make/4.3")

        if self.settings.os != "Windows" and self.options.shared:
            self.build_requires("libtool/2.4.6")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = NMakeToolchain(self)
        tc.generate()
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        if is_msvc(self):
            # TODO: implement MSVC build
            pass
        else:
            autotools = Autotools(self)
            autotools.make(target=None, args=["-f", self._makefile, self._debug_args])

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            copy(self, "*.a", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.lib", src=self._source_subfolder, dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.dll", src=self._source_subfolder, dst=os.path.join(self.package_folder, "bin"))
            copy(self, "tommath.h", src=self._source_subfolder, dst=os.path.join(self.package_folder, "include"))
        else:
            autotools = Autotools(self)
            autotools.make(target="install", args=["-f", self._makefile, self._debug_args, f"PREFIX={self.package_folder}"])

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["tommath"]

        self.cpp_info.set_property("cmake_file_name", "libtommath")
        self.cpp_info.set_property("cmake_target_name", "libtommath")
        self.cpp_info.set_property("pkg_config_name", "libtommath")

        if not self.options.shared and self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32"]
