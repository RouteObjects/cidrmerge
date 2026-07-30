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

import Foundation

struct CIDRMergeApplication: Sendable {
    typealias InputLoader = @Sendable (_ inputs: [String]) throws -> ParsedInput
    typealias OutputWriter = @Sendable (_ output: Data, _ path: String?) throws -> Void
    typealias DiagnosticWriter = @Sendable (_ diagnostics: Data) throws -> Void

    static let live = CIDRMergeApplication(
        inputLoader: { inputs in
            try TextInputLoader.load(inputs: inputs)
        },
        outputWriter: { output, path in
            try write(output, to: path)
        },
        diagnosticWriter: { diagnostics in
            try FileHandle.standardError.write(contentsOf: diagnostics)
        }
    )

    let inputLoader: InputLoader
    let outputWriter: OutputWriter
    let diagnosticWriter: DiagnosticWriter

    func run(
        inputs: [String],
        outputFormat: OutputFormat,
        representation: OutputRepresentation,
        includeStatistics: Bool,
        outputPath: String?
    ) throws {
        let parsedInput = try inputLoader(inputs)
        let result = parsedInput.merged(representation: representation)
        let output = try OutputRenderer.render(result, format: outputFormat)

        // CHANGE: Commit rendered output once and only after every input has parsed and merged.
        try outputWriter(output, outputPath)
        if includeStatistics {
            try diagnosticWriter(OutputRenderer.statistics(result.statistics))
        }
    }

    static func write(_ data: Data, to outputPath: String?) throws {
        do {
            if let outputPath {
                // CHANGE: Atomic replacement prevents a failed write from corrupting the destination.
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
