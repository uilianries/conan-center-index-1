from conans import ConanFile, CMake, tools
import os


class RocksDB(ConanFile):
    name = "rocksdb"
    homepage = "https://github.com/facebook/rocksdb"
    license = "GPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A library that provides an embeddable, persistent key-value store for fast storage"
    topics = ("conan", "rocksdb", "database",
              "leveldb", "facebook", "key-value")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gflags": [True, False],
        "with_snappy": [True, False],
        "with_lz4": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": False,
        "with_snappy": False,
        "with_lz4": False,
        "with_zlib": False,
        "with_zstd": False,
        "with_gflags": False
    }
    generators = ["cmake", "cmake_find_package", "cmake_paths"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "rocksdb-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["WITH_TESTS"] = False
        cmake.definitions["WITH_GFLAGS"] = self.options.with_gflags
        cmake.definitions["WITH_SNAPPY"] = self.options.with_snappy
        cmake.definitions["WITH_LZ4"] = self.options.with_lz4
        cmake.definitions["WITH_ZLIB"] = self.options.with_zlib
        cmake.definitions["WITH_ZSTD"] = self.options.with_zstd
        # not available yet in CCI
        cmake.definitions["WITH_JEMALLOC"] = False
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def requirements(self):
        if self.options.with_gflags:
            self.requires("gflags/2.2.2")
        if self.options.with_snappy:
            self.requires("snappy/1.1.7")
        if self.options.with_lz4:
            self.requires("lz4/1.9.2")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_zstd:
            self.requires("zstd/1.3.8")

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.name = "RocksDB"
        self.cpp_info.libs = tools.collect_libs(self)
