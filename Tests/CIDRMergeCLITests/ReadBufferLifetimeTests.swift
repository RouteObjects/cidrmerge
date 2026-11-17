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

@Suite("Read Buffer Lifetime Tests")
struct ReadBufferLifetimeTests {
    @Test("Pending lines and parsed values survive several chunk boundaries")
    func longLineAndFinalToken() throws {
        var data = Data("192.0.2.129/24 #".utf8)
        // CHANGE: Split a Unicode scalar after three complete reads, then finish without LF.
        data.append(contentsOf: repeatElement(UInt8(ascii: "x"), count: 3 * 65_536 - 1 - data.count))
        data.append(contentsOf: "é\r\n2001:DB8::1".utf8)

        try withDirectory { directory in
            let file = directory.appendingPathComponent("long.txt")
            try data.write(to: file)
            let memory = try TextInputLoader.load(data: data, source: file.path)
            let streamed = try TextInputLoader.load(inputs: [file.path])
            for representation in [OutputRepresentation.ranges, .cidr] {
                let expected = memory.merged(representation: representation)
                let actual = streamed.merged(representation: representation)
                #expect(actual.statistics == expected.statistics)
                #expect(actual.statistics.inputCount == 2)
                #expect(actual.statistics.normalizedInputCount == 2)
                #expect(OutputRenderer.raw(actual) == OutputRenderer.raw(expected))
                #expect(try OutputRenderer.json(actual) == OutputRenderer.json(expected))
            }
        }
    }

    @Test("Repeated and empty sources retain separate BOM and EOF handling")
    func repeatedSourcesAndEOF() throws {
        try withDirectory { directory in
            let first = directory.appendingPathComponent("first.txt")
            let empty = directory.appendingPathComponent("empty.txt")
            let second = directory.appendingPathComponent("second.txt")
            try Data("\u{FEFF}192.0.2.129/24\r".utf8).write(to: first)
            try Data().write(to: empty)
            try Data("\u{FEFF}2001:DB8::1".utf8).write(to: second)

            let result = try TextInputLoader.load(
                inputs: [first.path, empty.path, first.path, second.path]
            ).merged()
            #expect(result.statistics.inputCount == 3)
            #expect(result.statistics.inputIPv4Count == 2)
            #expect(result.statistics.inputIPv6Count == 1)
            #expect(result.statistics.normalizedInputCount == 3)
            #expect(result.statistics.outputCount == 2)
            #expect(result.ipv4.descriptions == ["192.0.2.0...192.0.2.255"])
            #expect(result.ipv6.descriptions == ["2001:db8::1...2001:db8::1"])
        }
    }

    @Test("FileHandle read failures preserve the stdin source and underlying reason")
    func readFailurePreservesSource() throws {
        try withDirectory { directory in
            let file = directory.appendingPathComponent("write-only.txt")
            try Data("192.0.2.0/24\n".utf8).write(to: file)
            let handle = try FileHandle(forWritingTo: file)
            defer { try? handle.close() }

            do {
                _ = try TextInputLoader.load(inputs: ["-"], standardInput: .init(rawValue: handle.fileDescriptor))
                Issue.record("Expected reading a write-only handle to fail")
            } catch let error as CIDRMergeError {
                guard case .inputReadFailed(let source, let reason) = error else {
                    Issue.record("Unexpected input error: \(error)")
                    return
                }
                #expect(source == InputSources.standardInputLabel)
                #expect(!reason.isEmpty)
            } catch {
                Issue.record("Unexpected error type: \(error)")
            }
        }
    }

    private func withDirectory(_ body: (URL) throws -> Void) throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent("cidrmerge-read-buffer-tests-\(UUID().uuidString)")
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }
        try body(directory)
    }
}
