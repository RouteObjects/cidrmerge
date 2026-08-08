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
import Testing

@testable import CIDRMergeCLI

@Suite("Text Input Tests")
struct TextInputTests {
    @Test("Text input accepts hosts, networks, comments, BOM, and CRLF")
    func acceptsPhaseOneTextSemantics() throws {
        var data = Data([0xEF, 0xBB, 0xBF])
        data.append(
            Data(
                """
                # comment\r
                192.0.2.7\r
                192.0.2.129/24 # containing network\r
                2001:0DB8::1/64\r

                """.utf8
            )
        )

        let collection = try TextInputLoader.load(data: data, source: "fixture.txt")
        let result = collection.merged()

        #expect(result.ipv4.descriptions == ["192.0.2.0...192.0.2.255"])
        #expect(result.ipv6.descriptions == ["2001:db8::...2001:db8::ffff:ffff:ffff:ffff"])
        #expect(result.statistics.inputCount == 3)
        #expect(result.statistics.inputIPv4Count == 2)
        #expect(result.statistics.inputIPv6Count == 1)
        #expect(result.statistics.normalizedInputCount == 3)
    }

    @Test("Malformed prefixes report source, line, and token")
    func malformedPrefixHasContext() {
        do {
            _ = try TextInputLoader.load(
                data: Data("192.0.2.0/24\n192.0.2.0/33\n".utf8),
                source: "routes.txt"
            )
            Issue.record("Expected malformed input to throw.")
        } catch let error as CIDRMergeError {
            #expect(
                error
                    == .invalidInput(
                        source: "routes.txt",
                        line: 2,
                        value: "192.0.2.0/33"
                    )
            )
        } catch {
            Issue.record("Unexpected error: \(error)")
        }
    }

    @Test("Text input accepts strict address ranges and canonicalizes their spelling")
    func acceptsAddressRanges() throws {
        let collection = try TextInputLoader.load(
            data: Data("2001:0DB8::1...2001:0DB8::F\n192.0.2.2...192.0.2.7\n".utf8)
        )
        let result = collection.merged()

        #expect(result.ipv4.descriptions == ["192.0.2.2...192.0.2.7"])
        #expect(result.ipv6.descriptions == ["2001:db8::1...2001:db8::f"])
        #expect(result.statistics.normalizedInputCount == 1)
    }

    @Test("Malformed ranges report source, line, and token")
    func malformedRangeHasContext() {
        do {
            _ = try TextInputLoader.load(
                data: Data("192.0.2.7...192.0.2.2\n".utf8),
                source: "ranges.txt"
            )
            Issue.record("Expected malformed range input to throw.")
        } catch let error as CIDRMergeError {
            #expect(
                error
                    == .invalidInput(
                        source: "ranges.txt",
                        line: 1,
                        value: "192.0.2.7...192.0.2.2"
                    )
            )
        } catch {
            Issue.record("Unexpected error: \(error)")
        }
    }

    @Test("Additional routing columns are rejected instead of discarded")
    func rejectsAdditionalColumns() {
        #expect(throws: (any Error).self) {
            try TextInputLoader.load(
                data: Data("192.0.2.0/24 64496\n".utf8),
                source: "rib.txt"
            )
        }
    }

    @Test("Invalid UTF-8 reports the affected logical line")
    func rejectsInvalidUTF8() {
        do {
            _ = try TextInputLoader.load(
                data: Data([0x31, 0x30, 0x2E, 0x30, 0x2E, 0x30, 0x2E, 0x31, 0x0A, 0xFF]),
                source: "bytes.txt"
            )
            Issue.record("Expected invalid UTF-8 to throw.")
        } catch let error as CIDRMergeError {
            #expect(error == .invalidUTF8(source: "bytes.txt", line: 2))
        } catch {
            Issue.record("Unexpected error: \(error)")
        }
    }

    @Test("Multiple files and one explicit stdin source are combined in argument order")
    func combinesFilesAndStandardInput() throws {
        let temporaryDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("cidrmerge-tests-\(UUID().uuidString)")
        try FileManager.default.createDirectory(
            at: temporaryDirectory,
            withIntermediateDirectories: true
        )
        defer { try? FileManager.default.removeItem(at: temporaryDirectory) }

        let first = temporaryDirectory.appendingPathComponent("first.txt")
        let second = temporaryDirectory.appendingPathComponent("second.txt")
        try "192.0.2.0/25\n".write(to: first, atomically: true, encoding: .utf8)
        try "2001:db8::/64\n".write(to: second, atomically: true, encoding: .utf8)

        let pipe = Pipe()
        try pipe.fileHandleForWriting.write(contentsOf: Data("192.0.2.128/25\n".utf8))
        try pipe.fileHandleForWriting.close()

        let collection = try TextInputLoader.load(
            inputs: [first.path, "-", second.path],
            standardInput: pipe.fileHandleForReading
        )
        let result = collection.merged()

        #expect(result.ipv4.descriptions == ["192.0.2.0...192.0.2.255"])
        #expect(result.ipv6.descriptions == ["2001:db8::...2001:db8::ffff:ffff:ffff:ffff"])
    }

    @Test("Repeated stdin is rejected before reading")
    func rejectsRepeatedStandardInput() {
        do {
            _ = try TextInputLoader.load(inputs: ["-", "-"])
            Issue.record("Expected repeated stdin to throw.")
        } catch let error as CIDRMergeError {
            #expect(error == .repeatedStandardInput)
        } catch {
            Issue.record("Unexpected error: \(error)")
        }
    }

    // Lock the deliberate network-free boundary in the public diagnostic.
    @Test("URL input must be downloaded externally")
    func rejectsURLInput() {
        do {
            _ = try TextInputLoader.load(inputs: ["https://example.com/prefixes.txt"])
            Issue.record("Expected URL input to throw.")
        } catch let error as CIDRMergeError {
            #expect(error == .unsupportedURL("https://example.com/prefixes.txt"))
            #expect(
                error.description
                    == "cidrmerge: https://example.com/prefixes.txt: error: URL input is not supported; download it first and pass a local file or stdin"
            )
        } catch {
            Issue.record("Unexpected error: \(error)")
        }
    }

    @Test("Every URL operand is rejected before any local file is opened")
    func prevalidatesURLInputs() {
        do {
            _ = try TextInputLoader.load(inputs: [
                "/definitely/missing/prefixes.txt",
                "https://example.com/prefixes.txt",
            ])
            Issue.record("Expected URL input to throw.")
        } catch let error as CIDRMergeError {
            #expect(error == .unsupportedURL("https://example.com/prefixes.txt"))
        } catch {
            Issue.record("Unexpected error: \(error)")
        }
    }

    @Test("HTTP URL schemes are rejected case-insensitively")
    func rejectsCaseVariantURLSchemes() {
        #expect(throws: CIDRMergeError.unsupportedURL("HTTPS://example.com/prefixes.txt")) {
            try TextInputLoader.load(inputs: ["HTTPS://example.com/prefixes.txt"])
        }
    }
}

