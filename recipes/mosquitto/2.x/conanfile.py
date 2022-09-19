import os
from conan import ConanFile
from conan.tools.files import get, replace_in_file, rmdir, rm, copy
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc


required_conan_version = ">=1.51.3"


class Mosquitto(ConanFile):
    name = "mosquitto"
    license = "EPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mosquitto.org"
    description = """Eclipse Mosquitto MQTT library, broker and more"""
    topics = ("MQTT", "IoT", "eclipse")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ssl": [True, False],
        "clients": [True, False],
        "broker": [True, False],
        "apps": [True, False],
        "cjson": [True, False],
        "build_cpp": [True, False],
        "websockets": [True, False],
        "threading": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ssl": True,
        "clients": False,
        "broker": False,
        "apps": False,
        "cjson": True, # https://github.com/eclipse/mosquitto/commit/bbe0afbfbe7bb392361de41e275759ee4ef06b1c
        "build_cpp": True,
        "websockets": False,
        "threading": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.clients:
            del self.options.cjson
        if not self.options.broker:
            del self.options.websockets
        if not self.options.build_cpp:
            try:
                del self.settings.compiler.libcxx
            except Exception:
                pass
            try:
                del self.settings.compiler.cppstd
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.ssl:
            self.requires("openssl/1.1.1q")
        if self.options.get_safe("cjson"):
            self.requires("cjson/1.7.14")
        if self.options.get_safe("websockets"):
            self.requires("libwebsockets/4.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_STATIC_LIBRARIES"] = not self.options.shared
        tc.variables["WITH_PIC"] = self.options.get_safe("fPIC", False)
        tc.variables["WITH_TLS"] = self.options.ssl
        tc.variables["WITH_CLIENTS"] = self.options.clients
        if Version(self.version) < "2.0.6":
            tc.variables["CMAKE_DISABLE_FIND_PACKAGE_cJSON"] = not self.options.get_safe("cjson")
        else:
            tc.variables["WITH_CJSON"] = self.options.get_safe("cjson")
        tc.variables["WITH_BROKER"] = self.options.broker
        tc.variables["WITH_APPS"] = self.options.apps
        tc.variables["WITH_PLUGINS"] = False
        tc.variables["WITH_LIB_CPP"] = self.options.build_cpp
        tc.variables["WITH_THREADING"] = self.settings.compiler != "Visual Studio" and self.options.threading
        tc.variables["WITH_WEBSOCKETS"] = self.options.get_safe("websockets", False)
        tc.variables["STATIC_WEBSOCKETS"] = self.options.get_safe("websockets", False) and not self.options["libwebsockets"].shared
        tc.variables["DOCUMENTATION"] = False
        tc.variables["CMAKE_INSTALL_SYSCONFDIR"] = os.path.join(self.package_folder, "res").replace("\\", "/")
        if self.options.shared and is_msvc(self):
            tc.cache_variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "client", "CMakeLists.txt"), "static)", "static ${CONAN_LIBS})")
        replace_in_file(self, os.path.join(self.source_folder, "client", "CMakeLists.txt"), "quitto)", "quitto ${CONAN_LIBS})")
        replace_in_file(self, os.path.join(self.source_folder, "apps", "mosquitto_ctrl", "CMakeLists.txt"), "static)", "static ${CONAN_LIBS})")
        replace_in_file(self, os.path.join(self.source_folder, "apps", "mosquitto_ctrl", "CMakeLists.txt"), "quitto)", "quitto ${CONAN_LIBS})")
        replace_in_file(self, os.path.join(self.source_folder, "apps", "mosquitto_passwd", "CMakeLists.txt"), "OPENSSL_LIBRARIES", "CONAN_LIBS")
        replace_in_file(self, os.path.join(self.source_folder, "apps", "mosquitto_ctrl", "CMakeLists.txt"), "OPENSSL_LIBRARIES", "CONAN_LIBS")
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"), "OPENSSL_LIBRARIES", "CONAN_LIBS")
        replace_in_file(self, os.path.join(self.source_folder, "lib", "CMakeLists.txt"), "OPENSSL_LIBRARIES", "CONAN_LIBS")
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"), "MOSQ_LIBS", "CONAN_LIBS")
        replace_in_file(self, os.path.join(self.source_folder, "include", "mosquitto.h"), "__declspec(dllimport)", "")
        replace_in_file(self, os.path.join(self.source_folder, "lib", "cpp", "mosquittopp.h"), "__declspec(dllimport)", "")
        # dynlibs for apple mobile want code signatures and that will not work here
        # this would actually be the right patch for static builds also, but this would have other side effects, so
        if(self.settings.os in ["iOS", "watchOS", "tvOS"]):
            replace_in_file(self, os.path.join(self.source_folder, "lib", "CMakeLists.txt"), "SHARED", "")
            replace_in_file(self, os.path.join(self.source_folder, "lib", "cpp", "CMakeLists.txt"), "SHARED", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "edl-v10", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "epl-v20", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.example", os.path.join(self.package_folder, "res"))
        if not self.options.shared:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dylib", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
        elif self.options.shared and is_msvc(self):
            copy(self, "mosquitto.lib", src=os.path.join(self.build_folder, "lib"), dst=os.path.join(self.package_folder, "lib"))
            if self.options.build_cpp:
                copy(self, "mosquittopp.lib", src=os.path.join(self.build_folder, "lib"), dst=os.path.join(self.package_folder, "lib"))

    def package_info(self):
        libsuffix = "" if self.options.shared else "_static"
        self.cpp_info.components["libmosquitto"].set_property("pkg_config_name", "libmosquitto")
        self.cpp_info.components["libmosquitto"].libs = ["mosquitto" + libsuffix]
        if self.options.ssl:
            self.cpp_info.components["libmosquitto"].requires = ["openssl::openssl"]
        if self.settings.os == "Linux":
            self.cpp_info.components["libmosquitto"].system_libs = ["pthread", "m"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libmosquitto"].system_libs = ["ws2_32"]

        if self.options.build_cpp:
            self.cpp_info.components["libmosquittopp"].set_property("pkg_config_name", "libmosquittopp")
            self.cpp_info.components["libmosquittopp"].libs = ["mosquittopp" + libsuffix]
            self.cpp_info.components["libmosquittopp"].requires = ["libmosquitto"]
            if self.settings.os == "Linux":
                self.cpp_info.components["libmosquittopp"].system_libs = ["pthread", "m"]
            elif self.settings.os == "Windows":
                self.cpp_info.components["libmosquittopp"].system_libs = ["ws2_32"]

        if self.options.broker or self.options.get_safe("apps") or self.options.get_safe("clients"):
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var with : {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        if self.options.broker:
            self.cpp_info.components["mosquitto_broker"].libdirs = []
            self.cpp_info.components["mosquitto_broker"].include_dirs = []
            if self.options.websockets:
                self.cpp_info.components["mosquitto_broker"].requires.append("libwebsockets::libwebsockets")
            if self.settings.os in ("FreeBSD", "Linux"):
                self.cpp_info.components["mosquitto_broker"].system_libs = ["pthread", "m"]
            elif self.settings.os == "Windows":
                self.cpp_info.components["mosquitto_broker"].system_libs = ["ws2_32"]

        for option in ["apps", "clients"]:
            if self.options.get_safe(option):
                option_comp_name = "mosquitto_{}".format(option)
                self.cpp_info.components[option_comp_name].libdirs = []
                self.cpp_info.components[option_comp_name].include_dirs = []
                self.cpp_info.components[option_comp_name].requires = ["openssl::openssl", "libmosquitto"]
                if self.options.cjson:
                    self.cpp_info.components[option_comp_name].requires.append("cjson::cjson")
