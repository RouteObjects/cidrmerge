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
    static func text(_ result: MergeResult) -> Data {
        var data = Data()
        reserveOutputCapacity(in: &data, entryCount: result.statistics.outputCount)
        appendText(result.ipv4, to: &data)
        appendText(result.ipv6, to: &data)
        return data
    }

    static func json(_ result: MergeResult) -> Data {
        var data = Data()
        reserveOutputCapacity(in: &data, entryCount: result.statistics.outputCount)
        data.appendUTF8("{\n")
        appendJSON(result.ipv4, key: "ipv4", trailingComma: true, to: &data)
        appendJSON(result.ipv6, key: "ipv6", trailingComma: false, to: &data)
        data.appendUTF8("}\n")
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

    private static func appendJSON<Family: IPAddressFamily>(
        _ output: FamilyMergeOutput<Family>,
        key: String,
        trailingComma: Bool,
        to data: inout Data
    ) {
        switch output {
        case .ranges(let ranges):
            appendJSONValues(
                ranges,
                key: key,
                trailingComma: trailingComma,
                description: \.description,
                to: &data
            )
        case .cidr(let networks):
            appendJSONValues(
                networks,
                key: key,
                trailingComma: trailingComma,
                description: \.description,
                to: &data
            )
        }
    }

    private static func appendJSONValues<Value>(
        _ values: [Value],
        key: String,
        trailingComma: Bool,
        description: KeyPath<Value, String>,
        to data: inout Data
    ) {
        if values.isEmpty {
            data.appendUTF8("  \"\(key)\": []\(trailingComma ? "," : "")\n")
            return
        }

        data.appendUTF8("  \"\(key)\": [\n")
        for (index, value) in values.enumerated() {
            // CHANGE: Canonical CIDR and range descriptions contain only JSON-safe ASCII.
            data.appendUTF8("    \"")
            data.appendUTF8(value[keyPath: description])
            data.appendUTF8(index == values.index(before: values.endIndex) ? "\"\n" : "\",\n")
        }
        data.appendUTF8("  ]\(trailingComma ? "," : "")\n")
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

extension Data {
    fileprivate mutating func appendUTF8(_ string: String) {
        append(contentsOf: string.utf8)
    }
}
