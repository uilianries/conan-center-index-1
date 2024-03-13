import os
import pip

from conan import ConanFile
from conan.tools.files import copy, get, rmdir, save
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class PythonPackagingConan(ConanFile):
    name = "python-packaging"
    description = " Core utilities for Python packages "
    topics = ("template", "python")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://packaging.pypa.io/"
    license = ("Apache-2.0", "BSD-2-Clause")
    package_type = "unknown"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "src", "packaging"), dst=os.path.join(self.package_folder, "lib", "packaging"))
        save(self, os.path.join(self.package_folder, "lib", "__init__.py"), "")

    def package_info(self):
        self.cpp_info.includedirs = []
        self.buildenv_info.define_path("PYTHONPATH", os.path.join(self.package_folder, "lib"))
