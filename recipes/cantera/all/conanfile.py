import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, save, chdir, load, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.apple import is_apple_os
from conan.tools.microsoft import msvs_toolset
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.54.0"


class canteraRecipe(ConanFile):
    name = "cantera"
    description = "Cantera is an open-source collection of object-oriented software tools for problems involving chemical kinetics, thermodynamics, and transport processes."
    license = "LicenseRef-Cantera"
    homepage = "https://www.cantera.org/"
    topics = ("chemical-kinetics", "combustion", "thermodynamics", "reacting-flows", "catalysis", "electrochemistry")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "9",
            "clang": "9",
            "apple-clang": "12",
        }

    @property
    def _cc(self):
        if "CC" in os.environ:
            return os.environ["CC"]
        if is_apple_os(self):
            return "clang"
        if is_msvc(self):
            return "cl"
        return str(self.settings.compiler)

    def _lib_path_arg(self, path):
        argname = "LIBPATH:" if is_msvc(self) else "L"
        return "-{}'{}'".format(argname, unix_path(self, path))

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("scons/4.3.0")

    def requirements(self):
        self.requires("boost/1.83.0", headers=True)
        self.requires("fmt/10.1.1")
        self.requires("yaml-cpp/0.7.0")
        self.requires("eigen/3.4.0")
        self.requires("sundials/5.4.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        autotools = AutotoolsToolchain(self)
        args = ["-Y", self.source_folder]
        libdirs = sum([dep.cpp_info.libdirs for dep in self.dependencies.values()], [])
        sharedlinkflags = sum([dep.cpp_info.sharedlinkflags for dep in self.dependencies.values()], [])
        includedirs = sum([dep.cpp_info.includedirs for dep in self.dependencies.values()], [])
        cflags = sum([dep.cpp_info.cflags for dep in self.dependencies.values()], [])
        cflags += autotools.cflags
        libs = sum([dep.cpp_info.libs for dep in self.dependencies.values()], [])
        if self.options.get_safe("fPIC"):
            cflags.append("-fPIC")
        kwargs = {
            "debug": self.settings.build_type == "Debug",
            "sundials_include": unix_path(self, self.dependencies["sundials"].cpp_info.includedirs[0]),
            "sundials_libdir": unix_path(self, self.dependencies["sundials"].cpp_info.libdirs[0]),
            "boost_inc_dir": unix_path(self, self.dependencies["boost"].cpp_info.includedirs[0]),
            "extra_inc_dirs": ",".join(includedirs),
            "extra_lib_dirs": ",".join(libdirs),
            "prefix": unix_path(self, self.package_folder),
            "cc_flags": " ".join(cflags),
            "cxx_flags": " ".join([f"-D{d}" for d in autotools.defines] + [f"-I'{unix_path(self, inc)}'" for inc in includedirs]),
            "CC": self._cc,''
            "system_yamlcpp": 'y',
            "system_eigen": 'y',
            "system_fmt": 'y',
            "system_sundials": 'y',
            "libdirname": "lib",
            "python_package": "none",
            "f90_interface": "n",
            "googletest": "none",
        }

        if is_msvc(self):
            kwargs["TARGET_ARCH"] = str(self.settings.arch)
            kwargs["MSVC_VERSION"] = "{:.1f}".format(float(msvs_toolset(self).lstrip("v")) / 10)
            kwargs["ZLIB_LIBNAME"] = f"{self.dependencies['zlib'].cpp_info.libs[0]}"
            env = Environment()
            env.define("OPENSSL_LIBS", os.pathsep.join(f"{lib}.lib" for lib in self.dependencies["openssl"].cpp_info.aggregated_components().libs))
            env.vars(self).save_script("conanbuild_msvc")

        escape_str = lambda x: f'"{x}"'
        scons_args = " ".join([escape_str(s) for s in args] + [f"{k}={escape_str(v)}" for k, v in kwargs.items()])
        save(self, os.path.join(self.source_folder, "scons_args"), scons_args)

    def _patch_sources(self):
        # INFO: Use fmt from conan
        replace_in_file(self, os.path.join(self.source_folder, "SConstruct"), "if env['system_fmt'] in ('y', 'default')", "if False")
        fmt_version = self.dependencies['fmt'].ref.version
        replace_in_file(self, os.path.join(self.source_folder, "SConstruct"), "retcode, fmt_lib_version = conf.TryRun(fmt_version_source, '.cpp')", f'retcode, fmt_lib_version = (True, "{fmt_version}")')
        replace_in_file(self, os.path.join(self.source_folder, "SConstruct"), 'Using fmt version {fmt_lib_version}', f'Using fmt version {fmt_version}')

    def build(self):
        self._patch_sources()
        if self.settings.os == "Windows":
            opt = "toolchain=msvc "
            cd_modifier = "/d"
        else:
            opt = ""
            cd_modifier = ""

        opt = opt +\
              "prefix={} ".format(self.package_folder) +\
              "libdirname=lib " \
              "python_package=none " \
              "f90_interface=n " \
              "googletest=none " \
              "versioned_shared_library=yes " \
              #"extra_inc_dirs={} ".format(os.pathsep.join(self.scons_extra_inc_dirs)) +\
#              "extra_lib_dirs={} ".format(os.pathsep.join(self.scons_extra_lib_dirs)) +\
              #"boost_inc_dir={} ".format(self.scons_boost_inc_dir) +\
              #"sundials_include={} ".format(self.scons_sundials_include) +\
              #"sundials_libdir={} ".format(self.scons_sundials_libdir)

        if self.settings.build_type == "Debug":
            opt = opt + "optimize=no "
        else:
            opt = opt + "debug=no "
        with chdir(self, self.source_folder):
            self.run("scons build {}".format(load(self, "scons_args")))

    def package(self):
        if self.settings.os == "Windows":
            cd_modifier = "/d"
        else:
            cd_modifier = ""


        self.run("cd {} {} && scons install".format(cd_modifier, self.source_folder))


    def package_info(self):
        self.cpp_info.libs = ["cantera_shared"] if self.options.shared else ["cantera"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.resdirs = ["data"]

        if self.options.shared:
            self.cpp_info.libdirs = ["bin"] if self.settings.os == "Windows" else ["share"]
        else:
            self.cpp_info.libdirs = ["lib"]
