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

import ArgumentParser
import Foundation

// Package access lets the thin executable invoke Argument Parser while the command remains in the
// regular CIDRMergeCLI module used by SwiftPM and Xcode tests.
package struct CIDRMergeCommand: ParsableCommand {
    static let version = "0.2.0"

    package static let configuration = CommandConfiguration(
        commandName: "cidrmerge",
        abstract: "Compile IP addresses, networks, and ranges into a minimal, sorted, exact address cover.",
        version: version
    )

    @Flag
    var outputFormat: OutputFormat = .raw

    @Option(
        name: .customLong("input-format"),
        help: "Input grammar for every operand: text or searchbot. The default is text."
    )
    var inputFormat: InputFormat = .text

    @Option(
        name: .customLong("representation"),
        help: "Semantic representation: ranges or cidr. The default is ranges."
    )
    var representation: OutputRepresentation = .ranges

    @Flag(
        name: .customLong("stats"),
        help: "Write input, normalization, selected output, and count change to stderr."
    )
    var stats = false

    @Flag(
        name: .customLong("checksum"),
        help: "With --output, write a detached SHA-256 checksum file for the exact output bytes."
    )
    var checksum = false

    @Option(
        name: [.customShort("o"), .customLong("output")],
        help: "Write output atomically to a file instead of stdout."
    )
    var outputPath: String?

    @Argument(
        help: "Local input files. With no input, read stdin; use '-' once to include stdin explicitly."
    )
    var inputs: [String] = []

    package init() {}

    package mutating func validate() throws {
        try DetachedSHA256Checksum.validate(
            isEnabled: checksum,
            outputPath: outputPath
        )
        if inputs.lazy.filter({ $0 == "-" }).count > 1 {
            throw CIDRMergeError.repeatedStandardInput
        }
    }

    package mutating func run() throws {
        try CIDRMergeApplication.live.run(
            inputs: inputs,
            inputFormat: inputFormat,
            outputFormat: outputFormat,
            representation: representation,
            includeStatistics: stats,
            includeChecksum: checksum,
            outputPath: outputPath
        )
    }
}

enum OutputFormat: Sendable, CaseIterable {
    case raw
    case json
}

extension OutputFormat: EnumerableFlag {
    static func name(for value: Self) -> NameSpecification {
        switch value {
        case .raw:
            return .long
        case .json:
            return [.customShort("j"), .long]
        }
    }

    static func help(for value: Self) -> ArgumentHelp? {
        switch value {
        case .raw:
            return "Print one selected-representation value per line."
        case .json:
            return "Print structured JSON with representation and address-family arrays."
        }
    }
}

extension OutputRepresentation: ExpressibleByArgument {}
extension InputFormat: ExpressibleByArgument {}
