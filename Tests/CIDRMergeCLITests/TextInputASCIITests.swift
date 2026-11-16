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

@Suite("ASCII Text Input Tests")
struct TextInputASCIITests {
    @Test("ASCII preparation preserves every input form and normalization count")
    func mixedFormsAndNormalization() throws {
        let data = Data(
            """
             192.0.2.1 # host
            192.0.3.129/24
            192.0.4.2...192.0.4.7
            2001:DB8::1
            2001:db8:1::123/64
            2001:DB8:2::1...2001:DB8:2::F
            """.utf8
        )
        let result = try TextInputLoader.load(data: data).merged()

        #expect(
            result.ipv4.descriptions == [
                "192.0.2.1...192.0.2.1", "192.0.3.0...192.0.3.255",
                "192.0.4.2...192.0.4.7",
            ]
        )
        #expect(
            result.ipv6.descriptions == [
                "2001:db8::1...2001:db8::1",
                "2001:db8:1::...2001:db8:1:0:ffff:ffff:ffff:ffff",
                "2001:db8:2::1...2001:db8:2::f",
            ]
        )
        #expect(result.statistics.inputCount == 6)
        #expect(result.statistics.inputIPv4Count == 3)
        #expect(result.statistics.inputIPv6Count == 3)
        #expect(result.statistics.normalizedInputCount == 5)
    }

    @Test("All ASCII whitespace is accepted at token edges and comments stay ignored")
    func asciiWhitespaceAndComments() throws {
        let whitespace: [UInt8] = [0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x20]
        for byte in whitespace {
            var data = Data([byte])
            data.append(Data("192.0.2.0/24".utf8))
            data.append(contentsOf: [byte, 0x0A])
            let result = try TextInputLoader.load(data: data).merged()
            #expect(result.ipv4.descriptions == ["192.0.2.0...192.0.2.255"])
            #expect(result.statistics.inputCount == 1)
            #expect(result.statistics.normalizedInputCount == 0)
        }

        let result = try TextInputLoader.load(
            data: Data("\t# comment\0\u{7F}\r\n \t\u{B}\u{C}\r\n192.0.2.0/24## ignored / ...\n".utf8)
        ).merged()
        #expect(result.statistics.inputCount == 1)
        #expect(result.statistics.normalizedInputCount == 0)
    }

    @Test("Other ASCII control bytes are preserved in invalid-token diagnostics")
    func rejectsOtherASCIIControls() {
        let controls = Array(UInt8(0)...UInt8(31)) + [UInt8(127)]
        for byte in controls where !(0x09...0x0D).contains(byte) {
            let tokenBytes = [byte] + Array("192.0.2.1".utf8) + [byte]
            let token = String(decoding: tokenBytes, as: UTF8.self)
            expectInvalidToken(Data(tokenBytes + [0x0A]), value: token)
        }
    }

    @Test("Unicode edge whitespace and ordinary Unicode comments retain fallback behavior")
    func unicodeWhitespaceAndComments() throws {
        let result = try TextInputLoader.load(
            data: Data("\u{A0}\u{2003}\u{2028}192.0.2.0/24\u{2029}\u{3000} # café 🌍\n".utf8)
        ).merged()
        #expect(result.ipv4.descriptions == ["192.0.2.0...192.0.2.255"])
        #expect(result.statistics.normalizedInputCount == 0)

        let empty = try TextInputLoader.load(data: Data("# café\n\u{A0}\u{2003}\n".utf8)).merged()
        #expect(empty.statistics.inputCount == 0)
    }

    @Test("A hash in a combined Character is not an ordinary comment separator")
    func characterCommentBoundaries() {
        // CHANGE: A byte-level hash search must not change the legacy Character-based split.
        for token in [
            "192.0.2.1 #\u{301} comment",
            "192.0.2.1 #\u{FE0F}\u{20E3} comment",
            "#\u{301} comment",
        ] {
            expectInvalidToken(Data((token + "\n").utf8), value: token)
        }
    }

    @Test("Whole-line UTF-8 validation precedes comment stripping and token validation")
    func invalidUTF8Precedence() {
        let invalidLines: [[UInt8]] = [
            [0xFF],
            Array("# ".utf8) + [0xFF],
            Array("192.0.2.1 # ".utf8) + [0xFF],
            Array("bad # ".utf8) + [0xC3, 0x28],
            Array("192.0.2.1 # ".utf8) + [0xED, 0xA0, 0x80],
            Array("192.0.2.1 # ".utf8) + [0xF0, 0x90],
        ]
        for invalidLine in invalidLines {
            let data = Data(Array("192.0.2.0/24\n".utf8) + invalidLine + [0x0A])
            #expect(throws: CIDRMergeError.invalidUTF8(source: "ascii.txt", line: 2)) {
                try TextInputLoader.load(data: data, source: "ascii.txt")
            }
        }
    }

    @Test("BOM handling keeps the existing Foundation decoding behavior")
    func byteOrderMarks() throws {
        let bom = Data([0xEF, 0xBB, 0xBF])
        let empty = try TextInputLoader.load(data: bom).merged()
        #expect(empty.statistics.inputCount == 0)

        let firstLine = try TextInputLoader.load(data: bom + Data("192.0.2.1\r\n".utf8)).merged()
        #expect(firstLine.ipv4.descriptions == ["192.0.2.1...192.0.2.1"])
        #expect(firstLine.statistics.inputCount == 1)
        #expect(firstLine.statistics.normalizedInputCount == 1)

        // CHANGE: Foundation versions differ on whether strict decoding consumes a BOM.
        // After the loader's one explicit first-line removal, preserve that decoder behavior.
        let decoded = try #require(String(bytes: Array(bom + Data("192.0.2.1".utf8)), encoding: .utf8))
        try #require(decoded == "192.0.2.1" || decoded == "\u{FEFF}192.0.2.1")
        for (data, line) in [
            (bom + bom + Data("192.0.2.1".utf8), 1),
            (Data("# first line\n".utf8) + bom + Data("192.0.2.1\n".utf8), 2),
        ] {
            try withFile(data) { path in
                if decoded == "192.0.2.1" {
                    for collection in [
                        try TextInputLoader.load(data: data, source: path),
                        try TextInputLoader.load(inputs: [path]),
                    ] {
                        let result = collection.merged()
                        #expect(result.ipv4.descriptions == ["192.0.2.1...192.0.2.1"])
                        #expect(result.statistics.inputCount == 1)
                        #expect(result.statistics.normalizedInputCount == 1)
                    }
                } else {
                    let expected = CIDRMergeError.invalidInput(
                        source: path, line: line, value: "\u{FEFF}192.0.2.1"
                    )
                    #expect(throws: expected) { try TextInputLoader.load(data: data, source: path) }
                    #expect(throws: expected) { try TextInputLoader.load(inputs: [path]) }
                }
            }
        }

        expectInvalidToken(
            Data(" \u{FEFF}192.0.2.1\n".utf8), value: "\u{FEFF}192.0.2.1"
        )
        expectInvalidToken(
            Data("192.0.2.\u{FEFF}1\n".utf8), value: "192.0.2.\u{FEFF}1"
        )
    }

    @Test("CRLF, repeated trailing CR, empty lines and final EOF preserve line handling")
    func lineEndingsAndEOF() throws {
        for text in ["192.0.2.0/24", "192.0.2.0/24\r", "\n192.0.2.0/24\r\r\r\n\n"] {
            let result = try TextInputLoader.load(data: Data(text.utf8)).merged()
            #expect(result.statistics.inputCount == 1)
            #expect(result.statistics.normalizedInputCount == 0)
        }
        for text in ["", "\n", "\r", "\r\r\n\n", "# final comment"] {
            let result = try TextInputLoader.load(data: Data(text.utf8)).merged()
            #expect(result.statistics.inputCount == 0)
        }
    }

    @Test("Malformed tokens preserve complete values regardless of delimiter ordering")
    func invalidTokenContext() {
        for token in [
            "192.0.2.0/24 64496",
            "192.0.2.1...192.0.2.2/32",
            "192.0.2.1/32...192.0.2.2",
            "192.0.2.1 ...192.0.2.2",
            "2001:db8::1\t2001:db8::2",
            "192.0.2.1\u{A0}192.0.2.2",
        ] {
            expectInvalidToken(
                Data(("# first\n \t" + token + " \t# comment\r\n").utf8),
                line: 2,
                value: token
            )
        }
    }

    @Test("Invalid-input text renders the original source, logical line and escaped token")
    func exactDiagnosticRendering() {
        do {
            _ = try TextInputLoader.load(
                data: Data("# first\n \tbad\tvalue # ignored\r\n".utf8), source: "ascii.txt"
            )
            Issue.record("Expected invalid input")
        } catch let error as CIDRMergeError {
            #expect(error == .invalidInput(source: "ascii.txt", line: 2, value: "bad\tvalue"))
            #expect(
                error.description
                    == "cidrmerge: ascii.txt:2: error: invalid IP address, network, or range \"bad\\tvalue\""
            )
        } catch {
            Issue.record("Unexpected error: \(error)")
        }
    }

    @Test("File and Data loading agree when CRLF or Unicode crosses a read boundary")
    func fileReadBoundaryParity() throws {
        let prefix = Array("192.0.2.0/24 #".utf8)
        let crlfBoundary = Data(
            prefix + Array(repeating: UInt8(ascii: "x"), count: 65_535 - prefix.count)
                + Array("\r\n2001:db8::/32".utf8)
        )
        let unicodeBoundary = Data(
            prefix + Array(repeating: UInt8(ascii: "x"), count: 65_535 - prefix.count)
                + Array("é\n2001:db8::/32\n".utf8)
        )
        for data in [crlfBoundary, unicodeBoundary] {
            try withFile(data) { path in
                let memory = try TextInputLoader.load(data: data, source: path)
                let file = try TextInputLoader.load(inputs: [path])
                for representation in [OutputRepresentation.ranges, .cidr] {
                    let expected = memory.merged(representation: representation)
                    let actual = file.merged(representation: representation)
                    #expect(actual.statistics == expected.statistics)
                    #expect(OutputRenderer.raw(actual) == OutputRenderer.raw(expected))
                    #expect(try OutputRenderer.json(actual) == OutputRenderer.json(expected))
                    #expect(actual.statistics.inputCount == 2)
                    #expect(actual.statistics.normalizedInputCount == 0)
                }
            }
        }
    }

    @Test("Invalid comment bytes beyond a file read boundary retain UTF-8 diagnostics")
    func fileReadBoundaryInvalidUTF8() throws {
        var data = Data("192.0.2.0/24\n#".utf8)
        data.append(contentsOf: repeatElement(UInt8(ascii: "x"), count: 65_536))
        data.append(contentsOf: [0xFF, 0x0A])
        try withFile(data) { path in
            let expected = CIDRMergeError.invalidUTF8(source: path, line: 2)
            #expect(throws: expected) { try TextInputLoader.load(data: data, source: path) }
            #expect(throws: expected) { try TextInputLoader.load(inputs: [path]) }
        }
    }

    private func expectInvalidToken(_ data: Data, line: Int = 1, value: String) {
        #expect(throws: CIDRMergeError.invalidInput(source: "ascii.txt", line: line, value: value)) {
            try TextInputLoader.load(data: data, source: "ascii.txt")
        }
    }

    private func withFile(_ data: Data, body: (String) throws -> Void) throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent("cidrmerge-ascii-tests-\(UUID().uuidString)")
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }
        let file = directory.appendingPathComponent("input.txt")
        try data.write(to: file)
        try body(file.path)
    }
}
