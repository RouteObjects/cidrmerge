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

#if canImport(FoundationEssentials)
    import FoundationEssentials
#else
    import Foundation
#endif

enum OutputRenderer {
    static func render(_ result: MergeResult, format: OutputFormat) throws -> Data {
        switch format {
        case .raw:
            return raw(result)
        case .json:
            return try json(result)
        }
    }

    static func raw(_ result: MergeResult) -> Data {
        var data = Data()
        reserveOutputCapacity(in: &data, entryCount: result.statistics.outputCount)
        appendText(result.ipv4, to: &data)
        appendText(result.ipv6, to: &data)
        return data
    }

    static func json(_ result: MergeResult) throws -> Data {
        let payload = JSONOutput(
            representation: result.representation.rawValue,
            ipv4: result.ipv4.descriptions,
            ipv6: result.ipv6.descriptions
        )
        let encoder = JSONEncoder()
        // Sorted keys make JSON byte-deterministic without coupling Core models to this schema.
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
        var data = try encoder.encode(payload)
        data.append(0x0A)
        return data
    }

    static func statistics(_ statistics: MergeStatistics) -> Data {
        let percentage: String
        if statistics.inputCount == 0 {
            percentage = "n/a"
        } else {
            let magnitude =
                abs(Double(statistics.countChange))
                / Double(statistics.inputCount) * 100
            percentage = CLICompatibility.percentage(magnitude)
        }

        let changeDescription: String
        if statistics.countChange < 0 {
            changeDescription = "reduction: \(entryDescription(-statistics.countChange)) (\(percentage))"
        } else if statistics.countChange > 0 {
            changeDescription = "expansion: \(entryDescription(statistics.countChange)) (\(percentage))"
        } else {
            changeDescription = "change: unchanged (\(percentage))"
        }

        return Data(
            """
            input: \(entryDescription(statistics.inputCount)) (\(statistics.inputIPv4Count) IPv4, \(statistics.inputIPv6Count) IPv6)
            normalized: \(entryDescription(statistics.normalizedInputCount))
            output: \(outputDescription(statistics.outputCount, representation: statistics.representation)) (\(statistics.outputIPv4Count) IPv4, \(statistics.outputIPv6Count) IPv6)
            \(changeDescription)

            """.utf8
        )
    }

    private static func appendText(_ output: FamilyMergeOutput<V4>, to data: inout Data) {
        // Reuse enough storage for two maximum-width endpoints, "...", and a newline.
        let capacity = 2 * CIDRUTF8Formatting.maximumIPv4AddressLiteralUTF8Count + 4
        withUnsafeTemporaryAllocation(byteCount: capacity, alignment: 1) { buffer in
            switch output {
            case .ranges(let ranges):
                for range in ranges {
                    var count = range.lowerBound.writeAddressLiteralUTF8(into: buffer)
                    buffer[count] = 0x2E
                    buffer[count + 1] = 0x2E
                    buffer[count + 2] = 0x2E
                    count += 3
                    count += range.upperBound.writeAddressLiteralUTF8(
                        into: UnsafeMutableRawBufferPointer(rebasing: buffer[count...])
                    )
                    appendLine(buffer, count: count, to: &data)
                }
            case .cidr(let networks):
                for network in networks {
                    let count = network.writeCIDRNotationUTF8(into: buffer)
                    appendLine(buffer, count: count, to: &data)
                }
            }
        }
    }

    private static func appendText(_ output: FamilyMergeOutput<V6>, to data: inout Data) {
        // Reuse enough storage for two maximum-width endpoints, "...", and a newline.
        let capacity = 2 * CIDRUTF8Formatting.maximumCompressedIPv6AddressLiteralUTF8Count + 4
        withUnsafeTemporaryAllocation(byteCount: capacity, alignment: 1) { buffer in
            switch output {
            case .ranges(let ranges):
                for range in ranges {
                    var count = range.lowerBound.writeCompressedAddressLiteralUTF8(into: buffer)
                    buffer[count] = 0x2E
                    buffer[count + 1] = 0x2E
                    buffer[count + 2] = 0x2E
                    count += 3
                    count += range.upperBound.writeCompressedAddressLiteralUTF8(
                        into: UnsafeMutableRawBufferPointer(rebasing: buffer[count...])
                    )
                    appendLine(buffer, count: count, to: &data)
                }
            case .cidr(let networks):
                for network in networks {
                    let count = network.writeCompressedCIDRNotationUTF8(into: buffer)
                    appendLine(buffer, count: count, to: &data)
                }
            }
        }
    }

    private static func appendLine(_ buffer: UnsafeMutableRawBufferPointer, count: Int, to data: inout Data) {
        // Append only the initialized text and newline; the reusable suffix is unspecified.
        buffer[count] = 0x0A
        data.append(buffer.baseAddress!.assumingMemoryBound(to: UInt8.self), count: count + 1)
    }

    private static func entryDescription(_ count: Int) -> String {
        "\(count) \(count == 1 ? "entry" : "entries")"
    }

    private static func outputDescription(
        _ count: Int,
        representation: OutputRepresentation
    ) -> String {
        switch representation {
        case .ranges:
            return "\(count) \(count == 1 ? "range" : "ranges")"
        case .cidr:
            return "\(count) \(count == 1 ? "prefix" : "prefixes")"
        }
    }

    private static func reserveOutputCapacity(in data: inout Data, entryCount: Int) {
        let (capacity, overflow) = entryCount.multipliedReportingOverflow(by: 48)
        if !overflow {
            data.reserveCapacity(capacity)
        }
    }
}

private struct JSONOutput: Encodable {
    let representation: String
    let ipv4: [String]
    let ipv6: [String]
}
