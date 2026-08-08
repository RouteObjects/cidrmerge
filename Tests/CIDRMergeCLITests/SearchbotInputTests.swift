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

@Suite("Searchbot Input Tests")
struct SearchbotInputTests {
    @Test("A complete mixed-family document ignores vendor metadata and records normalization")
    func acceptsCompleteDocument() throws {
        let parsedInput = try SearchbotInputLoader.load(
            data: fixtureData(named: "searchbot-valid", extension: "json"),
            source: "vendor.json"
        )
        let result = parsedInput.merged()

        #expect(
            String(decoding: OutputRenderer.raw(result), as: UTF8.self)
                == """
                192.0.2.0...192.0.2.3
                2001:db8::...2001:db8::3

                """
        )
        #expect(result.statistics.inputCount == 3)
        #expect(result.statistics.inputIPv4Count == 2)
        #expect(result.statistics.inputIPv6Count == 1)
        #expect(result.statistics.normalizedInputCount == 2)
    }

    @Test("Duplicate unknown metadata remains outside the searchbot contract")
    func ignoresDuplicateUnknownMetadata() throws {
        let parsedInput = try SearchbotInputLoader.load(
            data: Data(
                #"{"metadata":1,"metadata":2,"prefixes":[{"label":"a","label":"b","ipv4Prefix":"192.0.2.0/24"}]}"#.utf8
            ),
            source: "vendor.json"
        )

        #expect(parsedInput.merged().ipv4.descriptions == ["192.0.2.0...192.0.2.255"])
    }

    @Test("An empty prefixes array is the only empty searchbot document")
    func acceptsEmptyPrefixesArray() throws {
        let parsedInput = try SearchbotInputLoader.load(
            data: Data(#"{"prefixes":[]}"#.utf8),
            source: "empty.json"
        )

        #expect(parsedInput.merged().statistics.inputCount == 0)
        #expect(OutputRenderer.raw(parsedInput.merged()).isEmpty)
        #expect(throws: CIDRMergeError.self) {
            try SearchbotInputLoader.load(data: Data(), source: "zero-bytes.json")
        }
    }

    @Test("Every searchbot operand is decoded as one complete document")
    func combinesFilesAndStandardInput() throws {
        let temporaryDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("cidrmerge-searchbot-tests-\(UUID().uuidString)")
        try FileManager.default.createDirectory(
            at: temporaryDirectory,
            withIntermediateDirectories: true
        )
        defer { try? FileManager.default.removeItem(at: temporaryDirectory) }

        let first = temporaryDirectory.appendingPathComponent("first.json")
        let second = temporaryDirectory.appendingPathComponent("second.json")
        try #"{"prefixes":[{"ipv4Prefix":"192.0.2.0/31"}]}"#.write(
            to: first,
            atomically: true,
            encoding: .utf8
        )
        try #"{"prefixes":[{"ipv6Prefix":"2001:db8::/126"}]}"#.write(
            to: second,
            atomically: true,
            encoding: .utf8
        )

        let pipe = Pipe()
        try pipe.fileHandleForWriting.write(
            contentsOf: Data(#"{"prefixes":[{"ipv4Prefix":"192.0.2.2/31"}]}"#.utf8)
        )
        try pipe.fileHandleForWriting.close()

        let parsedInput = try SearchbotInputLoader.load(
            inputs: [first.path, "-", second.path],
            standardInput: pipe.fileHandleForReading
        )
        let result = parsedInput.merged(representation: .cidr)

        #expect(result.ipv4.descriptions == ["192.0.2.0/30"])
        #expect(result.ipv6.descriptions == ["2001:db8::/126"])
        #expect(result.statistics.inputCount == 3)
    }

    @Test("Searchbot and projected text are byte-identical for every output mode")
    func matchesProjectedText() throws {
        let searchbot = try SearchbotInputLoader.load(
            data: fixtureData(named: "searchbot-valid", extension: "json")
        )
        let text = try TextInputLoader.load(
            data: fixtureData(named: "searchbot-projected", extension: "txt")
        )

        for representation in [OutputRepresentation.ranges, .cidr] {
            let searchbotResult = searchbot.merged(representation: representation)
            let textResult = text.merged(representation: representation)

            #expect(searchbotResult.statistics == textResult.statistics)
            #expect(OutputRenderer.raw(searchbotResult) == OutputRenderer.raw(textResult))
            #expect(try OutputRenderer.json(searchbotResult) == OutputRenderer.json(textResult))
        }
    }

    @Test("Schema and prefix failures report stable source and JSON paths")
    func rejectsMalformedDocuments() {
        let cases: [(document: String, path: String, reason: String)] = [
            ("", "$", "malformed JSON"),
            (#"[]"#, "$", "value has the wrong JSON type"),
            (#"{}"#, "$.prefixes", "required value is missing"),
            (#"{"prefixes":{}}"#, "$.prefixes", "value has the wrong JSON type"),
            (#"{"prefixes":[17]}"#, "$.prefixes[0]", "value has the wrong JSON type"),
            (#"{"prefixes":[null]}"#, "$.prefixes[0]", "required value is null"),
            (
                #"{"prefixes":[{}]}"#,
                "$.prefixes[0]",
                "expected exactly one string-valued 'ipv4Prefix' or 'ipv6Prefix'"
            ),
            (
                #"{"prefixes":[{"ipv4Prefix":"192.0.2.0/24","ipv6Prefix":"2001:db8::/32"}]}"#,
                "$.prefixes[0]",
                "expected exactly one string-valued 'ipv4Prefix' or 'ipv6Prefix'"
            ),
            (
                #"{"prefixes":[],"prefixes":[]}"#,
                "$.prefixes",
                "duplicate JSON member"
            ),
            (
                #"{"prefixes":[{"ipv4Prefix":"192.0.2.0/24","ipv4\u0050refix":"198.51.100.0/24"}]}"#,
                "$.prefixes[0].ipv4Prefix",
                "duplicate JSON member"
            ),
            (
                #"{"prefixes":[{"ipv4Prefix":17}]}"#,
                "$.prefixes[0].ipv4Prefix",
                "value has the wrong JSON type"
            ),
            (
                #"{"prefixes":[{"ipv4Prefix":null}]}"#,
                "$.prefixes[0].ipv4Prefix",
                "required value is null"
            ),
            (
                #"{"prefixes":[{"ipv4Prefix":"2001:db8::/32"}]}"#,
                "$.prefixes[0].ipv4Prefix",
                "invalid IPv4 network prefix \"2001:db8::/32\""
            ),
            (
                #"{"prefixes":[{"ipv6Prefix":"192.0.2.0/24"}]}"#,
                "$.prefixes[0].ipv6Prefix",
                "invalid IPv6 network prefix \"192.0.2.0/24\""
            ),
            (
                #"{"prefixes":[{"ipv4Prefix":"192.0.2.1"}]}"#,
                "$.prefixes[0].ipv4Prefix",
                "invalid IPv4 network prefix \"192.0.2.1\""
            ),
            (#"{"prefixes":[]} trailing"#, "$", "malformed JSON"),
        ]

        for testCase in cases {
            do {
                _ = try SearchbotInputLoader.load(
                    data: Data(testCase.document.utf8),
                    source: "vendor.json"
                )
                Issue.record("Expected searchbot input to fail: \(testCase.document)")
            } catch let error as CIDRMergeError {
                #expect(
                    error
                        == .invalidSearchbotInput(
                            source: "vendor.json",
                            path: testCase.path,
                            reason: testCase.reason
                        )
                )
            } catch {
                Issue.record("Unexpected error: \(error)")
            }
        }
    }

    @Test("Searchbot JSON is UTF-8 and has bounded structural nesting")
    func rejectsUnsupportedEncodingAndExcessiveNesting() throws {
        let duplicateDocument =
            #"{"prefixes":[{"ipv4Prefix":"192.0.2.0/24","ipv4Prefix":"198.51.100.0/24"}]}"#
        var utf16Document = Data([0xFF, 0xFE])
        utf16Document.append(
            try #require(duplicateDocument.data(using: .utf16LittleEndian))
        )

        do {
            _ = try SearchbotInputLoader.load(data: utf16Document, source: "utf16.json")
            Issue.record("Expected UTF-16 searchbot input to fail")
        } catch let error as CIDRMergeError {
            #expect(
                error
                    == .invalidSearchbotInput(
                        source: "utf16.json",
                        path: "$",
                        reason: "input is not valid UTF-8"
                    )
            )
        }

        let nestedValue =
            String(repeating: "[", count: 128)
            + "null"
            + String(repeating: "]", count: 128)
        let nestedDocument = #"{"metadata":\#(nestedValue),"prefixes":[]}"#

        do {
            _ = try SearchbotInputLoader.load(
                data: Data(nestedDocument.utf8),
                source: "nested.json"
            )
            Issue.record("Expected excessively nested searchbot input to fail")
        } catch let error as CIDRMergeError {
            #expect(
                error
                    == .invalidSearchbotInput(
                        source: "nested.json",
                        path: "$",
                        reason: "JSON nesting exceeds 128 levels"
                    )
            )
        }
    }

    @Test("Searchbot source preflight preserves the offline and single-stdin boundaries")
    func prevalidatesOperands() {
        #expect(throws: CIDRMergeError.repeatedStandardInput) {
            try SearchbotInputLoader.load(inputs: ["-", "-"])
        }
        #expect(throws: CIDRMergeError.unsupportedURL("HTTPS://example.com/vendor.json")) {
            try SearchbotInputLoader.load(inputs: [
                "/definitely/missing/vendor.json",
                "HTTPS://example.com/vendor.json",
            ])
        }
    }

    private func fixtureData(named name: String, extension fileExtension: String) throws -> Data {
        let url = try #require(Bundle.module.url(forResource: name, withExtension: fileExtension))
        return try Data(contentsOf: url)
    }
}
