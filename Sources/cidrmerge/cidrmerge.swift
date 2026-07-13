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

@main
struct CIDRMerge: ParsableCommand {
    static let version = "0.1.0"

    static let configuration = CommandConfiguration(
        commandName: "cidrmerge",
        abstract: "Compile IP addresses and networks into a minimal, sorted, exact CIDR cover."
    )

    @Option(
        name: .customLong("input-format"),
        help: "Input format. Phase 1 supports: text."
    )
    var inputFormat: InputFormat = .text

    @Option(
        name: .customLong("output-format"),
        help: "Output format: text or json. The default is text."
    )
    var outputFormat: OutputFormat?

    @Flag(
        name: .customLong("json"),
        help: "Emit JSON. This cannot be combined with --output-format."
    )
    var json = false

    @Flag(
        name: .customLong("stats"),
        help: "Write input, normalization, output, and reduction counts to stderr."
    )
    var stats = false

    @Option(
        name: [.customShort("o"), .customLong("output")],
        help: "Write output atomically to a file instead of stdout."
    )
    var outputPath: String?

    @Flag(
        name: [.customShort("v"), .customLong("version")],
        help: "Show the cidrmerge version."
    )
    var showVersion = false

    @Argument(
        help: "Local text files. With no input, read stdin; use '-' once to include stdin explicitly."
    )
    var inputs: [String] = []

    mutating func validate() throws {
        if json, outputFormat != nil {
            throw CIDRMergeError.conflictingOutputFormats
        }
        if inputs.lazy.filter({ $0 == "-" }).count > 1 {
            throw CIDRMergeError.repeatedStandardInput
        }
    }

    mutating func run() throws {
        if showVersion {
            print(Self.version)
            return
        }

        let format = json ? OutputFormat.json : outputFormat ?? .text
        let collection = try TextInputLoader.load(inputs: inputs)
        let result = collection.merged()

        let output: Data
        switch format {
        case .text:
            output = OutputRenderer.text(result)
        case .json:
            output = OutputRenderer.json(result)
        }

        try Self.write(output, to: outputPath)
        if stats {
            try FileHandle.standardError.write(
                contentsOf: OutputRenderer.statistics(result.statistics)
            )
        }
    }

    static func write(_ data: Data, to outputPath: String?) throws {
        do {
            if let outputPath {
                // CHANGE: Foundation's atomic option prevents a failed write from replacing the destination.
                try data.write(
                    to: URL(fileURLWithPath: outputPath),
                    options: .atomic
                )
            } else {
                try FileHandle.standardOutput.write(contentsOf: data)
            }
        } catch {
            throw CIDRMergeError.outputWriteFailed(
                destination: outputPath ?? "<stdout>",
                reason: error.localizedDescription
            )
        }
    }
}

enum InputFormat: String, ExpressibleByArgument {
    case text
}

enum OutputFormat: String, ExpressibleByArgument {
    case text
    case json
}
