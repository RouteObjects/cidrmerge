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

import CIDR
import Foundation

/// Loads the crawler-prefix JSON grammar currently used by Google, Bing, Apple, and OpenAI.
///
/// Each operand is one complete UTF-8 document read from a local file or the one permitted
/// standard-input source. A document contains a top-level `prefixes` array whose entries each
/// select exactly one string-valued `ipv4Prefix` or `ipv6Prefix`. Unknown metadata is tolerated,
/// while policy-bearing duplicate members are rejected before Foundation can collapse them.
///
/// Accepted networks are parsed and canonicalized by swift-cidr, then projected to exact address
/// ranges for merging. Loading returns only after every operand succeeds, preserving fail-atomic
/// process output. This type does not download data, authenticate its source, verify crawler
/// identity, or assign allow/deny admission roles.
enum SearchbotInputLoader {
    static func load(
        inputs: [String],
        standardInput: FileHandle = .standardInput
    ) throws -> ParsedInput {
        let sources = try InputSources.validated(inputs)
        var parsedInput = ParsedInput()

        for source in sources {
            let label = source == "-" ? InputSources.standardInputLabel : source
            let data = try read(source: source, label: label, standardInput: standardInput)
            try decode(data, source: label, into: &parsedInput)
        }

        return parsedInput
    }

    static func load(data: Data, source: String = "<memory>") throws -> ParsedInput {
        var parsedInput = ParsedInput()
        try decode(data, source: source, into: &parsedInput)
        return parsedInput
    }

    private static func read(
        source: String,
        label: String,
        standardInput: FileHandle
    ) throws -> Data {
        do {
            if source == "-" {
                return try standardInput.readToEnd() ?? Data()
            }
            return try Data(contentsOf: URL(fileURLWithPath: source))
        } catch {
            throw CIDRMergeError.inputReadFailed(
                source: label,
                reason: error.localizedDescription
            )
        }
    }

    private static func decode(
        _ data: Data,
        source: String,
        into parsedInput: inout ParsedInput
    ) throws {
        guard String(data: data, encoding: .utf8) != nil else {
            throw CIDRMergeError.invalidSearchbotInput(
                source: source,
                path: "$",
                reason: "input is not valid UTF-8"
            )
        }
        if let issue = SearchbotJSONPreflight.validationIssue(in: data) {
            throw CIDRMergeError.invalidSearchbotInput(
                source: source,
                path: issue.path,
                reason: issue.reason
            )
        }

        let document: SearchbotDocument
        do {
            // CHANGE: Searchbot operands are complete documents by contract. Decoding the whole
            // value also rejects malformed or trailing JSON before any output can be committed.
            document = try JSONDecoder().decode(SearchbotDocument.self, from: data)
        } catch let issue as SearchbotDecodingIssue {
            throw CIDRMergeError.invalidSearchbotInput(
                source: source,
                path: issue.path,
                reason: issue.reason
            )
        } catch let error as DecodingError {
            let diagnostic = decodingDiagnostic(for: error)
            throw CIDRMergeError.invalidSearchbotInput(
                source: source,
                path: diagnostic.path,
                reason: diagnostic.reason
            )
        } catch {
            throw CIDRMergeError.invalidSearchbotInput(
                source: source,
                path: "$",
                reason: "malformed JSON"
            )
        }

        for prefix in document.prefixes {
            parsedInput.append(prefix.range, normalized: prefix.normalized)
        }
    }

    private static func decodingDiagnostic(
        for error: DecodingError
    ) -> (path: String, reason: String) {
        switch error {
        case .keyNotFound(let key, let context):
            return (
                codingPath(context.codingPath, appending: key),
                "required value is missing"
            )
        case .typeMismatch(_, let context):
            return (codingPath(context.codingPath), "value has the wrong JSON type")
        case .valueNotFound(_, let context):
            return (codingPath(context.codingPath), "required value is null")
        case .dataCorrupted(let context):
            return (codingPath(context.codingPath), "malformed JSON")
        @unknown default:
            return ("$", "malformed JSON")
        }
    }
}

/// The policy-bearing projection of one compatible crawler-prefix document.
///
/// Synthesized decoding requires the `prefixes` member while intentionally ignoring descriptive
/// fields such as `creationTime`. Prefix validation and swift-cidr conversion are delegated to
/// `SearchbotPrefix`.
private struct SearchbotDocument: Decodable {
    let prefixes: [SearchbotPrefix]
}

private struct SearchbotPrefix: Decodable {
    let range: AnyIPAddressRange
    let normalized: Bool

    private enum CodingKeys: String, CodingKey {
        case ipv4Prefix
        case ipv6Prefix
    }

