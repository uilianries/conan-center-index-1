import os
from conan import ConanFile
from conan.tools.build import cross_building


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if not cross_building(self, skip_x64_x86=True):
            self.run("nasm --version")
            asm_file = os.path.join(self.source_folder, "hello_linux.asm")
            out_file = os.path.join(self.build_folder, "hello_linux.o")
            bin_file = os.path.join(self.build_folder, "hello_linux")
            self.run("nasm -felf64 {} -o {}".format(asm_file, out_file))
            if self.settings.os == "Linux" and self.settings.arch == "x86_64":
                ld = os.getenv("LD", "ld")
                self.run("{} hello_linux.o -o {}".format(ld, bin_file))
                self.run(bin_file)
