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
        reserveOutputCapacity(in: &data, prefixCount: result.statistics.outputCount)

        for network in result.ipv4 {
            data.appendUTF8(network.description)
            data.append(0x0A)
        }
        for network in result.ipv6 {
            data.appendUTF8(network.description)
            data.append(0x0A)
        }

        return data
    }

    static func json(_ result: MergeResult) -> Data {
        var data = Data()
        reserveOutputCapacity(in: &data, prefixCount: result.statistics.outputCount)
        data.appendUTF8("{\n")
        appendJSONNetworks(result.ipv4, key: "ipv4", trailingComma: true, to: &data)
        appendJSONNetworks(result.ipv6, key: "ipv6", trailingComma: false, to: &data)
        data.appendUTF8("}\n")
        return data
    }

    static func statistics(_ statistics: MergeStatistics) -> Data {
        let percentage: String
        if statistics.inputCount == 0 {
            percentage = "n/a"
        } else {
            let reduction = Double(statistics.removedCount) / Double(statistics.inputCount) * 100
            percentage = String(
                format: "%.1f%%",
                locale: Locale(identifier: "en_US_POSIX"),
                reduction
            )
        }

        return Data(
            """
            input: \(countDescription(statistics.inputCount)) (\(statistics.inputIPv4Count) IPv4, \(statistics.inputIPv6Count) IPv6)
            normalized: \(countDescription(statistics.normalizedInputCount))
            output: \(countDescription(statistics.outputCount)) (\(statistics.outputIPv4Count) IPv4, \(statistics.outputIPv6Count) IPv6)
            reduction: \(countDescription(statistics.removedCount)) (\(percentage))

            """.utf8
        )
    }

    private static func countDescription(_ count: Int) -> String {
        "\(count) \(count == 1 ? "prefix" : "prefixes")"
    }

    private static func appendJSONNetworks<Family: IPAddressFamily>(
        _ networks: [IPNetwork<Family>],
        key: String,
        trailingComma: Bool,
        to data: inout Data
    ) {
        if networks.isEmpty {
            data.appendUTF8("  \"\(key)\": []\(trailingComma ? "," : "")\n")
            return
        }

        data.appendUTF8("  \"\(key)\": [\n")
        for (index, network) in networks.enumerated() {
            // CHANGE: Canonical CIDR descriptions contain only JSON-safe ASCII, enabling byte-stable output.
            data.appendUTF8("    \"")
            data.appendUTF8(network.description)
            data.appendUTF8(index == networks.index(before: networks.endIndex) ? "\"\n" : "\",\n")
        }
        data.appendUTF8("  ]\(trailingComma ? "," : "")\n")
    }

    private static func reserveOutputCapacity(in data: inout Data, prefixCount: Int) {
        let (capacity, overflow) = prefixCount.multipliedReportingOverflow(by: 32)
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
