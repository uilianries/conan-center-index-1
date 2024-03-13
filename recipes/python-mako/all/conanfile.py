import os
import pip

from conan import ConanFile
from conan.tools.files import copy, get, rmdir, save
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class PythonMakoConan(ConanFile):
    name = "python-mako"
    description = "Mako is a template library written in Python"
    topics = ("template", "python")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.makotemplates.org/"
    license = "MIT"
    package_type = "unknown"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        pip.main(['install', '--no-deps', '--ignore-installed', '--target', self.package_folder, self.source_folder])
        save(self, os.path.join(self.package_folder, "__init__.py"), "")
        rmdir(self, os.path.join(self.package_folder, f"Mako-{self.version}.dev0.dist-info"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.buildenv_info.define_path("PYTHONPATH", self.package_folder)
