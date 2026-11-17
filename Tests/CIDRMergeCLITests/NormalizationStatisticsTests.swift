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

@Suite("Optional Normalization Statistics Tests")
struct NormalizationStatisticsTests {
    @Test("Text accounting can be skipped without changing canonical output or cheap counts")
    func textOutputParity() throws {
        let data = Data(
            """
             192.0.2.1 # host
            192.0.3.129/24
            192.0.4.2...192.0.4.7
            2001:DB8::1
            2001:db8:1::123/64
            2001:DB8:2::1...2001:DB8:2::F
            198.51.100.0/24
            2001:db8:3::/64
            """.utf8
        )
        let expected = try TextInputLoader.load(data: data)
        #expect(expected.merged().statistics.normalizedInputCount == 5)
        #expect(expected.merged().statistics.inputCount == 8)
        for collect in [false, true] {
            let actual = try TextInputLoader.load(data: data, collectNormalizationStatistics: collect)
            try expectEquivalentOutput(actual, expected, collecting: collect)
        }
    }

    @Test("Searchbot accounting preserves escaped keys, metadata, and canonical networks")
    func searchbotOutputParity() throws {
        let data = Data(
            #"{"metadata":1,"metadata":2,"prefixes":[{"ipv4Prefix":"192.0.2.129/24"},{"ipv6\u0050refix":"2001:DB8::123/64"},{"ipv4Prefix":"198.51.100.0/24"},{"ipv6Prefix":"2001:db8:1::/64"}]}"#
                .utf8
        )
        let expected = try SearchbotInputLoader.load(data: data)
        #expect(expected.merged().statistics.normalizedInputCount == 2)
        #expect(expected.merged().statistics.inputCount == 4)
        for collect in [false, true] {
            let actual = try SearchbotInputLoader.load(data: data, collectNormalizationStatistics: collect)
            try expectEquivalentOutput(actual, expected, collecting: collect)
        }
    }

    @Test("Text policy reaches file and stdin readers across a split Unicode read boundary")
    func textFileAndStandardInput() throws {
        var data = Data("192.0.2.129/24 #".utf8)
        // CHANGE: Place a multibyte scalar across the fixed read boundary and end without LF.
        data.append(contentsOf: repeatElement(UInt8(ascii: "x"), count: 65_535 - data.count))
        data.append(contentsOf: "é\r\n\u{2003}2001:DB8::1\u{2003}".utf8)
        let expected = try TextInputLoader.load(data: data)
        #expect(expected.merged().statistics.normalizedInputCount == 2)

        try withFile(data) { file in
            for collect in [false, true] {
                let fromFile = try TextInputLoader.load(
                    inputs: [file.path], collectNormalizationStatistics: collect
                )
                let handle = try FileHandle(forReadingFrom: file)
                defer { try? handle.close() }
                let fromStandardInput = try TextInputLoader.load(
                    inputs: ["-"], standardInput: .init(rawValue: handle.fileDescriptor),
                    collectNormalizationStatistics: collect
                )
                try expectEquivalentOutput(fromFile, expected, collecting: collect)
                try expectEquivalentOutput(fromStandardInput, expected, collecting: collect)
            }
        }
    }

    @Test("Searchbot policy reaches file and stdin document decoding")
    func searchbotFileAndStandardInput() throws {
        let data = Data(#"{"prefixes":[{"ipv4Prefix":"192.0.2.129/24"},{"ipv6Prefix":"2001:DB8::123/64"}]}"#.utf8)
        let expected = try SearchbotInputLoader.load(data: data)
        #expect(expected.merged().statistics.normalizedInputCount == 2)

        try withFile(data) { file in
            for collect in [false, true] {
                let handle = try FileHandle(forReadingFrom: file)
                defer { try? handle.close() }
                let actual = try SearchbotInputLoader.load(
                    inputs: [file.path, "-"], standardInput: .init(rawValue: handle.fileDescriptor),
                    collectNormalizationStatistics: collect
                )
                var expectedStatistics = expected.merged().statistics
                expectedStatistics.inputCount *= 2
                expectedStatistics.inputIPv4Count *= 2
                expectedStatistics.inputIPv6Count *= 2
                expectedStatistics.normalizedInputCount = collect ? 4 : 0
                #expect(actual.merged().statistics == expectedStatistics)
                #expect(OutputRenderer.raw(actual.merged()) == OutputRenderer.raw(expected.merged()))
            }
        }
    }

    @Test("Skipping text accounting preserves token errors and UTF-8 error precedence")
    func textDiagnostics() {
        for collect in [false, true] {
            #expect(throws: CIDRMergeError.invalidInput(source: "policy.txt", line: 2, value: "192.0.2.7...192.0.2.2"))
            {
                try TextInputLoader.load(
                    data: Data("192.0.2.129/24\n192.0.2.7...192.0.2.2 # ignored\n".utf8),
                    source: "policy.txt", collectNormalizationStatistics: collect
                )
            }
            let invalid = Data("192.0.2.129/24\nbad # ".utf8) + Data([0xFF, 0x0A])
            #expect(throws: CIDRMergeError.invalidUTF8(source: "policy.txt", line: 2)) {
                try TextInputLoader.load(
                    data: invalid, source: "policy.txt", collectNormalizationStatistics: collect
                )
            }
        }
    }