    init(from decoder: any Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        let hasIPv4 = container.contains(.ipv4Prefix)
        let hasIPv6 = container.contains(.ipv6Prefix)

        // CHANGE: `contains` distinguishes an absent key from an explicitly null key, ensuring
        // null is diagnosed as a wrong value instead of being mistaken for an omitted family.
        guard hasIPv4 != hasIPv6 else {
            throw SearchbotDecodingIssue(
                path: codingPath(decoder.codingPath),
                reason: "expected exactly one string-valued 'ipv4Prefix' or 'ipv6Prefix'"
            )
        }

        if hasIPv4 {
            let value = try container.decode(String.self, forKey: .ipv4Prefix)
            guard let network = IPv4Network(value) else {
                throw SearchbotDecodingIssue(
                    path: codingPath(decoder.codingPath, appending: CodingKeys.ipv4Prefix),
                    reason: "invalid IPv4 network prefix \(String(reflecting: value))"
                )
            }
            range = AnyIPAddressRange(IPv4AddressRange(covering: network))
            normalized = network.description != value
        } else {
            let value = try container.decode(String.self, forKey: .ipv6Prefix)
            guard let network = IPv6Network(value) else {
                throw SearchbotDecodingIssue(
                    path: codingPath(decoder.codingPath, appending: CodingKeys.ipv6Prefix),
                    reason: "invalid IPv6 network prefix \(String(reflecting: value))"
                )
            }
            range = AnyIPAddressRange(IPv6AddressRange(covering: network))
            normalized = network.description != value
        }
    }
}

private struct SearchbotDecodingIssue: Error {
    let path: String
    let reason: String
}

/// Performs bounded structural checks that `JSONDecoder` cannot express safely for policy input.
///
/// Foundation decoding does not preserve duplicate JSON object members. This scanner therefore
/// rejects duplicate top-level `prefixes` and per-entry `ipv4Prefix` or `ipv6Prefix` members before
/// decoding, while continuing to tolerate duplicate unknown metadata for forward compatibility.
/// It also limits container nesting to protect complete-document parsing. `JSONDecoder` remains
/// responsible for malformed-JSON and typed-value diagnostics.
private struct SearchbotJSONPreflight {
    private enum Context {
        case root
        case prefixesArray
        case prefixEntry(Int)
        case other
    }

    private enum ScanError: Error {
        case malformed
        case duplicateMember(String)
        case nestingLimitExceeded
    }

    private static let maximumNestingDepth = 128

    private let bytes: [UInt8]
    private var index = 0

    init(data: Data) {
        bytes = Array(data)
    }

    static func validationIssue(in data: Data) -> SearchbotDecodingIssue? {
        var scanner = Self(data: data)
        do {
            try scanner.scanDocument()
            return nil
        } catch let error as ScanError {
            switch error {
            case .malformed:
                // JSONDecoder remains the authority for malformed-document diagnostics.
                return nil
            case .duplicateMember(let path):
                return SearchbotDecodingIssue(path: path, reason: "duplicate JSON member")
            case .nestingLimitExceeded:
                return SearchbotDecodingIssue(
                    path: "$",
                    reason: "JSON nesting exceeds \(maximumNestingDepth) levels"
                )
            }
        } catch {
            return nil
        }
    }

    private mutating func scanDocument() throws {
        if bytes.starts(with: [0xEF, 0xBB, 0xBF]) {
            index = 3
        }
        skipWhitespace()
        try scanValue(context: .root, nestingDepth: 0)
        skipWhitespace()
        guard index == bytes.endIndex else {
            throw ScanError.malformed
        }
    }

    private mutating func scanValue(context: Context, nestingDepth: Int) throws {
        guard let byte = currentByte else {
            throw ScanError.malformed
        }

        switch byte {
        case 0x7B:
            guard nestingDepth < Self.maximumNestingDepth else {
                throw ScanError.nestingLimitExceeded
            }
            try scanObject(context: context, nestingDepth: nestingDepth + 1)
        case 0x5B:
            guard nestingDepth < Self.maximumNestingDepth else {
                throw ScanError.nestingLimitExceeded
            }
            try scanArray(context: context, nestingDepth: nestingDepth + 1)
        case 0x22:
            _ = try scanStringToken()
        case 0x74:
            try scanLiteral([0x74, 0x72, 0x75, 0x65])
        case 0x66:
            try scanLiteral([0x66, 0x61, 0x6C, 0x73, 0x65])
        case 0x6E:
            try scanLiteral([0x6E, 0x75, 0x6C, 0x6C])
        case 0x2D, 0x30...0x39:
            try scanNumber()
        default:
            throw ScanError.malformed
        }
    }

    private mutating func scanObject(context: Context, nestingDepth: Int) throws {
        try consume(0x7B)
        skipWhitespace()
        if consumeIfPresent(0x7D) {
            return
        }

        var semanticMembers = Set<String>()
        while true {
            let keyToken = try scanStringToken()
            let key = try decodeString(in: keyToken)

            // CHANGE: Foundation collapses duplicate object members. Detect the policy-bearing
            // keys structurally so equivalent spellings cannot select different prefixes.
            if let path = semanticPath(for: key, in: context),
                !semanticMembers.insert(key).inserted
            {
                throw ScanError.duplicateMember(path)
            }

            skipWhitespace()
            try consume(0x3A)
            skipWhitespace()
            try scanValue(
                context: childContext(for: key, in: context),
                nestingDepth: nestingDepth
            )
            skipWhitespace()

            if consumeIfPresent(0x7D) {
                return
            }
            try consume(0x2C)
            skipWhitespace()
        }
    }