@Suite("Output Tests")
struct OutputTests {
    @Test("Default text output is IPv4-first canonical ranges")
    func rendersDeterministicText() throws {
        let result = try mergedResult(
            """
            2001:0DB8::1/32
            192.0.2.129/24
            """
        )

        #expect(
            String(decoding: OutputRenderer.raw(result), as: UTF8.self)
                == """
                192.0.2.0...192.0.2.255
                2001:db8::...2001:db8:ffff:ffff:ffff:ffff:ffff:ffff

                """
        )
    }

    @Test("CIDR text output preserves the existing canonical prefix behavior")
    func rendersDeterministicCIDRText() throws {
        let result = try mergedResult(
            """
            2001:0DB8::1/32
            192.0.2.129/24
            """,
            representation: .cidr
        )

        #expect(
            String(decoding: OutputRenderer.raw(result), as: UTF8.self)
                == """
                192.0.2.0/24
                2001:db8::/32

                """
        )
    }

    @Test("JSON output uses separate deterministic IPv4 and IPv6 arrays")
    func rendersDeterministicJSON() throws {
        let result = try mergedResult(
            """
            2001:db8::/32
            192.0.2.0/24
            """
        )

        #expect(
            String(decoding: try OutputRenderer.json(result), as: UTF8.self)
                == """
                {
                  "ipv4" : [
                    "192.0.2.0...192.0.2.255"
                  ],
                  "ipv6" : [
                    "2001:db8::...2001:db8:ffff:ffff:ffff:ffff:ffff:ffff"
                  ],
                  "representation" : "ranges"
                }

                """
        )
    }

    @Test("Empty JSON output preserves both family arrays")
    func rendersEmptyJSON() throws {
        let result = ParsedInput().merged()

        #expect(
            String(decoding: try OutputRenderer.json(result), as: UTF8.self)
                == """
                {
                  "ipv4" : [

                  ],
                  "ipv6" : [

                  ],
                  "representation" : "ranges"
                }

                """
        )
        #expect(OutputRenderer.raw(result).isEmpty)
    }

    @Test("Statistics include normalization, family totals, and reduction")
    func rendersStatistics() throws {
        let result = try mergedResult(
            """
            192.0.2.1
            192.0.2.0/32
            2001:0DB8::1/128
            """
        )

        #expect(
            String(decoding: OutputRenderer.statistics(result.statistics), as: UTF8.self)
                == """
                input: 3 entries (2 IPv4, 1 IPv6)
                normalized: 2 entries
                output: 2 ranges (1 IPv4, 1 IPv6)
                reduction: 1 entry (33.3%)

                """
        )
    }

    @Test("Statistics report CIDR expansion for an arbitrary range")
    func rendersExpansionStatistics() throws {
        let result = try mergedResult(
            "192.168.1.1...192.168.1.189",
            representation: .cidr
        )

        #expect(
            String(decoding: OutputRenderer.statistics(result.statistics), as: UTF8.self)
                == """
                input: 1 entry (1 IPv4, 0 IPv6)
                normalized: 0 entries
                output: 12 prefixes (12 IPv4, 0 IPv6)
                expansion: 11 entries (1100.0%)

                """
        )
    }

    @Test("Statistics distinguish an unchanged representation count")
    func rendersUnchangedStatistics() throws {
        let result = try mergedResult("192.0.2.1")

        #expect(
            String(decoding: OutputRenderer.statistics(result.statistics), as: UTF8.self)
                == """
                input: 1 entry (1 IPv4, 0 IPv6)
                normalized: 1 entry
                output: 1 range (1 IPv4, 0 IPv6)
                change: unchanged (0.0%)

                """
        )
    }

    @Test("File output replaces its destination only after complete data is available")
    func writesOutputAtomically() throws {
        let outputURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("cidrmerge-output-\(UUID().uuidString).txt")
        defer { try? FileManager.default.removeItem(at: outputURL) }
        try Data("old\n".utf8).write(to: outputURL)

        try CIDRMergeApplication.write(Data("new\n".utf8), to: outputURL.path)

        #expect(try String(contentsOf: outputURL, encoding: .utf8) == "new\n")
    }

    private func mergedResult(
        _ text: String,
        representation: OutputRepresentation = .ranges
    ) throws -> MergeResult {
        try TextInputLoader.load(data: Data(text.utf8)).merged(representation: representation)
    }
}

