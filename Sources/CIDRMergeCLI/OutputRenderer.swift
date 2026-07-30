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
        // CHANGE: Sorted keys make JSON byte-deterministic without coupling Core models to this schema.
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
            percentage = String(
                format: "%.1f%%",
                locale: Locale(identifier: "en_US_POSIX"),
                magnitude
            )
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

    private static func appendText<Family: IPAddressFamily>(
        _ output: FamilyMergeOutput<Family>,
        to data: inout Data
    ) {
        switch output {
        case .ranges(let ranges):
            for range in ranges {
                data.appendUTF8(range.description)
                data.append(0x0A)
            }
        case .cidr(let networks):
            for network in networks {
                data.appendUTF8(network.description)
                data.append(0x0A)
            }
        }
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

extension Data {
    fileprivate mutating func appendUTF8(_ string: String) {
        append(contentsOf: string.utf8)
    }
}
