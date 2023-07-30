from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.build import can_run
from conan.tools.apple import is_apple_os
import os
from io import StringIO
import re

required_conan_version = ">=1.60.0"

class RsyncConan(ConanFile):
    name = "rsync"
    description = "Rsync utility"
    topics = ("rsync")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://rsync.samba.org/"
    license = "LGPL-3.0"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "with_zlib": [True, False],
        "with_openssl": [True, False],
        "with_zstd": [True, False],
        "with_xxhash": [True, False],
        "with_lz4": [True, False],
        "acl": [True, False]
    }
    default_options = {
        "with_zlib": True,
        "with_openssl": True,
        "with_zstd": True,
        "with_xxhash": True,
        "with_lz4": True,
        "acl": False
    }
    
    @property
    def _configure_args(self):
        args = [
            "--enable-acl-support={}".format("yes" if self.options.acl else "no"),
            "--with-included-zlib={}".format("no" if self.options.with_zlib else "yes")
        ]
        if not self.options.with_openssl:
            args.append("--disable-openssl")

        if not self.options.with_zstd:
            args.append("--disable-zstd")

        if not self.options.with_lz4:
            args.append("--disable-lz4")

        if not self.options.with_xxhash:
            args.append("--disable-xxhash")

        return args
    
    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"Windows is not supported.")        

        if is_apple_os(self):
            raise ConanInvalidConfiguration(f"Apple operating systems is not supported.")        

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.12]")

        if self.options.with_zstd:
            self.requires("zstd/[>=1.5.2]")

        if self.options.with_lz4:
            self.requires("lz4/1.9.2")

        if self.options.with_xxhash:
            self.requires("xxhash/0.8.1")

    def generate(self):
        ad = AutotoolsDeps(self)
        ad.generate()

        tc = AutotoolsToolchain(self)

        if self.settings.os == "Neutrino":
            tc.extra_defines.append("MAKEDEV_TAKES_3_ARGS")

        tc.generate()

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)  
        autotools.configure(args=self._configure_args)
        autotools.make()

        if can_run(self):
            output = StringIO()
            self.output.info(f"Build folder {self.build_folder}")
            self.run(f"{self.build_folder}/rsync --version", output, env="conanrun")
            output_str = str.strip(output.getvalue())

            s = re.search(f"{self.version}", output_str)
            if s == None:
                raise ConanException(f"rsync command output '{output_str}' should contain version string '{self.version}'")
            else:
                self.output.info(f"Version verified: '{self.version}'")        

    def package(self):
        autotools = Autotools(self)  
        autotools.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"), ignore_case=True)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bindir = os.path.join(self.package_folder, "bin")
        self.runenv_info.prepend_path("PATH", bindir)
