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

struct MergeStatistics: Equatable, Sendable {
    var inputCount = 0
    var inputIPv4Count = 0
    var inputIPv6Count = 0
    var normalizedInputCount = 0
    var outputIPv4Count = 0
    var outputIPv6Count = 0

    var outputCount: Int {
        outputIPv4Count + outputIPv6Count
    }

    var removedCount: Int {
        inputCount - outputCount
    }
}

struct MergeResult: Equatable, Sendable {
    var ipv4: [IPv4Network]
    var ipv6: [IPv6Network]
    var statistics: MergeStatistics
}

struct PrefixCollection: Sendable {
    private(set) var ipv4: [IPv4Network] = []
    private(set) var ipv6: [IPv6Network] = []
    private(set) var statistics = MergeStatistics()

    mutating func append(_ network: AnyIPNetwork, normalized: Bool) {
        statistics.inputCount += 1
        if normalized {
            statistics.normalizedInputCount += 1
        }

        switch network {
        case .v4(let network):
            statistics.inputIPv4Count += 1
            ipv4.append(network)
        case .v6(let network):
            statistics.inputIPv6Count += 1
            ipv6.append(network)
        }
    }

    func merged() -> MergeResult {
        let mergedIPv4 = NetworkMerger.merge(ipv4)
        let mergedIPv6 = NetworkMerger.merge(ipv6)
        var finalStatistics = statistics
        finalStatistics.outputIPv4Count = mergedIPv4.count
        finalStatistics.outputIPv6Count = mergedIPv6.count

        return MergeResult(
            ipv4: mergedIPv4,
            ipv6: mergedIPv6,
            statistics: finalStatistics
        )
    }
}

enum NetworkMerger {
    static func merge<Family: IPAddressFamily>(
        _ networks: [IPNetwork<Family>]
    ) -> [IPNetwork<Family>] {
        guard networks.count > 1 else { return networks }

        let sorted = networks.sorted { lhs, rhs in
            if lhs.prefix == rhs.prefix {
                return lhs.prefixLength < rhs.prefixLength
            }
            return lhs.prefix < rhs.prefix
        }

        var stack: [IPNetwork<Family>] = []
        stack.reserveCapacity(sorted.count)

        for network in sorted {
            var current = network
            var isSubsumed = false

            while let previous = stack.last {
                if previous.contains(current) {
                    isSubsumed = true
                    break
                }

                if current.contains(previous) {
                    stack.removeLast()
                    continue
                }

                if let parent = aggregateSiblings(previous, current) {
                    // CHANGE: Re-evaluate the parent against the stack so sibling merges cascade to a fixed point.
                    stack.removeLast()
                    current = parent
                    continue
                }

                break
            }

            if !isSubsumed {
                stack.append(current)
            }
        }

        return stack
    }

    static func aggregateSiblings<Family: IPAddressFamily>(
        _ lhs: IPNetwork<Family>,
        _ rhs: IPNetwork<Family>
    ) -> IPNetwork<Family>? {
        guard lhs != rhs,
            lhs.prefixLength == rhs.prefixLength,
            lhs.nextNetwork == rhs,
            let lhsParent = parent(of: lhs),
            let rhsParent = parent(of: rhs),
            lhsParent == rhsParent
        else {
            return nil
        }

        return lhsParent
    }

    static func parent<Family: IPAddressFamily>(
        of network: IPNetwork<Family>
    ) -> IPNetwork<Family>? {
        let rawPrefixLength = network.prefixLength.rawValue
        guard rawPrefixLength > 0,
            let parentPrefixLength = PrefixLength<Family>(rawValue: rawPrefixLength - 1)
        else {
            return nil
        }

        // CHANGE: Construct through IPNetwork so swift-cidr remains the canonical alignment engine.
        return IPNetwork(
            prefix: network.prefix,
            prefixLength: parentPrefixLength
        )
    }
}
