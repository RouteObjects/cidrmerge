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
import Testing

import struct CIDRMergeCore.CIDRMergeCoverage

@Suite("CIDRMergeCoverage Tests")
struct CIDRMergeCoverageTests {
    @Test("Empty input produces empty family indexes and projections")
    func emptyCoverage() {
        let coverage = CIDRMergeCoverage(ranges: [AnyIPAddressRange]())

        #expect(coverage.ipv4.isEmpty)
        #expect(coverage.ipv6.isEmpty)
        #expect(coverage.ranges.isEmpty)
        #expect(coverage.summarizedNetworks().isEmpty)
    }

    @Test("Mixed input normalizes independently and projects IPv4 first")
    func mixedFamilyNormalization() throws {
        let coverage = CIDRMergeCoverage(
            ranges: try [
                #require(AnyIPAddressRange("2001:db8::4...2001:db8::7")),
                #require(AnyIPAddressRange("192.0.2.8...192.0.2.9")),
                #require(AnyIPAddressRange("192.0.2.3...192.0.2.5")),
                #require(AnyIPAddressRange("2001:db8::1...2001:db8::3")),
                #require(AnyIPAddressRange("192.0.2.2...192.0.2.7")),
                #require(AnyIPAddressRange("192.0.2.8...192.0.2.9")),
            ]
        )

        #expect(coverage.ipv4.ranges.map(\.description) == ["192.0.2.2...192.0.2.9"])
        #expect(coverage.ipv6.ranges.map(\.description) == ["2001:db8::1...2001:db8::7"])
        #expect(
            coverage.ranges.map(\.description)
                == ["192.0.2.2...192.0.2.9", "2001:db8::1...2001:db8::7"]
        )
    }

    @Test("Equality and hashing compare normalized mixed-family coverage")
    func normalizedEquality() throws {
        let fragmented = CIDRMergeCoverage(
            ranges: try [
                #require(AnyIPAddressRange("2001:db8::3...2001:db8::4")),
                #require(AnyIPAddressRange("192.0.2.4...192.0.2.7")),
                #require(AnyIPAddressRange("192.0.2.2...192.0.2.5")),
                #require(AnyIPAddressRange("2001:db8::1...2001:db8::2")),
            ]
        )
        let normalized = CIDRMergeCoverage(
            ranges: try [
                #require(AnyIPAddressRange("192.0.2.2...192.0.2.7")),
                #require(AnyIPAddressRange("2001:db8::1...2001:db8::4")),
            ]
        )

        #expect(fragmented == normalized)
        #expect(fragmented.hashValue == normalized.hashValue)
    }

    @Test("Prepartitioned CLI construction matches the public mixed-family initializer")
    func prepartitionedConstruction() throws {
        let ipv4 = try [
            #require(IPv4AddressRange("192.0.2.1...192.0.2.3")),
            #require(IPv4AddressRange("192.0.2.4...192.0.2.7")),
        ]
        let ipv6 = try [
            #require(IPv6AddressRange("2001:db8::1...2001:db8::3")),
            #require(IPv6AddressRange("2001:db8::4...2001:db8::7")),
        ]
        let mixed = ipv6.map(AnyIPAddressRange.v6) + ipv4.map(AnyIPAddressRange.v4)

        let publicCoverage = CIDRMergeCoverage(ranges: mixed)
        let cliCoverage = CIDRMergeCoverage(ipv4Ranges: ipv4, ipv6Ranges: ipv6)

        #expect(cliCoverage == publicCoverage)
        #expect(
            cliCoverage.ranges.map(\.description) == [
                "192.0.2.1...192.0.2.7",
                "2001:db8::1...2001:db8::7",
            ])
    }

    @Test("Normalization preserves uncovered gaps in both families")
    func preservesGaps() throws {
        let coverage = CIDRMergeCoverage(
            ranges: try [
                #require(AnyIPAddressRange("192.0.2.1...192.0.2.2")),
                #require(AnyIPAddressRange("192.0.2.4...192.0.2.5")),
                #require(AnyIPAddressRange("2001:db8::1...2001:db8::2")),
                #require(AnyIPAddressRange("2001:db8::4...2001:db8::5")),
            ]
        )

        #expect(coverage.ipv4.ranges.count == 2)
        #expect(coverage.ipv6.ranges.count == 2)
        #expect(
            !coverage.contains(
                try #require(AnyIPAddress("192.0.2.3"))
            )
        )
        #expect(
            !coverage.contains(
                try #require(AnyIPAddress("2001:db8::3"))
            )
        )
    }

    @Test("Canonical network summaries are deterministic and IPv4 first")
    func ipv4FirstSummaries() throws {
        let coverage = CIDRMergeCoverage(
            ranges: try [
                #require(AnyIPAddressRange("2001:db8::1...2001:db8::3")),
                #require(AnyIPAddressRange("192.168.2.2...192.168.2.7")),
            ]
        )

        let summaries = coverage.summarizedNetworks()
        #expect(
            summaries.map(\.description)
                == [
                    "192.168.2.2/31",
                    "192.168.2.4/30",
                    "2001:db8::1/128",
                    "2001:db8::2/127",
                ]
        )
        #expect(summaries.prefix(2).allSatisfy { $0.isIPv4 })
        #expect(summaries.suffix(2).allSatisfy { $0.isIPv6 })
    }

    @Test("Containment dispatches to the matching family index")
    func containsBothFamilies() throws {
        let coverage = CIDRMergeCoverage(
            ranges: try [
                #require(AnyIPAddressRange("192.0.2.10...192.0.2.19")),
                #require(AnyIPAddressRange("2001:db8::10...2001:db8::19")),
            ]
        )

        #expect(
            coverage.contains(
                try #require(AnyIPAddress("192.0.2.10"))
            )
        )
        #expect(
            coverage.contains(
                try #require(AnyIPAddress("192.0.2.19"))
            )
        )
        #expect(
            coverage.contains(
                try #require(AnyIPAddress("2001:db8::10"))
            )
        )
        #expect(
            coverage.contains(
                try #require(AnyIPAddress("2001:db8::19"))
            )
        )
        #expect(
            !coverage.contains(
                try #require(AnyIPAddress("192.0.2.20"))
            )
        )
        #expect(
            !coverage.contains(
                try #require(AnyIPAddress("2001:db8::20"))
            )
        )
    }
}
