from conan import ConanFile
from conan.tools.build import build_jobs, can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import chdir
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    @property
    def _tested_modules(self):
        return [
            # Main modules
            "calib3d", "core", "cuda", "dnn", "features2d", "flann", "gapi", "highgui", "imgcodecs",
            "imgproc", "ml", "objdetect", "photo", "stitching", "video"
            # Extra modules
            "alphamat", "aruco", "bgsegm", "bioinspired", "ccalib", "datasets", "dnn_superres",
            "face", "freetype", "fuzzy", "hdf", "hfs", "img_hash", "intensity_transform",
            "line_descriptor", "mcc", "optflow", "phase_unwrapping", "plot", "quality", "reg",
            "rgbd", "saliency", "sfm", "shape", "structured_light", "superres",
            "surface_matching", "text", "tracking", "wechat_qrcode", "xfeatures2d",
            "ximgproc", "xobjdetect", "xphoto", "cudaimgproc", "cudaarithm", "cudafilters",
        ]

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        self.output.info(f"OPTIONS: {self.dependencies["opencv"].options}")

        tc = CMakeToolchain(self)
        for module in self._tested_modules:
            cmake_option = f"OPENCV_WITH_{module.upper()}"
            if module == "core":
                tc.variables[cmake_option] = True
            elif module == "imgcodecs":
                tc.variables[cmake_option] = self.dependencies["opencv"].options.imgcodecs and self.dependencies["opencv"].options.with_png
            elif module == "videoio":
                tc.variables[cmake_option] = self.dependencies["opencv"].options.videoio and self.dependencies["opencv"].options.with_ffmpeg
            elif module == "cuda":
                tc.variables[cmake_option] = self.dependencies["opencv"].options.with_cuda
            else:
                tc.variables[cmake_option] = self.dependencies["opencv"].options.get_safe(module, False)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            with chdir(self, self.build_folder):
                self.run(f"ctest --output-on-failure -C {self.settings.build_type}", env="conanrun")
