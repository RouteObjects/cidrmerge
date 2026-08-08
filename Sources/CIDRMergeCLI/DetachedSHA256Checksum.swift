//===----------------------------------------------------------------------===//
//
// This source file is part of the cidrmerge project.
//
// Copyright (c) 2026 Craig A. Munro
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
//
// SPDX-License-Identifier: Apache-2.0
//
//===----------------------------------------------------------------------===//

import Crypto
import Foundation

/// A detached SHA-256 checksum file for one exact rendered output artifact.
struct DetachedSHA256Checksum: Equatable, Sendable {
    let path: String
    let contents: Data

    static func validate(isEnabled: Bool, outputPath: String?) throws {
        guard isEnabled else { return }
        guard let outputPath else {
            throw CIDRMergeError.checksumRequiresOutput
        }

        let basename = URL(fileURLWithPath: outputPath).lastPathComponent
        guard !basename.contains("\r"), !basename.contains("\n") else {
            throw CIDRMergeError.invalidChecksumBasename(basename)
        }
    }

    static func render(output: Data, outputPath: String) throws -> Self {
        try validate(isEnabled: true, outputPath: outputPath)

        let basename = URL(fileURLWithPath: outputPath).lastPathComponent
        let digest = SHA256.hash(data: output)
        let hexadecimalDigits = Array("0123456789abcdef".utf8)
        var contents = Data()
        contents.reserveCapacity(64 + 2 + basename.utf8.count + 1)

        for byte in digest {
            contents.append(hexadecimalDigits[Int(byte >> 4)])
            contents.append(hexadecimalDigits[Int(byte & 0x0F)])
        }
        contents.append(0x20)
        contents.append(0x20)
        contents.append(contentsOf: basename.utf8)
        contents.append(0x0A)

        return Self(path: outputPath + ".sha256", contents: contents)
    }
}

/// Commits buffered output while preserving the checksum-first, fail-closed write contract.
struct OutputCommitter: Sendable {
    typealias AtomicFileWriter = @Sendable (_ data: Data, _ path: String) throws -> Void
    typealias StandardOutputWriter = @Sendable (_ data: Data) throws -> Void

    static let live = Self(
        atomicFileWriter: { data, path in
            // Foundation stages the replacement before atomically moving it into place.
            try data.write(to: URL(fileURLWithPath: path), options: .atomic)
        },
        standardOutputWriter: { data in
            try FileHandle.standardOutput.write(contentsOf: data)
        }
    )

    let atomicFileWriter: AtomicFileWriter
    let standardOutputWriter: StandardOutputWriter

    func write(
        _ output: Data,
        to outputPath: String?,
        includeChecksum: Bool
    ) throws {
        try DetachedSHA256Checksum.validate(
            isEnabled: includeChecksum,
            outputPath: outputPath
        )

        guard let outputPath else {
            try writeStandardOutput(output)
            return
        }

        if includeChecksum {
            // CHANGE: Commit the detached verifier first. Any later failure leaves a missing or
            // mismatched pair that an admission consumer using required verification rejects.
            let checksum = try DetachedSHA256Checksum.render(
                output: output,
                outputPath: outputPath
            )
            try writeFile(checksum.contents, to: checksum.path)
        }
        try writeFile(output, to: outputPath)
    }

    private func writeFile(_ data: Data, to path: String) throws {
        do {
            try atomicFileWriter(data, path)
        } catch {
            throw CIDRMergeError.outputWriteFailed(
                destination: path,
                reason: error.localizedDescription
            )
        }
    }

    private func writeStandardOutput(_ data: Data) throws {
        do {
            try standardOutputWriter(data)
        } catch {
            throw CIDRMergeError.outputWriteFailed(
                destination: "<stdout>",
                reason: error.localizedDescription
            )
        }
    }
}