@Suite("Command Surface Tests")
struct CommandSurfaceTests {
    @Test("Root command exposes orthogonal serialization and representation options")
    func parsesCommandOptions() throws {
        let command = try CIDRMergeCommand.parse([
            "--json",
            "--input-format", "searchbot",
            "--representation", "cidr",
            "--stats",
            "-o", "merged.json",
            "first.txt",
            "-",
            "second.txt",
        ])

        #expect(command.outputFormat == .json)
        #expect(command.inputFormat == .searchbot)
        #expect(command.representation == .cidr)
        #expect(command.stats)
        #expect(command.outputPath == "merged.json")
        #expect(command.inputs == ["first.txt", "-", "second.txt"])
    }

    @Test("Ranges are the default semantic representation")
    func defaultsToRanges() throws {
        let command = try CIDRMergeCommand.parse([])

        #expect(command.representation == .ranges)
        #expect(command.outputFormat == .raw)
        #expect(command.inputFormat == .text)
    }

    @Test("Raw and JSON serialization flags are mutually exclusive")
    func rejectsConflictingOutputFormats() {
        #expect(throws: (any Error).self) {
            try CIDRMergeCommand.parse(["--raw", "--json"])
        }
    }

    @Test("Unknown input formats are rejected")
    func rejectsUnknownInputFormat() {
        #expect(throws: (any Error).self) {
            try CIDRMergeCommand.parse(["--input-format", "auto"])
        }
    }

    @Test("Version metadata is owned by ArgumentParser and -v remains unassigned")
    func exposesVersionMetadata() throws {
        #expect(CIDRMergeCommand.configuration.version == "0.1.0")
        #expect(throws: (any Error).self) {
            try CIDRMergeCommand.parse(["-v"])
        }
    }
}

