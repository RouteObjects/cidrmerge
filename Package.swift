// swift-tools-version: 6.1

//===----------------------------------------------------------------------===//
//
// This source file is part of the cidrmerge project.
//
// Copyright (c) 2026 Craig A. Munro
//
// Licensed under the Apache License, Version 2.0.
// See the LICENSE file for details.
//
// SPDX-License-Identifier: Apache-2.0
//
//===----------------------------------------------------------------------===//

import PackageDescription

let package = Package(
    name: "cidrmerge",
    platforms: [
        .iOS(.v18),  // Match swift-cidr's UInt128 deployment floor for Xcode builds.
        .macOS(.v15),
    ],
    products: [
        .library(name: "CIDRMergeCore", targets: ["CIDRMergeCore"]),
        .executable(name: "cidrmerge", targets: ["CIDRMergeExecutable"]),
    ],
    dependencies: [
        .package(
            url: "https://github.com/RouteObjects/swift-cidr.git",
            .upToNextMinor(from: "0.5.0")
        ),
        .package(
            url: "https://github.com/apple/swift-argument-parser",
            .upToNextMajor(from: "1.7.0")
        ),
        .package(
            url: "https://github.com/apple/swift-crypto.git",
            .upToNextMajor(from: "4.5.1")
        ),
    ],
    targets: [
        .target(
            name: "CIDRMergeCore",
            dependencies: [
                // swift-cidr is the sole owner of address-range and exact-coverage math.
                .product(name: "CIDR", package: "swift-cidr")
            ]
        ),
        // Keep command parsing and process I/O importable for SwiftPM and Xcode tests.
        .target(
            name: "CIDRMergeCLI",
            dependencies: [
                "CIDRMergeCore",
                .product(name: "ArgumentParser", package: "swift-argument-parser"),
                .product(name: "CIDR", package: "swift-cidr"),
                // CHANGE: Exact-byte integrity belongs to the CLI artifact boundary, not Core.
                .product(name: "Crypto", package: "swift-crypto"),
            ]
        ),
        // The executable target owns only process startup and delegates to CIDRMergeCLI.
        .executableTarget(
            name: "CIDRMergeExecutable",
            dependencies: ["CIDRMergeCLI"]
        ),
        .testTarget(
            name: "CIDRMergeCoreTests",
            dependencies: [
                "CIDRMergeCore",
                .product(name: "CIDR", package: "swift-cidr"),
            ]
        ),
        .testTarget(
            name: "CIDRMergeCLITests",
            dependencies: [
                "CIDRMergeCLI",
                "CIDRMergeCore",
                .product(name: "CIDR", package: "swift-cidr"),
            ],
            resources: [.process("Fixtures")]
        ),
    ],
    swiftLanguageModes: [.v6]
)
