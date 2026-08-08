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

import Foundation
import Testing

@testable import CIDRMergeCLI

@Suite("Detached SHA-256 Checksum Tests")
struct DetachedSHA256ChecksumTests {
    @Test("Detached checksum bytes match the documented exact-output record")
    func rendersDocumentedRecord() throws {
        let output = Data(
            """
            192.0.2.0...192.0.2.191
            2001:db8::...2001:db8::3

            """.utf8
        )

        let checksum = try DetachedSHA256Checksum.render(
            output: output,
            outputPath: "/staging/generation/allow.txt"
        )

        #expect(checksum.path == "/staging/generation/allow.txt.sha256")
        #expect(
            String(decoding: checksum.contents, as: UTF8.self)
                == "fc0e96431e295e3cf11d17eabe4043dfc7a968c43cbc241f548c52e2175cb04c  allow.txt\n"
        )
    }

    @Test("Empty raw output hashes exactly zero bytes")
    func hashesEmptyOutput() throws {
        let checksum = try DetachedSHA256Checksum.render(
            output: Data(),
            outputPath: "empty ranges.txt"
        )

        #expect(
            String(decoding: checksum.contents, as: UTF8.self)
                == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  empty ranges.txt\n"
        )
    }

    @Test("The basename is recorded literally, including spaces and Unicode")
    func preservesLiteralBasename() throws {
        let checksum = try DetachedSHA256Checksum.render(
            output: Data(),
            outputPath: "/generation/policy  α.txt"
        )

        #expect(
            String(decoding: checksum.contents, as: UTF8.self)
                == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  policy  α.txt\n"
        )
    }

    @Test("JSON checksum covers the renderer's final line feed")
    func hashesExactJSONBytes() throws {
        let result = try TextInputLoader.load(
            data: Data("192.0.2.0/24\n2001:db8::/32\n".utf8)
        ).merged(representation: .cidr)
        let output = try OutputRenderer.json(result)
        let checksum = try DetachedSHA256Checksum.render(
            output: output,
            outputPath: "policy.json"
        )

        #expect(output.last == 0x0A)
        #expect(
            String(decoding: checksum.contents, as: UTF8.self)
                == "901df054b3fb4eb812693875e0a8b52db5fc112afd76e1402e732cfcd4f2bdac  policy.json\n"
        )
    }

    @Test("Checksum mode requires file output before input is loaded")
    func rejectsStandardOutputBeforeInput() {
        let recorder = ChecksumApplicationRecorder()
        let application = CIDRMergeApplication(
            inputLoader: { _, _ in
                recorder.recordInput()
                return ParsedInput()
            },
            outputWriter: { _, _, _ in
                recorder.recordOutput()
            },
            diagnosticWriter: { _ in
                recorder.recordDiagnostics()
            }
        )

        #expect(throws: CIDRMergeError.checksumRequiresOutput) {
            try application.run(
                inputs: ["/definitely/missing/input.txt"],
                outputFormat: .raw,
                representation: .ranges,
                includeStatistics: true,
                includeChecksum: true,
                outputPath: nil
            )
        }
        #expect(recorder.events.isEmpty)
    }

    @Test("Checksum mode rejects CR and LF in the output basename before input")
    func rejectsUnsafeBasenamesBeforeInput() {
        for path in ["directory/policy\r.txt", "directory/policy\n.txt"] {
            let recorder = ChecksumApplicationRecorder()
            let application = CIDRMergeApplication(
                inputLoader: { _, _ in
                    recorder.recordInput()
                    return ParsedInput()
                },
                outputWriter: { _, _, _ in
                    recorder.recordOutput()
                },
                diagnosticWriter: { _ in
                    recorder.recordDiagnostics()
                }
            )

            #expect(throws: CIDRMergeError.self) {
                try application.run(
                    inputs: [],
                    outputFormat: .raw,
                    representation: .ranges,
                    includeStatistics: true,
                    includeChecksum: true,
                    outputPath: path
                )
            }
            #expect(recorder.events.isEmpty)
        }
    }

    @Test("The detached checksum is committed before the exact output")
    func writesChecksumFirst() throws {
        let recorder = AtomicWriteRecorder()
        let committer = OutputCommitter(
            atomicFileWriter: { data, path in
                recorder.write(data, to: path)
            },
            standardOutputWriter: { _ in
                Issue.record("File output must not write standard output")
            }
        )

        try committer.write(
            Data("192.0.2.0...192.0.2.255\n".utf8),
            to: "/generation/allow.txt",
            includeChecksum: true
        )

        #expect(recorder.paths == ["/generation/allow.txt.sha256", "/generation/allow.txt"])
        #expect(recorder.data.count == 2)
        #expect(recorder.data[1] == Data("192.0.2.0...192.0.2.255\n".utf8))
        #expect(String(decoding: recorder.data[0], as: UTF8.self).hasSuffix("  allow.txt\n"))
    }

    @Test("A detached checksum failure leaves the output untouched")
    func stopsAfterChecksumFailure() {
        let recorder = AtomicWriteRecorder(failingWrite: 1)
        let committer = OutputCommitter(
            atomicFileWriter: { data, path in
                try recorder.writeOrFail(data, to: path)
            },
            standardOutputWriter: { _ in }
        )

        do {
            try committer.write(
                Data("new output\n".utf8),
                to: "/generation/allow.txt",
                includeChecksum: true
            )
            Issue.record("Expected the detached checksum write to fail")
        } catch let error as CIDRMergeError {
            guard case .outputWriteFailed(let destination, _) = error else {
                Issue.record("Unexpected error: \(error)")
                return
            }
            #expect(destination == "/generation/allow.txt.sha256")
        } catch {
            Issue.record("Unexpected error: \(error)")
        }

        #expect(recorder.paths == ["/generation/allow.txt.sha256"])
    }

    @Test("An output failure leaves the newly committed checksum fail-closed")
    func outputFailureFollowsChecksumCommit() {
        let recorder = AtomicWriteRecorder(failingWrite: 2)
        let committer = OutputCommitter(
            atomicFileWriter: { data, path in
                try recorder.writeOrFail(data, to: path)
            },
            standardOutputWriter: { _ in }
        )

        do {
            try committer.write(
                Data("new output\n".utf8),
                to: "/generation/allow.txt",
                includeChecksum: true
            )
            Issue.record("Expected the output write to fail")
        } catch let error as CIDRMergeError {
            guard case .outputWriteFailed(let destination, _) = error else {
                Issue.record("Unexpected error: \(error)")
                return
            }
            #expect(destination == "/generation/allow.txt")
        } catch {
            Issue.record("Unexpected error: \(error)")
        }

        #expect(recorder.paths == ["/generation/allow.txt.sha256", "/generation/allow.txt"])
        #expect(recorder.successfulWriteCount == 1)
    }

    @Test("Statistics are emitted only after the complete pair commits")
    func outputFailurePreventsStatistics() {
        let writes = AtomicWriteRecorder(failingWrite: 2)
        let applicationEvents = ChecksumApplicationRecorder()
        let committer = OutputCommitter(
            atomicFileWriter: { data, path in
                try writes.writeOrFail(data, to: path)
            },
            standardOutputWriter: { _ in }
        )
        let application = CIDRMergeApplication(
            inputLoader: { _, _ in
                try TextInputLoader.load(data: Data("192.0.2.0/24\n".utf8))
            },
            outputWriter: { output, path, includeChecksum in
                try committer.write(
                    output,
                    to: path,
                    includeChecksum: includeChecksum
                )
            },
            diagnosticWriter: { _ in
                applicationEvents.recordDiagnostics()
            }
        )

        #expect(throws: CIDRMergeError.self) {
            try application.run(
                inputs: [],
                outputFormat: .raw,
                representation: .ranges,
                includeStatistics: true,
                includeChecksum: true,
                outputPath: "/generation/allow.txt"
            )
        }
        #expect(applicationEvents.events.isEmpty)
        #expect(writes.successfulWriteCount == 1)
    }

    @Test("Checksum-disabled output does not touch a detached checksum file")
    func leavesChecksumAloneWhenDisabled() throws {
        let recorder = AtomicWriteRecorder()
        let committer = OutputCommitter(
            atomicFileWriter: { data, path in
                recorder.write(data, to: path)
            },
            standardOutputWriter: { _ in }
        )

        try committer.write(
            Data("output\n".utf8),
            to: "policy.txt",
            includeChecksum: false
        )

        #expect(recorder.paths == ["policy.txt"])
    }

    @Test("The live committer atomically replaces both files")
    func writesLiveArtifactPair() throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent("cidrmerge-checksum-tests-\(UUID().uuidString)")
        try FileManager.default.createDirectory(
            at: directory,
            withIntermediateDirectories: true
        )
        defer { try? FileManager.default.removeItem(at: directory) }

        let outputURL = directory.appendingPathComponent("allow ranges.txt")
        let checksumURL = URL(fileURLWithPath: outputURL.path + ".sha256")
        try Data("old output\n".utf8).write(to: outputURL)
        try Data("old checksum\n".utf8).write(to: checksumURL)

        let output = Data("192.0.2.0...192.0.2.255\n".utf8)
        try OutputCommitter.live.write(
            output,
            to: outputURL.path,
            includeChecksum: true
        )

        #expect(try Data(contentsOf: outputURL) == output)
        #expect(
            try String(contentsOf: checksumURL, encoding: .utf8)
                == "4fadfa35475984133bb25b33cbb5e793e475888f0c2f1d1347f4df2c7b06f52e  allow ranges.txt\n"
        )
    }
}