@Suite("Application Boundary Tests")
struct ApplicationBoundaryTests {
    @Test("The application buffers output and writes statistics after one output commit")
    func commitsOutputBeforeDiagnostics() throws {
        let recorder = ApplicationRecorder()
        let application = CIDRMergeApplication(
            inputLoader: { _, format in
                #expect(format == .searchbot)
                return try TextInputLoader.load(data: Data("192.0.2.0/24\n".utf8))
            },
            outputWriter: { output, path in
                recorder.recordOutput(output, path: path)
            },
            diagnosticWriter: { diagnostics in
                recorder.recordDiagnostics(diagnostics)
            }
        )

        try application.run(
            inputs: ["ignored-by-injected-loader"],
            inputFormat: .searchbot,
            outputFormat: .json,
            representation: .cidr,
            includeStatistics: true,
            outputPath: "merged.json"
        )

        #expect(recorder.outputWriteCount == 1)
        #expect(recorder.outputPath == "merged.json")
        #expect(recorder.outputString.contains(#""representation" : "cidr""#))
        #expect(recorder.diagnosticWriteCount == 1)
        #expect(recorder.diagnosticsString.contains("output: 1 prefix"))
        #expect(recorder.events == ["output", "diagnostics"])
    }

    @Test("An output failure prevents statistics from being emitted")
    func outputFailurePreventsDiagnostics() {
        let recorder = ApplicationRecorder()
        let application = CIDRMergeApplication(
            inputLoader: { _, _ in
                try TextInputLoader.load(data: Data("192.0.2.0/24\n".utf8))
            },
            outputWriter: { _, _ in
                throw ExpectedOutputFailure()
            },
            diagnosticWriter: { diagnostics in
                recorder.recordDiagnostics(diagnostics)
            }
        )

        #expect(throws: ExpectedOutputFailure.self) {
            try application.run(
                inputs: [],
                outputFormat: .raw,
                representation: .ranges,
                includeStatistics: true,
                outputPath: nil
            )
        }
        #expect(recorder.diagnosticWriteCount == 0)
    }

    @Test("An input failure prevents output and statistics from being emitted")
    func inputFailurePreventsWrites() {
        let recorder = ApplicationRecorder()
        let application = CIDRMergeApplication(
            inputLoader: { _, _ in
                throw ExpectedInputFailure()
            },
            outputWriter: { output, path in
                recorder.recordOutput(output, path: path)
            },
            diagnosticWriter: { diagnostics in
                recorder.recordDiagnostics(diagnostics)
            }
        )

        #expect(throws: ExpectedInputFailure.self) {
            try application.run(
                inputs: [],
                inputFormat: .searchbot,
                outputFormat: .raw,
                representation: .ranges,
                includeStatistics: true,
                outputPath: nil
            )
        }
        #expect(recorder.outputWriteCount == 0)
        #expect(recorder.diagnosticWriteCount == 0)
    }
}

private struct ExpectedOutputFailure: Error {}
private struct ExpectedInputFailure: Error {}

private final class ApplicationRecorder: @unchecked Sendable {
    private let lock = NSLock()
    private var recordedEvents: [String] = []
    private var recordedOutput = Data()
    private var recordedOutputPath: String?
    private var recordedDiagnostics = Data()
    private var recordedOutputWriteCount = 0
    private var recordedDiagnosticWriteCount = 0

    var events: [String] {
        lock.withLock { recordedEvents }
    }

    var outputString: String {
        lock.withLock { String(decoding: recordedOutput, as: UTF8.self) }
    }

    var outputPath: String? {
        lock.withLock { recordedOutputPath }
    }

    var diagnosticsString: String {
        lock.withLock { String(decoding: recordedDiagnostics, as: UTF8.self) }
    }

    var outputWriteCount: Int {
        lock.withLock { recordedOutputWriteCount }
    }

    var diagnosticWriteCount: Int {
        lock.withLock { recordedDiagnosticWriteCount }
    }

    func recordOutput(_ output: Data, path: String?) {
        lock.withLock {
            recordedEvents.append("output")
            recordedOutput = output
            recordedOutputPath = path
            recordedOutputWriteCount += 1
        }
    }

    func recordDiagnostics(_ diagnostics: Data) {
        lock.withLock {
            recordedEvents.append("diagnostics")
            recordedDiagnostics = diagnostics
            recordedDiagnosticWriteCount += 1
        }
    }
}