    @Test("Skipping Searchbot accounting preserves whole-document and schema validation")
    func searchbotDiagnostics() {
        let cases: [(String, String, String)] = [
            (#"{"prefixes":[],"prefixes":[]}"#, "$.prefixes", "duplicate JSON member"),
            (
                #"{"prefixes":[{"ipv4Prefix":"192.0.2.0/24","ipv4\u0050refix":"198.51.100.0/24"}]}"#,
                "$.prefixes[0].ipv4Prefix", "duplicate JSON member"
            ),
            (#"{"prefixes":[{"ipv4Prefix":17}]}"#, "$.prefixes[0].ipv4Prefix", "value has the wrong JSON type"),
            (
                #"{"prefixes":[{"ipv6Prefix":"192.0.2.0/24"}]}"#, "$.prefixes[0].ipv6Prefix",
                "invalid IPv6 network prefix \"192.0.2.0/24\""
            ),
            (#"{"prefixes":[{"ipv4Prefix":"192.0.2.129/24"}]} trailing"#, "$", "malformed JSON"),
        ]
        for collect in [false, true] {
            for (document, path, reason) in cases {
                #expect(throws: CIDRMergeError.invalidSearchbotInput(source: "policy.json", path: path, reason: reason))
                {
                    try SearchbotInputLoader.load(
                        data: Data(document.utf8), source: "policy.json",
                        collectNormalizationStatistics: collect
                    )
                }
            }
            let invalid = Data(#"{"prefixes":[],"metadata":""#.utf8) + Data([0xFF]) + Data(#""}"#.utf8)
            #expect(
                throws: CIDRMergeError.invalidSearchbotInput(
                    source: "policy.json", path: "$", reason: "input is not valid UTF-8")
            ) {
                try SearchbotInputLoader.load(
                    data: invalid, source: "policy.json", collectNormalizationStatistics: collect
                )
            }
        }
    }

    private func expectEquivalentOutput(
        _ actual: ParsedInput, _ expected: ParsedInput, collecting: Bool
    ) throws {
        for representation in [OutputRepresentation.ranges, .cidr] {
            let actualResult = actual.merged(representation: representation)
            let expectedResult = expected.merged(representation: representation)
            var expectedStatistics = expectedResult.statistics
            if !collecting {
                expectedStatistics.normalizedInputCount = 0
            }
            #expect(actualResult.statistics == expectedStatistics)
            #expect(actualResult.ipv4 == expectedResult.ipv4)
            #expect(actualResult.ipv6 == expectedResult.ipv6)
            for format in [OutputFormat.raw, .json] {
                let actualBytes = try OutputRenderer.render(actualResult, format: format)
                let expectedBytes = try OutputRenderer.render(expectedResult, format: format)
                #expect(actualBytes == expectedBytes)
                #expect(
                    try DetachedSHA256Checksum.render(output: actualBytes, outputPath: "policy.txt")
                        == DetachedSHA256Checksum.render(output: expectedBytes, outputPath: "policy.txt")
                )
            }
        }
    }

    private func withFile(_ data: Data, _ body: (URL) throws -> Void) throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent("cidrmerge-normalization-tests-\(UUID().uuidString)")
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }
        let file = directory.appendingPathComponent("input")
        try data.write(to: file)
        try body(file)
    }
}
