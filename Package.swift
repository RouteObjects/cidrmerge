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
        .iOS(.v18),  // CHANGE: Match swift-cidr's UInt128 deployment floor for Xcode builds.
        .macOS(.v15),
    ],
    products: [
        .executable(name: "cidrmerge", targets: ["cidrmerge"])
    ],
    dependencies: [
        .package(url: "https://github.com/RouteObjects/swift-cidr.git", from: "0.3.0"),
        .package(url: "https://github.com/apple/swift-argument-parser", from: "1.7.0"),
    ],
    targets: [
        .executableTarget(
            name: "cidrmerge",
            dependencies: [
                .product(name: "ArgumentParser", package: "swift-argument-parser"),
                .product(name: "CIDR", package: "swift-cidr"),
            ]
        ),
        .testTarget(
            name: "cidrmergeTests",
            dependencies: [
                "cidrmerge",
                .product(name: "CIDR", package: "swift-cidr"),
            ]
        ),
    ],
    swiftLanguageModes: [.v6]
)
