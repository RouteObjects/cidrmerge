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

import CIDR
import Foundation

enum CIDRMergeError: Error, Equatable, CustomStringConvertible {
    case invalidInput(source: String, line: Int, value: String)
    case invalidUTF8(source: String, line: Int)
    case inputReadFailed(source: String, reason: String)
    case outputWriteFailed(destination: String, reason: String)
    case repeatedStandardInput
    case unsupportedURL(String)

    var description: String {
        switch self {
        case .invalidInput(let source, let line, let value):
            return
                "cidrmerge: \(source):\(line): error: invalid IP address, network, or range \(String(reflecting: value))"
        case .invalidUTF8(let source, let line):
            return "cidrmerge: \(source):\(line): error: input is not valid UTF-8"
        case .inputReadFailed(let source, let reason):
            return "cidrmerge: \(source): error: unable to read input: \(reason)"
        case .outputWriteFailed(let destination, let reason):
            return "cidrmerge: \(destination): error: unable to write output: \(reason)"
        case .repeatedStandardInput:
            return "cidrmerge: error: standard input '-' may appear at most once"
        case .unsupportedURL(let value):
            // Keep network acquisition outside the deterministic merge path.
            let guidance = "download it first and pass a local file or stdin"
            return "cidrmerge: \(value): error: URL input is not supported; \(guidance)"
        }
    }
}

enum TextInputLoader {
    private static let standardInputLabel = "<stdin>"
    private static let chunkSize = 64 * 1_024
    private static let utf8ByteOrderMark: [UInt8] = [0xEF, 0xBB, 0xBF]

    static func load(
        inputs: [String],
        standardInput: FileHandle = .standardInput
    ) throws -> ParsedInput {
        let sources = inputs.isEmpty ? ["-"] : inputs
        guard sources.lazy.filter({ $0 == "-" }).count <= 1 else {
            throw CIDRMergeError.repeatedStandardInput
        }
        // Reject every unsupported URL before opening any earlier local-file operand.
        if let source = sources.first(where: isHTTPURL) {
            throw CIDRMergeError.unsupportedURL(source)
        }

        var collection = ParsedInput()
        for source in sources {
            if source == "-" {
                try consume(
                    standardInput,
                    source: standardInputLabel,
                    into: &collection
                )
                continue
            }

            let handle: FileHandle
            do {
                handle = try FileHandle(forReadingFrom: URL(fileURLWithPath: source))
            } catch {
                throw CIDRMergeError.inputReadFailed(
                    source: source,
                    reason: error.localizedDescription
                )
            }
            defer { try? handle.close() }

            try consume(handle, source: source, into: &collection)
        }

        return collection
    }

    static func load(data: Data, source: String = "<memory>") throws -> ParsedInput {
        var collection = ParsedInput()
        var pending: [UInt8] = []
        pending.reserveCapacity(128)
        var lineNumber = 1

        for byte in data {
            if byte == 0x0A {
                try consumeLine(
                    pending,
                    source: source,
                    lineNumber: lineNumber,
                    into: &collection
                )
                pending.removeAll(keepingCapacity: true)
                lineNumber += 1
            } else {
                pending.append(byte)
            }
        }

        if !pending.isEmpty {
            try consumeLine(
                pending,
                source: source,
                lineNumber: lineNumber,
                into: &collection
            )
        }

        return collection
    }

    private static func consume(
        _ handle: FileHandle,
        source: String,
        into collection: inout ParsedInput
    ) throws {
        var pending: [UInt8] = []
        pending.reserveCapacity(128)
        var lineNumber = 1

        do {
            while let data = try handle.read(upToCount: chunkSize), !data.isEmpty {
                for byte in data {
                    if byte == 0x0A {
                        try consumeLine(
                            pending,
                            source: source,
                            lineNumber: lineNumber,
                            into: &collection
                        )
                        pending.removeAll(keepingCapacity: true)
                        lineNumber += 1
                    } else {
                        pending.append(byte)
                    }
                }
            }

            if !pending.isEmpty {
                try consumeLine(
                    pending,
                    source: source,
                    lineNumber: lineNumber,
                    into: &collection
                )
            }
        } catch let error as CIDRMergeError {
            throw error
        } catch {
            throw CIDRMergeError.inputReadFailed(
                source: source,
                reason: error.localizedDescription
            )
        }
    }

    private static func consumeLine(
        _ rawBytes: [UInt8],
        source: String,
        lineNumber: Int,
        into collection: inout ParsedInput
    ) throws {
        var bytes = rawBytes
        if bytes.last == 0x0D {
            bytes.removeLast()
        }
        if lineNumber == 1, bytes.starts(with: utf8ByteOrderMark) {
            bytes.removeFirst(utf8ByteOrderMark.count)
        }

        guard let line = String(bytes: bytes, encoding: .utf8) else {
            throw CIDRMergeError.invalidUTF8(source: source, line: lineNumber)
        }

        let uncommented =
            line.split(
                separator: "#",
                maxSplits: 1,
                omittingEmptySubsequences: false
            ).first ?? ""
        let token = uncommented.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !token.isEmpty else { return }

        let range: AnyIPAddressRange
        let normalized: Bool
        switch inputKind(of: token) {
        case .network:
            guard let parsed = AnyIPNetwork(token) else {
                throw CIDRMergeError.invalidInput(
                    source: source,
                    line: lineNumber,
                    value: token
                )
            }
            range = AnyIPAddressRange(covering: parsed)
            normalized = parsed.description != token
        case .range:
            guard let parsed = AnyIPAddressRange(token) else {
                throw CIDRMergeError.invalidInput(
                    source: source,
                    line: lineNumber,
                    value: token
                )
            }
            range = parsed
            normalized = parsed.description != token
        case .address:
            guard let address = AnyIPAddress(token) else {
                throw CIDRMergeError.invalidInput(
                    source: source,
                    line: lineNumber,
                    value: token
                )
            }
            range = AnyIPAddressRange(address)
            normalized = address.description != token
        }

        // Compare after comment/whitespace removal so stats count semantic canonicalization only.
        collection.append(range, normalized: normalized)
    }

    private static func inputKind(of token: String) -> InputTokenKind {
        var consecutiveDots = 0
        // Classify each line in one UTF-8 pass so prefix-heavy and range-heavy data sets do
        // not pay for separate full-string delimiter searches.
        for byte in token.utf8 {
            switch byte {
            case 0x2F:
                return .network
            case 0x2E:
                consecutiveDots += 1
                if consecutiveDots == 3 {
                    return .range
                }
            default:
                consecutiveDots = 0
            }
        }
        return .address
    }

    private static func isHTTPURL(_ source: String) -> Bool {
        let normalized = source.prefix(8).lowercased()
        return normalized.hasPrefix("http://") || normalized.hasPrefix("https://")
    }
}

private enum InputTokenKind {
    case address
    case network
    case range
}
