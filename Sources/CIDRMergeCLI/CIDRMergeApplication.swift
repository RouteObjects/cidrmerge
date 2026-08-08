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
    typealias InputLoader = @Sendable (_ inputs: [String], _ format: InputFormat) throws -> ParsedInput
    typealias OutputWriter =
        @Sendable (_ output: Data, _ path: String?, _ includeChecksum: Bool) throws -> Void
    typealias DiagnosticWriter = @Sendable (_ diagnostics: Data) throws -> Void

    static let live = CIDRMergeApplication(
        inputLoader: { inputs, format in
            switch format {
            case .text:
                try TextInputLoader.load(inputs: inputs)
            case .searchbot:
                try SearchbotInputLoader.load(inputs: inputs)
            }
        },
        outputWriter: { output, path, includeChecksum in
            try OutputCommitter.live.write(
                output,
                to: path,
                includeChecksum: includeChecksum
            )
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
        inputFormat: InputFormat = .text,
        outputFormat: OutputFormat,
        representation: OutputRepresentation,
        includeStatistics: Bool,
        includeChecksum: Bool = false,
        outputPath: String?
    ) throws {
        // CHANGE: Reject incompatible destinations before an input file or stdin is consumed.
        try DetachedSHA256Checksum.validate(
            isEnabled: includeChecksum,
            outputPath: outputPath
        )

        let parsedInput = try inputLoader(inputs, inputFormat)
        let result = parsedInput.merged(representation: representation)
        let output = try OutputRenderer.render(result, format: outputFormat)

        // Commit rendered output once and only after every input has parsed and merged.
        try outputWriter(output, outputPath, includeChecksum)
        if includeStatistics {
            try diagnosticWriter(OutputRenderer.statistics(result.statistics))
        }
    }
}