private struct ExpectedAtomicWriteFailure: Error, LocalizedError {
    var errorDescription: String? { "expected atomic write failure" }
}

private final class AtomicWriteRecorder: @unchecked Sendable {
    private let lock = NSLock()
    private let failingWrite: Int?
    private var writes: [(path: String, data: Data)] = []
    private var attempts = 0
    private var successfulWrites = 0

    init(failingWrite: Int? = nil) {
        self.failingWrite = failingWrite
    }

    var paths: [String] {
        lock.withLock { writes.map(\.path) }
    }

    var data: [Data] {
        lock.withLock { writes.map(\.data) }
    }

    var successfulWriteCount: Int {
        lock.withLock { successfulWrites }
    }

    func write(_ data: Data, to path: String) {
        lock.withLock {
            attempts += 1
            writes.append((path, data))
            successfulWrites += 1
        }
    }

    func writeOrFail(_ data: Data, to path: String) throws {
        try lock.withLock {
            attempts += 1
            if attempts == failingWrite {
                // Record attempted destinations so the failure order remains observable.
                writes.append((path, data))
                throw ExpectedAtomicWriteFailure()
            }
            writes.append((path, data))
            successfulWrites += 1
        }
    }
}

private final class ChecksumApplicationRecorder: @unchecked Sendable {
    private let lock = NSLock()
    private var recordedEvents: [String] = []

    var events: [String] {
        lock.withLock { recordedEvents }
    }

    func recordInput() {
        lock.withLock { recordedEvents.append("input") }
    }

    func recordOutput() {
        lock.withLock { recordedEvents.append("output") }
    }

    func recordDiagnostics() {
        lock.withLock { recordedEvents.append("diagnostics") }
    }
}
