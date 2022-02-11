import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class OpenldapConan(ConanFile):
    name = "openldap"
    description = "OpenLDAP C++ library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openldap.org/"
    license = "OpenLDAP"
    topics = "openldap"
    exports_sources = ["patches/*"]
    settings = {
        "os": ["Linux"],
        "compiler": {
            "gcc": {"version": ["8", "8.2", "10", "10.2"]}
        },
        "build_type": ["Debug", "Release"],
        "arch": ["x86_64"]
    }
    generators = "cmake"
    options = {
        "shared": [True, False],
        "cyrus_sasl": [True, False]
    }
    default_options = {
        "shared": False,
        "cyrus_sasl": True
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("openssl/1.1.1k")
        if self.options.cyrus_sasl:
            self.requires("cyrus-sasl/2.1.27")

    def source(self):
        conan_data = self.conan_data["sources"][self.version]
        tools.get(url=conan_data["url"], sha256=conan_data["sha256"])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        conf_args = []
        autotools = AutoToolsBuildEnvironment(self)
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        if self.options.cyrus_sasl:
            conf_args.append("--with-cyrus_sasl")
        else:
            conf_args.append("--without-cyrus_sasl")
        conf_args.extend(
            ["--without-fetch", "--with-tls=openssl", "--enable-auditlog"])

        libpath = ""
        for path in autotools.library_paths:
            libpath += "{}:".format(path)
        
        # Need to link to -pthread instead of -lpthread for gcc 8 shared=True on CI job
        libs = ""
        autotools.libs.remove("pthread") 
        for lib in autotools.libs:
            libs += "-l{} ".format(lib)
        libs += "-pthread "
        with tools.environment_append({"systemdsystemunitdir": self.package_folder, "LD_LIBRARY_PATH": libpath, "LIBS": libs}):
            autotools.configure(
                configure_dir=os.path.join(
                    self._source_subfolder),
                args=conf_args)
        self.run("make depend -j8")
        autotools.make()

    def package(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.install()
        from shutil import rmtree, copy
        from glob import glob
        rm_dirs = ["var", "share", "etc", "lib/pkgconfig"]
        rm_files = glob(os.path.join(self.package_folder, "lib/*.la"))
        rm_files.append("slapd.service")
        for target in rm_dirs:
            rmtree(
                os.path.join(
                    self.package_folder,
                    target),
                ignore_errors=False)
        for target in rm_files:
            os.remove(os.path.join(
                self.package_folder,
                target))
        licenses_dst = os.path.join(self.package_folder, "licenses")
        os.mkdir(licenses_dst)
        copy(
            os.path.join(
                self.build_folder,
                self._source_subfolder,
                "LICENSE"),
            licenses_dst)
        copy(
            os.path.join(
                self.build_folder,
                self._source_subfolder,
                "COPYRIGHT"),
            licenses_dst)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
