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
import Testing

@testable import cidrmerge

@Suite("IP Address Range Tests")
struct IPAddressRangeTests {
    @Test("Programmatic endpoints discard non-host prefix context")
    func normalizesEndpointPrefixContext() throws {
        let lower = try #require(IPv4Address("192.0.2.2/24"))
        let upper = try #require(IPv4Address("192.0.2.7/30"))
        let range = try #require(IPv4AddressRange(lowerBound: lower, upperBound: upper))

        #expect(range.description == "192.0.2.2...192.0.2.7")
        #expect(range.lowerBound.prefixLength.intValue == 32)
        #expect(range.upperBound.prefixLength.intValue == 32)
        #expect(range.closedRange.contains(try #require(IPv4Address("192.0.2.4"))))
    }

    @Test("Range text has one strict address-only grammar")
    func parsesStrictGrammar() throws {
        #expect(IPv4AddressRange("192.0.2.2...192.0.2.7")?.description == "192.0.2.2...192.0.2.7")
        #expect(IPv6AddressRange("2001:0DB8::1...2001:0DB8::F")?.description == "2001:db8::1...2001:db8::f")
        #expect(IPv4AddressRange("192.0.2.7...192.0.2.2") == nil)
        #expect(IPv4AddressRange("192.0.2.2/32...192.0.2.7/32") == nil)
        #expect(IPv4AddressRange("192.0.2.2 ...192.0.2.7") == nil)
        #expect(IPv4AddressRange("192.0.2.2...192.0.2.7...192.0.2.8") == nil)
        #expect(AnyIPAddressRange("192.0.2.2...2001:db8::1") == nil)
    }

    @Test("A range uses canonical single-string Codable")
    func roundTripsCodable() throws {
        let range = try #require(IPv6AddressRange("2001:db8::1...2001:db8::f"))
        let encoded = try JSONEncoder().encode(range)
        let decoded = try JSONDecoder().decode(IPv6AddressRange.self, from: encoded)

        #expect(String(decoding: encoded, as: UTF8.self) == #""2001:db8::1...2001:db8::f""#)
        #expect(decoded == range)
        #expect(throws: DecodingError.self) {
            try JSONDecoder().decode(
                IPv6AddressRange.self,
                from: Data(#""2001:db8::f...2001:db8::1""#.utf8)
            )
        }
    }

    @Test("Family-erased ranges use the same canonical string wire form")
    func roundTripsErasedCodable() throws {
        let range = try #require(AnyIPAddressRange("192.0.2.2...192.0.2.7"))
        let encoded = try JSONEncoder().encode(range)
        let decoded = try JSONDecoder().decode(AnyIPAddressRange.self, from: encoded)

        #expect(String(decoding: encoded, as: UTF8.self) == #""192.0.2.2...192.0.2.7""#)
        #expect(decoded == range)
    }

    @Test("Range sizes cover singletons and complete address spaces")
    func reportsRepresentableSizes() throws {
        let singleton = try #require(IPv4AddressRange("192.0.2.7...192.0.2.7"))
        let allIPv4 = try #require(IPv4AddressRange("0.0.0.0...255.255.255.255"))
        let allIPv6 = try #require(IPv6AddressRange("::...ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"))

        #expect(singleton.rangeSizeIfRepresentable == 1)
        #expect(allIPv4.rangeSizeIfRepresentable == UInt128(UInt32.max) + 1)
        #expect(allIPv6.rangeSizeIfRepresentable == nil)
    }

    @Test("Containment, overlap, adjacency, and merging are exact")
    func performsRangeMath() throws {
        let first = try #require(IPv4AddressRange("192.0.2.2...192.0.2.7"))
        let contained = try #require(IPv4AddressRange("192.0.2.3...192.0.2.6"))
        let overlap = try #require(IPv4AddressRange("192.0.2.7...192.0.2.9"))
        let adjacent = try #require(IPv4AddressRange("192.0.2.8...192.0.2.10"))
        let gap = try #require(IPv4AddressRange("192.0.2.9...192.0.2.10"))

        #expect(first.contains(contained))
        #expect(first.contains(try #require(IPv4Address("192.0.2.4"))))
        #expect(first.overlaps(overlap))
        #expect(first.isAdjacent(to: adjacent))
        #expect(first.merged(with: adjacent)?.description == "192.0.2.2...192.0.2.10")
        #expect(first.merged(with: gap) == nil)
    }

    @Test("Adjacency checks do not overflow at the top of an address family")
    func handlesTopOfSpace() throws {
        let penultimate = try #require(IPv4AddressRange("255.255.255.254...255.255.255.254"))
        let maximum = try #require(IPv4AddressRange("255.255.255.255...255.255.255.255"))

        #expect(penultimate.isAdjacent(to: maximum))
        #expect(maximum.isAdjacent(to: penultimate))
        #expect(maximum.merged(with: penultimate)?.description == "255.255.255.254...255.255.255.255")
        #expect(!maximum.isAdjacent(to: maximum))
    }

    @Test("Coalescing returns a minimal sorted exact range list")
    func coalescesRanges() throws {
        let ranges = try [
            "192.0.2.8...192.0.2.9",
            "192.0.2.2...192.0.2.7",
            "192.0.2.3...192.0.2.5",
            "192.0.2.8...192.0.2.9",
            "192.0.2.11...192.0.2.12",
        ].map { try #require(IPv4AddressRange($0)) }

        #expect(
            IPv4AddressRange.coalescing(ranges).map(\.description)
                == ["192.0.2.2...192.0.2.9", "192.0.2.11...192.0.2.12"]
        )
    }

    @Test("Family erasure partitions deterministically and never mixes families")
    func erasesFamiliesSafely() throws {
        let ipv4 = try #require(AnyIPAddressRange("192.0.2.1...192.0.2.2"))
        let ipv6 = try #require(
            AnyIPAddressRange("2001:db8::1...2001:db8::2", parseOrder: .ipv6ThenIPv4)
        )

        #expect(ipv4.isIPv4)
        #expect(ipv6.isIPv6)
        #expect(!ipv4.contains(ipv6))
        #expect(!ipv4.overlaps(ipv6))
        #expect(!ipv4.isAdjacent(to: ipv6))
        #expect(ipv4.merged(with: ipv6) == nil)
        #expect(AnyIPAddressRange.coalescing([ipv6, ipv4]).map(\.description) == [ipv4.description, ipv6.description])
    }

    @Test("Networks bridge to ranges without preserving prefix representation")
    func coversNetworkPrefixes() throws {
        let network = try #require(AnyIPNetwork("192.0.2.128/25"))
        let range = AnyIPAddressRange(covering: network)

        #expect(range.description == "192.0.2.128...192.0.2.255")
        #expect(range.lowerBound.description == "192.0.2.128/32")
        #expect(range.upperBound.description == "192.0.2.255/32")
    }
}
