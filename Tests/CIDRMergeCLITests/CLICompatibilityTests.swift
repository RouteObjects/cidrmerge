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
import SystemPackage
import Testing

@testable import CIDRMergeCLI

#if canImport(Darwin)
    import Darwin
#endif

@Suite("Foundation compatibility tests")
struct CLICompatibilityTests {
    @Test("Unicode boundary trimming preserves the Foundation scalar set and graphemes")
    func boundaryWhitespace() {
        let boundaryScalars: [UInt32] = [
            0x0009, 0x000A, 0x000B, 0x000C, 0x000D, 0x0020, 0x0085, 0x00A0, 0x1680,
            0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2007, 0x2008,
            0x2009, 0x200A, 0x200B, 0x2028, 0x2029, 0x202F, 0x205F, 0x3000,
            0x0000, 0x001C, 0x180E, 0x200C, 0x2060, 0xFEFF,
        ]
        for scalarValue in boundaryScalars {
            let boundary = String(Unicode.Scalar(scalarValue)!)
            for token in ["", "192.0.2.0/24", "2001:db8::1", "\u{0301}192.0.2.0/24", "#\u{20E3}"] {
                let text = boundary + token + boundary
                #expect(
                    CLICompatibility.trimBoundaryWhitespace(text[...])
                        == text.trimmingCharacters(in: .whitespacesAndNewlines)
                )
            }
        }
        for text in [" \u{0301}192.0.2.0/24 ", "\u{200B}\u{0301} \u{200B}", "x \u{0301}", " \u{0301}"] {
            #expect(
                CLICompatibility.trimBoundaryWhitespace(text[...])
                    == text.trimmingCharacters(in: .whitespacesAndNewlines)
            )
        }
    }

    @Test("Percentages preserve decimal ties, adjacent Doubles, and large count ratios")
    func percentages() {
        let locale = Locale(identifier: "en_US_POSIX")
        func check(_ magnitude: Double) {
            #expect(
                CLICompatibility.percentage(magnitude)
                    == String(format: "%.1f%%", locale: locale, magnitude)
            )
        }
        check(0)
        for magnitude in [0.05, 0.15, 6.25, 6.35, 9.95, 12.25, 99.95, Double(Int.max) * 100] {
            check(magnitude.nextDown)
            check(magnitude)
            check(magnitude.nextUp)
        }
        let counts = [1, 2, 3, 7, 9, 10, 11, 100, 1_000, 999_999, 1_000_000, Int.max / 2, Int.max - 1, Int.max]
        for input in counts {
            for output in counts {
                check(abs(Double(output - input)) / Double(input) * 100)
            }
        }
        for input in 1...50 {
            for output in 0...100 {
                check(abs(Double(output - input)) / Double(input) * 100)
            }
        }
    }

    @Test("Error descriptions preserve Cocoa reasons and explicit overrides")
    func cocoaErrorDescriptions() {
        let codes = [
            4, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 512, 513, 514, 516, 517,
            518, 640, 642, 1024, 2048, 3072, 3328, 3840, 3841, 3842, 3851, 3852, 4353,
            4354, 4355, 4864, 4865, 4866, 999_999,
        ]
        for code in codes {
            let error = CocoaError(CocoaError.Code(rawValue: code))
            #expect(CLICompatibility.errorDescription(error) == error.localizedDescription)
        }
        for userInfo: [String: Any] in [
            [NSLocalizedDescriptionKey: "Explicit description."],
            [NSLocalizedFailureReasonErrorKey: "Explicit failure reason."],
            [NSLocalizedDescriptionKey: "Description wins.", NSLocalizedFailureReasonErrorKey: "Ignored."],
        ] {
            let error = CocoaError(.fileReadUnknown, userInfo: userInfo)
            #expect(CLICompatibility.errorDescription(error) == error.localizedDescription)
        }
    }

    @Test("Injected errors preserve LocalizedError and arbitrary enum fallback codes")
    func injectedErrorDescriptions() {
        let errors: [any Error] = [
            CompatibilityPlainError(),
            CompatibilityEnumError.first,
            CompatibilityEnumError.associated(42),
            CompatibilityEnumError.last,
            CompatibilityLocalizedError(description: "Injected description.", reason: "Ignored."),
            CompatibilityLocalizedError(description: nil, reason: "Injected failure reason."),
            CompatibilityLocalizedError(description: nil, reason: nil),
            POSIXError(.EBADF),
            POSIXError(.EACCES),
        ]
        for error in errors {
            #expect(CLICompatibility.errorDescription(error) == error.localizedDescription)
        }
    }

    @Test("Descriptor open failures preserve FileHandle diagnostics")
    func descriptorOpenErrors() throws {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: false)
        defer { try? FileManager.default.removeItem(at: directory) }
        let regularFile = directory.appendingPathComponent("regular-file")
        try Data("fixture".utf8).write(to: regularFile)
        let unreadableFile = directory.appendingPathComponent("unreadable-file")
        try Data("fixture".utf8).write(to: unreadableFile)
        try FileManager.default.setAttributes([.posixPermissions: 0], ofItemAtPath: unreadableFile.path)
        defer { try? FileManager.default.setAttributes([.posixPermissions: 0o600], ofItemAtPath: unreadableFile.path) }
        for url in [
            directory.appendingPathComponent("missing-parent/input.txt"),
            regularFile.appendingPathComponent("child"),
            directory.appendingPathComponent(String(repeating: "x", count: 300)),
            unreadableFile,
        ] {
            let baselineError: any Error
            do {
                let handle = try FileHandle(forReadingFrom: url)
                try handle.close()
                // A privileged Linux test process can read a file with no permission bits.
                continue
            } catch {
                baselineError = error
            }
            do {
                let descriptor = try DescriptorIO.openForReading(url.path)
                try descriptor.close()
                Issue.record("Expected the descriptor open to fail.")
            } catch {
                #expect(CLICompatibility.errorDescription(error) == baselineError.localizedDescription)
            }
        }
    }

    @Test("Darwin directory diagnostics preserve inherited errno and relative path context")
    func relativeDescriptorPath() throws {
        #if canImport(Darwin)
            let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
            try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: false)
            defer { try? FileManager.default.removeItem(at: directory) }
            let currentComponents = URL(fileURLWithPath: FileManager.default.currentDirectoryPath).pathComponents.count
            let relativePath = String(repeating: "../", count: currentComponents) + directory.path.dropFirst()
            for path in [directory.path, relativePath] {
                for inheritedErrno: Int32 in [0, EPERM, ENOENT, EBADF, EACCES, EISDIR, ENOSPC] {
                    var baselineError: (any Error)?
                    errno = inheritedErrno
                    do {
                        let handle = try FileHandle(forReadingFrom: URL(fileURLWithPath: path))
                        try handle.close()
                    } catch { baselineError = error }
                    let expected = try #require(baselineError)
                    errno = inheritedErrno
                    do {
                        let descriptor = try DescriptorIO.openForReading(path)
                        try descriptor.close()
                        Issue.record("Expected a directory descriptor open to fail on Darwin.")
                    } catch {
                        #expect(CLICompatibility.errorDescription(error) == expected.localizedDescription)
                    }
                }
            }
        #endif
    }

    @Test("Invalid descriptor read and write preserve FileHandle diagnostics")
    func descriptorReadAndWriteErrors() throws {
        let handle = FileHandle(fileDescriptor: -1, closeOnDealloc: false)
        var readError: (any Error)?
        do { _ = try handle.read(upToCount: 1) } catch { readError = error }
        let expectedRead = try #require(readError)
        withUnsafeTemporaryAllocation(byteCount: 1, alignment: 1) { buffer in
            do {
                _ = try DescriptorIO.read(from: FileDescriptor(rawValue: -1), into: buffer)
                Issue.record("Expected the descriptor read to fail.")
            } catch {
                #expect(CLICompatibility.errorDescription(error) == expectedRead.localizedDescription)
            }
        }
        var writeError: (any Error)?
        do { try handle.write(contentsOf: Data([0x41])) } catch { writeError = error }
        let expectedWrite = try #require(writeError)
        do {
            try DescriptorIO.write(Data([0x41]), to: FileDescriptor(rawValue: -1))
            Issue.record("Expected the descriptor write to fail.")
        } catch {
            #expect(CLICompatibility.errorDescription(error) == expectedWrite.localizedDescription)
        }
    }
}

private struct CompatibilityPlainError: Error {}

private enum CompatibilityEnumError: Error {
    case first
    case associated(Int)
    case last
}

private struct CompatibilityLocalizedError: Error, LocalizedError {
    let description: String?
    let reason: String?
    var errorDescription: String? { description }
    var failureReason: String? { reason }
}
