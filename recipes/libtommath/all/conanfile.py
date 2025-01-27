from conan import ConanFile
from conan.tools.microsoft import is_msvc, NMakeToolchain, msvc_runtime_flag
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.files import copy, rm, rmdir, get, chdir
from conan.errors import ConanInvalidConfiguration
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
    package_type = "library"


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
    def _optimization_flags(self):
        # libtommath requires optimization on MSVC Debug builds for dead code elimination.
        # Otherwise, the build will fail with error LNK2019: unresolved external symbol s_read_arc4random
        # By default, it uses /Ox: https://github.com/libtom/libtommath/blob/v1.3.0/makefile.msvc#L14
        # https://github.com/libtom/libtommath/blob/42b3fb07e7d504f61a04c7fca12e996d76a25251/s_mp_rand_platform.c#L120-L138
        # https://github.com/libtom/libtommath/issues/485
        return "/Ox" if is_msvc(self) and self.settings.build_type == "Debug" else ""

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def build_requirements(self):
        if not is_msvc(self) and self.settings_build.os == "Windows" and not self.conf.get("tools.gnu:make_program"):
            self.build_requires("make/4.3")

        if self.settings.os != "Windows" and self.options.shared:
            self.build_requires("libtool/2.4.6")

    def validate(self):
        if is_msvc(self) and self.options.shared:
            # INFO: Official release does not support shared library on Windows with MSVC yet
            # However, the develop branch has it supported already:
            # https://github.com/libtom/libtommath/blob/5809141a3a6ec1bf3443c927c02b955e19224016/makefile.msvc#L24
            # TODO: Update msvc+shared support when the next release of libtommath is available
            raise ConanInvalidConfiguration("Does not support shared library on Windows with MSVC for now.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = NMakeToolchain(self)
        tc.generate()
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        if is_msvc(self):
            runtime_flag = "/" + msvc_runtime_flag(self)
            with chdir(self, self.source_folder):
                self.run(f'nmake -f {self._makefile} all CFLAGS="{self._optimization_flags} {runtime_flag}"')
        else:
            make_target = "libtommath.dll" if self.options.shared and self.settings.os == "Windows" else "all"
            debug_flags = "COMPILE_DEBUG=1" if self.settings.build_type == "Debug" else ""
            autotools = Autotools(self)
            autotools.make(target=make_target, args=["-f", self._makefile, debug_flags])

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            with chdir(self, self.source_folder):
                self.run(f"nmake -f {self._makefile} install PREFIX={self.package_folder}")
        elif self.settings.os == "Windows":
            copy(self, "tommath.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
            copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"))
            copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"))
        else:
            autotools = Autotools(self)
            autotools.make(target="install", args=["-f", self._makefile, f"PREFIX={self.package_folder}"])

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if not self.settings.os == "Windows" and self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["tommath"]

        self.cpp_info.set_property("cmake_file_name", "libtommath")
        self.cpp_info.set_property("cmake_target_name", "libtommath")
        self.cpp_info.set_property("pkg_config_name", "libtommath")

        if not self.options.shared and self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32"]
