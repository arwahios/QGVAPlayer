// swift-tools-version: 5.9
//
//  Package.swift
//  QGVAPlayer
//
//  Created by Arwah on 2026/10/07.
//
//  Based on Tencent/vap iOS1.0.19 (+ Haya safety patches). Feature must not import this
//  directly — only EffectKit Adapter.
//  Product is `.dynamic` so the host app embeds one QGVAPlayer.framework that Flutter
//  (and native EffectKit) can share at runtime.
//

import PackageDescription

let package = Package(
    name: "QGVAPlayer",
    platforms: [.iOS(.v16)],
    products: [
        .library(name: "QGVAPlayer", type: .dynamic, targets: ["QGVAPlayer"])
    ],
    targets: [
        .target(
            name: "QGVAPlayer",
            path: "Sources/QGVAPlayer",
            exclude: ["Info.plist"],
            publicHeadersPath: "include",
            cSettings: [
                .headerSearchPath("Classes"),
                .headerSearchPath("Classes/Models"),
                .headerSearchPath("Classes/Controllers"),
                .headerSearchPath("Classes/Controllers/Decoders"),
                .headerSearchPath("Classes/MP4Parser"),
                .headerSearchPath("Classes/Utils"),
                .headerSearchPath("Classes/Utils/Categorys"),
                .headerSearchPath("Classes/Utils/Logger"),
                .headerSearchPath("Classes/Views/Metal"),
                .headerSearchPath("Classes/Views/Metal/Vapx"),
                .headerSearchPath("Classes/Views/OpenGL"),
                .headerSearchPath("Shaders"),
            ],
            linkerSettings: [
                .linkedFramework("Metal"),
                .linkedFramework("MetalKit"),
                .linkedFramework("AVFoundation"),
                .linkedFramework("CoreVideo"),
                .linkedFramework("CoreMedia"),
                .linkedFramework("CoreGraphics"),
                .linkedFramework("UIKit"),
                .linkedFramework("OpenGLES"),
                .linkedFramework("AudioToolbox"),
                .linkedFramework("VideoToolbox"),
            ]
        )
    ]
)
