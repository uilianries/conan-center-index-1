import os
from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.layout import basic_layout


class DefaultNameConan(ConanFile):
    settings = "os", "arch"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if not cross_building(self):
            self.run("perl --version")
            perl_script = os.path.join(self.source_folder, "list_files.pl")
            self.run("perl {}".format(perl_script))
