[app]
title = Nexus Mobile
package.name = nexusmobile
package.domain = org.nexus
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3, kivy==2.3.0, cython<3.0.0, pyjnius, android
orientation = portrait
fullscreen = 1
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CAMERA
android.api = 33
android.minapi = 21
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
