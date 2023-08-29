from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version
from conan.tools.env import VirtualBuildEnv
from conan.tools.microsoft import is_msvc
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, rmdir, rename, get, rm, replace_in_file
from conan.tools.build import cross_building, check_min_cppstd
import shutil
import os
import functools

required_conan_version = ">=1.45.0"

class LibXMLPlusPlus(ConanFile):
    # FIXME: naming the library "libxml++" causes conan not to add it to the
    # environment path on windows
    name = "libxmlpp"
    description = "libxml++ (a.k.a. libxmlplusplus) provides a C++ interface to XML files"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libxmlplusplus/libxmlplusplus"
    topics = ["xml", "parser", "wrapper"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "pkg_config"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libxml2/2.9.14")
        if Version(self.version) <= "2.42.1":
            self.requires("glibmm/2.66.4")
        else:
            self.requires("glibmm/2.72.1")

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def build_requirements(self):
        self.build_requires("meson/1.2.1")
        self.build_requires("pkgconf/1.9.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)

        if is_msvc(self):
            # when using cpp_std=c++NM the /permissive- flag is added which
            # attempts enforcing standard conformant c++ code. the problem is
            # that older versions of the Windows SDK isn't standard conformant!
            # see:
            # https://developercommunity.visualstudio.com/t/error-c2760-in-combaseapih-with-windows-sdk-81-and/185399
            replace_in_file(
                os.path.join(self.source_folder, "meson.build"),
                "cpp_std=c++", "cpp_std=vc++")

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        tc = MesonToolchain(self)
        tc.project_options["build-examples"] = "false"
        tc.project_options["build-tests"] = "false"
        tc.project_options["build-documentation"] = "false"
        tc.project_options["msvc14x-parallel-installable"] = "false"
        tc.project_options["default_library"] = "shared" if self.options.shared else "static"
        tc.generate()
        td = PkgConfigDeps(self)
        td.generate()

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        lib_version = "2.6" if Version(self.version) <= "2.42.1" else "5.0"

        copy(self, "COPYING", dst="licenses", src=self.source_folder)
        meson = Meson(self)
        meson.install()

        shutil.move(
            os.path.join(self.package_folder, "lib", f"libxml++-{lib_version}", "include", "libxml++config.h"),
            os.path.join(self.package_folder, "include", f"libxml++-{lib_version}", "libxml++config.h"))

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", f"libxml++-{lib_version}"))

        if is_msvc(self):
            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
            if not self.options.shared:
                rename(
                    self,
                    os.path.join(self.package_folder, "lib", f"libxml++-{lib_version}.a"),
                    os.path.join(self.package_folder, "lib", f"xml++-{lib_version}.lib"))

    def package_info(self):
        lib_version = "2.6" if Version(self.version) <= "2.42.1" else "5.0"

        self.cpp_info.set_property("cmake_module_file_name", "libxml++")
        self.cpp_info.set_property("cmake_module_target_name", "libxml++::libxml++")
        self.cpp_info.set_property("pkg_config_name", "libxml++")
        self.cpp_info.components[f"libxml++-{lib_version}"].set_property("pkg_config_name", f"libxml++-{lib_version}")
        self.cpp_info.components[f"libxml++-{lib_version}"].libs = [f"xml++-{lib_version}"]
        self.cpp_info.components[f"libxml++-{lib_version}"].includedirs = [
            os.path.join("include", f"libxml++-{lib_version}")
        ]
        self.cpp_info.components[f"libxml++-{lib_version}"].requires = [
                "glibmm::glibmm", "libxml2::libxml2"
        ]

        self.cpp_info.names["cmake_find_package"] = "libxml++"
        self.cpp_info.names["cmake_find_package_multi"] = "libxml++"
        self.cpp_info.names["pkg_config"] = "libxml++"
        self.cpp_info.components[f"libxml++-{lib_version}"].names["pkg_config"] = f"libxml++-{lib_version}"
