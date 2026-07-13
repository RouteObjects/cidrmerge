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

@Suite("Coverage Compiler Tests")
struct CoverageCompilerTests {
    @Test("Ranges are the default minimal containment representation")
    func defaultsToRanges() throws {
        let collection = try collection([
            "192.0.2.0/25",
            "192.0.2.128/26",
        ])

        let result = collection.merged()

        #expect(result.statistics.representation == .ranges)
        #expect(result.ipv4.descriptions == ["192.0.2.0...192.0.2.191"])
    }

    @Test("CIDR representation delegates unequal adjacency to swift-cidr summarization")
    func summarizesUnequalAdjacency() throws {
        let collection = try collection([
            "192.0.2.0/25",
            "192.0.2.128/26",
        ])

        #expect(
            collection.merged(representation: .cidr).ipv4.descriptions
                == ["192.0.2.0/25", "192.0.2.128/26"]
        )
    }

    @Test("A gap is never covered by either representation")
    func preservesGaps() throws {
        let collection = try collection([
            "192.0.2.0/26",
            "192.0.2.128/26",
        ])

        #expect(
            collection.merged().ipv4.descriptions
                == ["192.0.2.0...192.0.2.63", "192.0.2.128...192.0.2.191"]
        )
        #expect(
            collection.merged(representation: .cidr).ipv4.descriptions
                == ["192.0.2.0/26", "192.0.2.128/26"]
        )
    }

    @Test("Top-of-space adjacency coalesces without overflow")
    func coalescesTopOfAddressSpace() throws {
        let collection = try collection([
            "255.255.255.255/32",
            "255.255.255.254/32",
        ])

        #expect(collection.merged().ipv4.descriptions == ["255.255.255.254...255.255.255.255"])
        #expect(collection.merged(representation: .cidr).ipv4.descriptions == ["255.255.255.254/31"])
    }

    @Test("IPv6 uses the same family-bound range aggregation")
    func coalescesIPv6() throws {
        let collection = try collection([
            "2001:db8::/65",
            "2001:db8:0:0:8000::/65",
        ])

        #expect(
            collection.merged().ipv6.descriptions
                == ["2001:db8::...2001:db8::ffff:ffff:ffff:ffff"]
        )
        #expect(collection.merged(representation: .cidr).ipv6.descriptions == ["2001:db8::/64"])
    }

    @Test("A simple arbitrary range has one range and two canonical prefixes")
    func simpleRangeExample() throws {
        let collection = try collection(["192.168.2.2...192.168.2.7"])

        #expect(collection.merged().ipv4.descriptions == ["192.168.2.2...192.168.2.7"])
        #expect(
            collection.merged(representation: .cidr).ipv4.descriptions
                == ["192.168.2.2/31", "192.168.2.4/30"]
        )
    }

    @Test("A larger arbitrary range has one range and the expected canonical prefix cover")
    func largerRangeExample() throws {
        let collection = try collection(["192.168.1.1...192.168.1.189"])

        #expect(collection.merged().ipv4.descriptions == ["192.168.1.1...192.168.1.189"])
        #expect(
            collection.merged(representation: .cidr).ipv4.descriptions
                == [
                    "192.168.1.1/32",
                    "192.168.1.2/31",
                    "192.168.1.4/30",
                    "192.168.1.8/29",
                    "192.168.1.16/28",
                    "192.168.1.32/27",
                    "192.168.1.64/26",
                    "192.168.1.128/27",
                    "192.168.1.160/28",
                    "192.168.1.176/29",
                    "192.168.1.184/30",
                    "192.168.1.188/31",
                ]
        )
    }

    @Test("Range-to-CIDR preserves coverage but not original prefix structure")
    func doesNotPromisePrefixRoundTrips() throws {
        let collection = try collection([
            "192.0.2.0/32",
            "192.0.2.1/32",
            "192.0.2.2/32",
            "192.0.2.3/32",
        ])

        #expect(collection.merged().ipv4.descriptions == ["192.0.2.0...192.0.2.3"])
        #expect(collection.merged(representation: .cidr).ipv4.descriptions == ["192.0.2.0/30"])
    }

    @Test("Randomized inputs retain exact membership in both representations")
    func randomizedExactUnionProperties() throws {
        let base = try #require(IPv4Address("198.51.100.0")).address
        var generator = DeterministicGenerator(state: 0xC1D2_4E)

        for _ in 0..<1_000 {
            let count = Int(generator.next() % 41)
            var input: [IPv4Network] = []
            input.reserveCapacity(count)
            var collection = CoverageCollection()

            for _ in 0..<count {
                let prefixLengthValue = 24 + Int(generator.next() % 9)
                let prefixLength = try #require(IPv4PrefixLength(prefixLengthValue))
                let address = base | UInt32(generator.next() & 0xFF)
                let network = IPv4Network(prefix: address, prefixLength: prefixLength)
                input.append(network)
                collection.append(.v4(IPv4AddressRange(covering: network)), normalized: false)
            }

            let rangeResult = collection.merged()
            let cidrResult = collection.merged(representation: .cidr)
            let outputRanges = try #require(rangeResult.ipv4.ranges)
            let outputNetworks = try #require(cidrResult.ipv4.networks)

            #expect(outputRanges.count <= input.count)
            #expect(outputNetworks.count <= input.count)
            #expect(IPv4AddressRange.coalescing(outputRanges) == outputRanges)

            for offset in UInt32(0)...UInt32(255) {
                let address = IPv4Address(address: base | offset)
                let inputContains = input.contains { $0.contains(address) }
                #expect(outputRanges.contains { $0.contains(address) } == inputContains)
                #expect(outputNetworks.contains { $0.contains(address) } == inputContains)
            }

            for index in outputRanges.indices.dropLast() {
                #expect(!outputRanges[index].overlaps(outputRanges[index + 1]))
                #expect(!outputRanges[index].isAdjacent(to: outputRanges[index + 1]))
            }
        }
    }

    private func collection(_ values: [String]) throws -> CoverageCollection {
        try TextInputLoader.load(data: Data(values.joined(separator: "\n").utf8))
    }
}

extension FamilyMergeOutput {
    fileprivate var ranges: [IPAddressRange<Family>]? {
        guard case .ranges(let ranges) = self else { return nil }
        return ranges
    }

    fileprivate var networks: [IPNetwork<Family>]? {
        guard case .cidr(let networks) = self else { return nil }
        return networks
    }
}

private struct DeterministicGenerator {
    var state: UInt64

    mutating func next() -> UInt64 {
        state = state &* 6_364_136_223_846_793_005 &+ 1_442_695_040_888_963_407
        return state
    }
}
