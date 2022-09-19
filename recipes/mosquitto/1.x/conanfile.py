from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, replace_in_file, copy, rmdir, rm
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=1.51.3"


class MosquittoConan(ConanFile):
    name = "mosquitto"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse/mosquitto"
    topics = ("mqtt", "broker", "libwebsockets", "mosquitto", "eclipse", "iot")
    license = "EPL-1.0", "BSD-3-Clause"
    description = "Eclipse Mosquitto - An open source MQTT broker"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_tls": [True, False],
               "with_websockets": [True, False],
               "with_threading": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_tls": True,
                       "with_websockets": True,
                       "with_threading": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_tls:
            self.requires("openssl/1.1.1q")
        if self.options.with_websockets:
            self.requires("libwebsockets/4.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["WITH_STATIC_LIBRARIES"] = not self.options.shared
        tc.variables["WITH_TLS"] = self.options.with_tls
        tc.variables["WITH_TLS_PSK"] = self.options.with_tls
        tc.variables["WITH_EC"] = self.options.with_tls
        tc.variables["DOCUMENTATION"] = False
        tc.variables["WITH_THREADING"] = not is_msvc(self) and self.options.with_threading
        if self.options.shared and is_msvc(self):
            tc.cache_variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        if self.settings.os == "Windows":
            if self.options.with_tls:
                replace_in_file(self, os.path.join(self.source_folder, "lib", "CMakeLists.txt"),
                                    "set (LIBRARIES ${LIBRARIES} ws2_32)",
                                    "set (LIBRARIES ${LIBRARIES} ws2_32 crypt32)")
                replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                                    "set (MOSQ_LIBS ${MOSQ_LIBS} ws2_32)",
                                    "set (MOSQ_LIBS ${MOSQ_LIBS} ws2_32 crypt32)")
                replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                                    "target_link_libraries(mosquitto_passwd ${OPENSSL_LIBRARIES})",
                                    "target_link_libraries(mosquitto_passwd ${OPENSSL_LIBRARIES} ws2_32 crypt32)")
            replace_in_file(self, os.path.join(self.source_folder, "lib", "CMakeLists.txt"),
                                "install(TARGETS libmosquitto RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")",
                                "install(TARGETS libmosquitto RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\" ARCHIVE DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")")
            replace_in_file(self, os.path.join(self.source_folder, "lib", "cpp", "CMakeLists.txt"),
                                "install(TARGETS mosquittopp RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")",
                                "install(TARGETS mosquittopp RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\" ARCHIVE DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="edl-v10", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="epl-v10", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="mosquitto.conf", src=self.source_folder, dst=os.path.join(self.package_folder, "res"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        if not self.options.shared:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dylib", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        lib_suffix = "_static" if not self.options.shared else ""
        # FIXME: there should be no namespace for CMake targets
        self.cpp_info.components["libmosquitto"].name = "mosquitto"
        self.cpp_info.components["libmosquitto"].libs = ["mosquitto" + lib_suffix]
        self.cpp_info.components["libmosquitto"].set_property("pkg_config_name", "libmosquitto")
        if self.options.with_tls:
            self.cpp_info.components["libmosquitto"].requires.append("openssl::openssl")
            self.cpp_info.components["libmosquitto"].defines.extend(["WITH_TLS", "WITH_TLS_PSK", "WITH_EC"])
        if self.options.with_websockets:
            self.cpp_info.components["libmosquitto"].requires.append("libwebsockets::libwebsockets")
            self.cpp_info.components["libmosquitto"].defines.append("WITH_WEBSOCKETS")
        if self.settings.os == "Windows":
            self.cpp_info.components["libmosquitto"].system_libs.append("ws2_32")
            if self.options.with_tls:
                self.cpp_info.components["libmosquitto"].system_libs.append("crypt32")
        elif self.settings.os == "Linux":
            self.cpp_info.components["libmosquitto"].system_libs.extend(["rt", "pthread", "dl"])

        self.cpp_info.components["libmosquittopp"].name = "mosquittopp"
        self.cpp_info.components["libmosquittopp"].libs = ["mosquittopp" + lib_suffix]
        self.cpp_info.components["libmosquittopp"].requires = ["libmosquitto"]
        self.cpp_info.components["libmosquittopp"].set_property("pkg_config_name", "libmosquittopp")
        if not self.options.shared:
            self.cpp_info.components["libmosquitto"].defines.append("LIBMOSQUITTO_STATIC")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
