[app]
title = ESP32 Remote
package.name = esp32remote
package.domain = org.esp32
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.archs = arm64-v8a
android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
p4a.branch = release-2024.01.21

[buildozer]
log_level = 2
warn_on_root = 0
