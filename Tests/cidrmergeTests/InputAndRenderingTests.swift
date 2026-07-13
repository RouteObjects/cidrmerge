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

@testable import cidrmerge

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

        #expect(result.ipv4.map(\.description) == ["192.0.2.0/24"])
        #expect(result.ipv6.map(\.description) == ["2001:db8::/64"])
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
                    == .invalidPrefix(
                        source: "routes.txt",
                        line: 2,
                        value: "192.0.2.0/33"
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

        #expect(result.ipv4.map(\.description) == ["192.0.2.0/24"])
        #expect(result.ipv6.map(\.description) == ["2001:db8::/64"])
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

    @Test("URL input is reserved for Phase 2")
    func rejectsURLInput() {
        do {
            _ = try TextInputLoader.load(inputs: ["https://example.com/prefixes.txt"])
            Issue.record("Expected URL input to throw.")
        } catch let error as CIDRMergeError {
            #expect(error == .unsupportedURL("https://example.com/prefixes.txt"))
        } catch {
            Issue.record("Unexpected error: \(error)")
        }
    }
}

@Suite("Output Tests")
struct OutputTests {
    @Test("Text output is IPv4 first, IPv6 second, canonical, and newline terminated")
    func rendersDeterministicText() throws {
        let result = try mergedResult(
            """
            2001:0DB8::1/32
            192.0.2.129/24
            """
        )

        #expect(
            String(decoding: OutputRenderer.text(result), as: UTF8.self)
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
            String(decoding: OutputRenderer.json(result), as: UTF8.self)
                == """
                {
                  "ipv4": [
                    "192.0.2.0/24"
                  ],
                  "ipv6": [
                    "2001:db8::/32"
                  ]
                }

                """
        )
    }

    @Test("Empty JSON output preserves both family arrays")
    func rendersEmptyJSON() {
        let result = PrefixCollection().merged()

        #expect(
            String(decoding: OutputRenderer.json(result), as: UTF8.self)
                == """
                {
                  "ipv4": [],
                  "ipv6": []
                }

                """
        )
        #expect(OutputRenderer.text(result).isEmpty)
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
                input: 3 prefixes (2 IPv4, 1 IPv6)
                normalized: 2 prefixes
                output: 2 prefixes (1 IPv4, 1 IPv6)
                reduction: 1 prefix (33.3%)

                """
        )
    }

    @Test("File output replaces its destination only after complete data is available")
    func writesOutputAtomically() throws {
        let outputURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("cidrmerge-output-\(UUID().uuidString).txt")
        defer { try? FileManager.default.removeItem(at: outputURL) }
        try Data("old\n".utf8).write(to: outputURL)

        try CIDRMerge.write(Data("new\n".utf8), to: outputURL.path)

        #expect(try String(contentsOf: outputURL, encoding: .utf8) == "new\n")
    }

    private func mergedResult(_ text: String) throws -> MergeResult {
        try TextInputLoader.load(data: Data(text.utf8)).merged()
    }
}

@Suite("Command Surface Tests")
struct CommandSurfaceTests {
    @Test("Root command exposes the Phase 1 options")
    func parsesPhaseOneOptions() throws {
        let command = try CIDRMerge.parse([
            "--input-format", "text",
            "--output-format", "json",
            "--stats",
            "-o", "merged.json",
            "first.txt",
            "-",
            "second.txt",
        ])

        #expect(command.inputFormat == .text)
        #expect(command.outputFormat == .json)
        #expect(command.stats)
        #expect(command.outputPath == "merged.json")
        #expect(command.inputs == ["first.txt", "-", "second.txt"])
    }

    @Test("--json is mutually exclusive with --output-format")
    func rejectsConflictingOutputFormats() {
        #expect(throws: (any Error).self) {
            try CIDRMerge.parse(["--json", "--output-format", "text"])
        }
    }

    @Test("Long and short version flags are accepted")
    func parsesVersionFlags() throws {
        #expect(try CIDRMerge.parse(["--version"]).showVersion)
        #expect(try CIDRMerge.parse(["-v"]).showVersion)
    }
}