    private mutating func scanArray(context: Context, nestingDepth: Int) throws {
        try consume(0x5B)
        skipWhitespace()
        if consumeIfPresent(0x5D) {
            return
        }

        var elementIndex = 0
        while true {
            let childContext: Context
            if case .prefixesArray = context {
                childContext = .prefixEntry(elementIndex)
            } else {
                childContext = .other
            }
            try scanValue(context: childContext, nestingDepth: nestingDepth)
            elementIndex += 1
            skipWhitespace()

            if consumeIfPresent(0x5D) {
                return
            }
            try consume(0x2C)
            skipWhitespace()
        }
    }

    private mutating func scanStringToken() throws -> Range<Int> {
        let start = index
        try consume(0x22)

        while let byte = currentByte {
            index += 1
            switch byte {
            case 0x22:
                return start..<index
            case 0x5C:
                guard let escape = currentByte else {
                    throw ScanError.malformed
                }
                index += 1
                switch escape {
                case 0x22, 0x2F, 0x5C, 0x62, 0x66, 0x6E, 0x72, 0x74:
                    break
                case 0x75:
                    for _ in 0..<4 {
                        guard let hex = currentByte, isHexDigit(hex) else {
                            throw ScanError.malformed
                        }
                        index += 1
                    }
                default:
                    throw ScanError.malformed
                }
            case 0x00...0x1F:
                throw ScanError.malformed
            default:
                break
            }
        }

        throw ScanError.malformed
    }

    private func decodeString(in range: Range<Int>) throws -> String {
        do {
            return try JSONDecoder().decode(String.self, from: Data(bytes[range]))
        } catch {
            throw ScanError.malformed
        }
    }

    private mutating func scanLiteral(_ literal: [UInt8]) throws {
        guard bytes[index...].starts(with: literal) else {
            throw ScanError.malformed
        }
        index += literal.count
    }

    private mutating func scanNumber() throws {
        _ = consumeIfPresent(0x2D)
        guard let first = currentByte else {
            throw ScanError.malformed
        }

        if first == 0x30 {
            index += 1
            if let next = currentByte, (0x30...0x39).contains(next) {
                throw ScanError.malformed
            }
        } else if (0x31...0x39).contains(first) {
            index += 1
            consumeDigits()
        } else {
            throw ScanError.malformed
        }

        if consumeIfPresent(0x2E) {
            guard let digit = currentByte, (0x30...0x39).contains(digit) else {
                throw ScanError.malformed
            }
            consumeDigits()
        }

        if consumeIfPresent(0x65) || consumeIfPresent(0x45) {
            if !consumeIfPresent(0x2B) {
                _ = consumeIfPresent(0x2D)
            }
            guard let digit = currentByte, (0x30...0x39).contains(digit) else {
                throw ScanError.malformed
            }
            consumeDigits()
        }
    }

    private mutating func consumeDigits() {
        while let byte = currentByte, (0x30...0x39).contains(byte) {
            index += 1
        }
    }

    private mutating func consume(_ expected: UInt8) throws {
        guard consumeIfPresent(expected) else {
            throw ScanError.malformed
        }
    }

    private mutating func consumeIfPresent(_ expected: UInt8) -> Bool {
        guard currentByte == expected else {
            return false
        }
        index += 1
        return true
    }

    private mutating func skipWhitespace() {
        while let byte = currentByte, byte == 0x20 || byte == 0x09 || byte == 0x0A || byte == 0x0D {
            index += 1
        }
    }

    private func semanticPath(for key: String, in context: Context) -> String? {
        switch context {
        case .root where key == "prefixes":
            return "$.prefixes"
        case .prefixEntry(let index) where key == "ipv4Prefix" || key == "ipv6Prefix":
            return "$.prefixes[\(index)].\(key)"
        default:
            return nil
        }
    }

    private func childContext(for key: String, in context: Context) -> Context {
        if case .root = context, key == "prefixes" {
            return .prefixesArray
        }
        return .other
    }

    private func isHexDigit(_ byte: UInt8) -> Bool {
        (0x30...0x39).contains(byte)
            || (0x41...0x46).contains(byte)
            || (0x61...0x66).contains(byte)
    }

    private var currentByte: UInt8? {
        index < bytes.endIndex ? bytes[index] : nil
    }
}

private func codingPath(
    _ keys: [any CodingKey],
    appending key: (any CodingKey)? = nil
) -> String {
    var path = "$"
    for component in keys + (key.map { [$0] } ?? []) {
        if let index = component.intValue {
            path += "[\(index)]"
        } else {
            path += ".\(component.stringValue)"
        }
    }
    return path
}
