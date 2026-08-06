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

/// Normalized exact address coverage across IPv4 and IPv6.
///
/// `CIDRMergeCoverage` is cidrmerge's mixed-family policy-compiler facade. It partitions input by
/// address family and delegates every range, containment, normalization, and summarization
/// operation to swift-cidr. Family-erased output is always ordered IPv4 first, then IPv6.
public struct CIDRMergeCoverage: Sendable, Hashable {
    /// The normalized IPv4 coverage.
    public let ipv4: IPAddressCoverage<V4>

    /// The normalized IPv6 coverage.
    public let ipv6: IPAddressCoverage<V6>

    /// Creates mixed-family exact coverage from family-erased ranges.
    public init<Ranges: Sequence>(ranges: Ranges)
    where Ranges.Element == AnyIPAddressRange {
        var ipv4Ranges: [IPv4AddressRange] = []
        var ipv6Ranges: [IPv6AddressRange] = []

        for range in ranges {
            switch range {
            case .v4(let range):
                ipv4Ranges.append(range)
            case .v6(let range):
                ipv6Ranges.append(range)
            }
        }

        // Family-specific canonical coverage remains owned by swift-cidr; this facade only
        // establishes the mixed-family partition and deterministic family order.
        self.init(ipv4Ranges: ipv4Ranges, ipv6Ranges: ipv6Ranges)
    }

    /// Creates mixed-family coverage from ranges already partitioned by the CLI parser.
    ///
    /// This package-only path preserves the streaming parser's bounded staging cost while keeping
    /// the public API centered on family-erased swift-cidr ranges.
    package init<IPv4Ranges: Sequence, IPv6Ranges: Sequence>(
        ipv4Ranges: IPv4Ranges,
        ipv6Ranges: IPv6Ranges
    )
    where
        IPv4Ranges.Element == IPv4AddressRange,
        IPv6Ranges.Element == IPv6AddressRange
    {
        // Avoid rebuilding a million-element family-erased array when CLI parsing has
        // already established each range's family.
        self.ipv4 = IPAddressCoverage(ipv4Ranges)
        self.ipv6 = IPAddressCoverage(ipv6Ranges)
    }

    /// The normalized family-erased ranges, ordered IPv4 first and then IPv6.
    public var ranges: [AnyIPAddressRange] {
        var result: [AnyIPAddressRange] = []
        result.reserveCapacity(ipv4.ranges.count + ipv6.ranges.count)
        result.append(contentsOf: ipv4.ranges.map(AnyIPAddressRange.v4))
        result.append(contentsOf: ipv6.ranges.map(AnyIPAddressRange.v6))
        return result
    }

    /// The smallest exact CIDR cover, ordered IPv4 first and then IPv6.
    public func summarizedNetworks() -> [AnyIPNetwork] {
        let ipv4Networks = ipv4.summarizedNetworks()
        let ipv6Networks = ipv6.summarizedNetworks()
        var result: [AnyIPNetwork] = []
        result.reserveCapacity(ipv4Networks.count + ipv6Networks.count)
        result.append(contentsOf: ipv4Networks.map(AnyIPNetwork.v4))
        result.append(contentsOf: ipv6Networks.map(AnyIPNetwork.v6))
        return result
    }

    /// Returns whether `address` belongs to this exact coverage set.
    public func contains(_ address: AnyIPAddress) -> Bool {
        switch address {
        case .v4(let address):
            ipv4.contains(address)
        case .v6(let address):
            ipv6.contains(address)
        }
    }
}
