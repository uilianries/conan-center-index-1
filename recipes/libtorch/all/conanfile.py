from conans import ConanFile, tools

class Libtorch(ConanFile):
    name = "libtorch"
    version = "1.2.0"
    license = "BSD"
    homepage = "https://pytorch.org"
    description = "Tensors and Dynamic neural networks in Python with strong GPU acceleration"
    settings = {"os": ["Windows","Linux"],
        "build_type": ["Debug", "Release", "RelWithDebInfo"],
        "compiler": {"gcc": {"version": None,
                            "libcxx": ["libstdc++", "libstdc++11"]},
                    "Visual Studio": {"version": None},
                    }
        }
    options = {"cuda": ["9.2","10.0", "None"]}
    default_options = {"cuda": "None"}

    def source(self):
        libstd = str(self.settings.compiler.libcxx) if self.settings.os == "Linux" else None
        build_type = str(self.settings.build_type) if self.settings.os == "Windows" else None
        name = "{}-{}-{}-{}-{}".format(self.version, self.settings.os, build_type, self.options.cuda, libstd)
        tools.get(**self.conan_data["sources"][name])

    def package(self):
        self.copy("*", src="libtorch/include", dst="include")
        self.copy("*", src="libtorch/lib", dst="lib")

    def package_info(self):
        self.cpp_info.libs = ['torch', 'caffe2', 'c10']
        if self.settings.os == "Linux":
            self.cpp_info.libs.append('pthread')
        self.cpp_info.includedirs = ['include', 'include/torch/csrc/api/include']
        self.cpp_info.bindirs = ['bin']
        self.cpp_info.libdirs = ['lib']
        if self.options.cuda != 'None':
            self.cpp_info.libs.extend(
                ['cuda', 'nvrtc', 'nvToolsExt', 'cudart', 'caffe2_gpu',
                 'c10_cuda', 'cufft', 'curand', 'cudnn', 'culibos', 'cublas'])

