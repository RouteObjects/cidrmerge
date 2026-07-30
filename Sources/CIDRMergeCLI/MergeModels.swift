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
import CIDRMergeCore

enum OutputRepresentation: String, Equatable, Sendable {
    case ranges
    case cidr
}

/// Input and output cardinality recorded by the text-oriented CLI boundary.
struct MergeStatistics: Equatable, Sendable {
    var representation: OutputRepresentation
    var inputCount = 0
    var inputIPv4Count = 0
    var inputIPv6Count = 0
    var normalizedInputCount = 0
    var outputIPv4Count = 0
    var outputIPv6Count = 0

    var outputCount: Int {
        outputIPv4Count + outputIPv6Count
    }

    /// Positive for expansion, negative for reduction, and zero when the count is unchanged.
    var countChange: Int {
        outputCount - inputCount
    }
}

enum FamilyMergeOutput<Family: IPAddressFamily>: Equatable, Sendable {
    case ranges([IPAddressRange<Family>])
    case cidr([IPNetwork<Family>])

    var count: Int {
        switch self {
        case .ranges(let ranges): ranges.count
        case .cidr(let networks): networks.count
        }
    }

    var descriptions: [String] {
        switch self {
        case .ranges(let ranges): ranges.map(\.description)
        case .cidr(let networks): networks.map(\.description)
        }
    }
}

struct MergeResult: Equatable, Sendable {
    var representation: OutputRepresentation
    var ipv4: FamilyMergeOutput<V4>
    var ipv6: FamilyMergeOutput<V6>
    var statistics: MergeStatistics
}

/// Parsed family-partitioned coverage plus statistics that only have meaning for textual input.
struct ParsedInput: Sendable {
    private(set) var ipv4: [IPv4AddressRange] = []
    private(set) var ipv6: [IPv6AddressRange] = []
    private(set) var inputCount = 0
    private(set) var inputIPv4Count = 0
    private(set) var inputIPv6Count = 0
    private(set) var normalizedInputCount = 0

    mutating func append(_ range: AnyIPAddressRange, normalized: Bool) {
        inputCount += 1
        if normalized {
            normalizedInputCount += 1
        }

        switch range {
        case .v4(let range):
            inputIPv4Count += 1
            ipv4.append(range)
        case .v6(let range):
            inputIPv6Count += 1
            ipv6.append(range)
        }
    }

    func merged(representation: OutputRepresentation = .ranges) -> MergeResult {
        let ipv4Coverage = IPAddressCoverage(ipv4)
        let ipv6Coverage = IPAddressCoverage(ipv6)

        let ipv4Output: FamilyMergeOutput<V4>
        let ipv6Output: FamilyMergeOutput<V6>
        switch representation {
        case .ranges:
            ipv4Output = .ranges(ipv4Coverage.ranges)
            ipv6Output = .ranges(ipv6Coverage.ranges)
        case .cidr:
            // CHANGE: swift-cidr remains the only range-to-prefix summarization engine.
            ipv4Output = .cidr(ipv4Coverage.summarizedNetworks())
            ipv6Output = .cidr(ipv6Coverage.summarizedNetworks())
        }

        return MergeResult(
            representation: representation,
            ipv4: ipv4Output,
            ipv6: ipv6Output,
            statistics: MergeStatistics(
                representation: representation,
                inputCount: inputCount,
                inputIPv4Count: inputIPv4Count,
                inputIPv6Count: inputIPv6Count,
                normalizedInputCount: normalizedInputCount,
                outputIPv4Count: ipv4Output.count,
                outputIPv6Count: ipv6Output.count
            )
        )
    }
}
