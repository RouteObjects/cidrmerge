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

import SystemPackage

#if canImport(FoundationEssentials)
    import FoundationEssentials
#else
    import Foundation
#endif

struct CIDRMergeApplication: Sendable {
    typealias InputLoader =
        @Sendable (_ inputs: [String], _ format: InputFormat, _ collectNormalizationStatistics: Bool) throws ->
        ParsedInput
    typealias OutputWriter =
        @Sendable (_ output: Data, _ path: String?, _ includeChecksum: Bool) throws -> Void
    typealias DiagnosticWriter = @Sendable (_ diagnostics: Data) throws -> Void

    static let live = CIDRMergeApplication(
        inputLoader: { inputs, format, collectNormalizationStatistics in
            switch format {
            case .text:
                try TextInputLoader.load(inputs: inputs, collectNormalizationStatistics: collectNormalizationStatistics)
            case .searchbot:
                try SearchbotInputLoader.load(
                    inputs: inputs, collectNormalizationStatistics: collectNormalizationStatistics)
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
            try DescriptorIO.write(diagnostics, to: .standardError)
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
        // Reject incompatible destinations before an input file or stdin is consumed.
        try DetachedSHA256Checksum.validate(
            isEnabled: includeChecksum,
            outputPath: outputPath
        )

        // CHANGE: Canonical formatting is needed only when normalization statistics will be emitted.
        let parsedInput = try inputLoader(inputs, inputFormat, includeStatistics)
        let result = parsedInput.merged(representation: representation)
        let output = try OutputRenderer.render(result, format: outputFormat)

        // Commit rendered output once and only after every input has parsed and merged.
        try outputWriter(output, outputPath, includeChecksum)
        if includeStatistics {
            try diagnosticWriter(OutputRenderer.statistics(result.statistics))
        }
    }
}
