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

@testable import cidrmerge

@Suite("Network Merger Tests")
struct NetworkMergerTests {
    @Test("Exact duplicates and contained networks collapse to the covering prefix")
    func deduplicatesAndSubsumes() throws {
        let networks = try parseIPv4([
            "10.0.0.0/8",
            "10.0.0.0/8",
            "10.1.0.0/16",
            "10.1.2.0/24",
        ])

        #expect(NetworkMerger.merge(networks).map(\.description) == ["10.0.0.0/8"])
    }

    @Test("Sibling merges cascade to their common ancestor")
    func cascadesSiblingMerges() throws {
        let networks = try parseIPv4([
            "192.0.2.192/26",
            "192.0.2.0/26",
            "192.0.2.128/26",
            "192.0.2.64/26",
        ])

        #expect(NetworkMerger.merge(networks).map(\.description) == ["192.0.2.0/24"])
    }

    @Test("Adjacent unequal networks remain exact when no parent represents their union")
    func preservesUnequalAdjacency() throws {
        let networks = try parseIPv4([
            "192.0.2.0/25",
            "192.0.2.128/26",
        ])

        #expect(
            NetworkMerger.merge(networks).map(\.description)
                == ["192.0.2.0/25", "192.0.2.128/26"]
        )
    }

    @Test("A gap is never covered by aggregation")
    func preservesGaps() throws {
        let networks = try parseIPv4([
            "192.0.2.0/26",
            "192.0.2.128/26",
        ])

        #expect(
            NetworkMerger.merge(networks).map(\.description)
                == ["192.0.2.0/26", "192.0.2.128/26"]
        )
    }

    @Test("Top-of-space siblings aggregate without overflow")
    func aggregatesTopOfAddressSpace() throws {
        let networks = try parseIPv4([
            "255.255.255.255/32",
            "255.255.255.254/32",
        ])

        #expect(NetworkMerger.merge(networks).map(\.description) == ["255.255.255.254/31"])
    }

    @Test("IPv6 sibling networks use the same family-bound aggregation")
    func aggregatesIPv6Siblings() throws {
        let first = try #require(IPv6Network("2001:db8::/65"))
        let second = try #require(IPv6Network("2001:db8:0:0:8000::/65"))

        #expect(NetworkMerger.merge([second, first]).map(\.description) == ["2001:db8::/64"])
    }

    @Test("Randomized /24-contained inputs retain exact membership and never expand in count")
    func randomizedExactUnionProperties() throws {
        let base = try #require(IPv4Address("198.51.100.0")).address
        var generator = DeterministicGenerator(state: 0xC1D2_4E)

        for _ in 0..<1_000 {
            let count = Int(generator.next() % 41)
            var input: [IPv4Network] = []
            input.reserveCapacity(count)

            for _ in 0..<count {
                let prefixLengthValue = 24 + Int(generator.next() % 9)
                let prefixLength = try #require(IPv4PrefixLength(prefixLengthValue))
                let address = base | UInt32(generator.next() & 0xFF)
                input.append(IPv4Network(prefix: address, prefixLength: prefixLength))
            }

            let output = NetworkMerger.merge(input)
            #expect(output.count <= input.count)
            #expect(NetworkMerger.merge(output) == output)
            #expect(NetworkMerger.merge(input.reversed()) == output)

            for offset in UInt32(0)...UInt32(255) {
                let address = IPv4Address(address: base | offset)
                let inputContainsAddress = input.contains { $0.contains(address) }
                let outputContainsAddress = output.contains { $0.contains(address) }
                #expect(inputContainsAddress == outputContainsAddress)
            }

            for firstIndex in output.indices {
                for secondIndex in output.indices where firstIndex != secondIndex {
                    #expect(!output[firstIndex].contains(output[secondIndex]))
                }
            }

            for index in output.indices.dropLast() {
                #expect(NetworkMerger.aggregateSiblings(output[index], output[index + 1]) == nil)
            }
        }
    }

    private func parseIPv4(_ values: [String]) throws -> [IPv4Network] {
        try values.map { try #require(IPv4Network($0)) }
    }
}

private struct DeterministicGenerator {
    var state: UInt64

    mutating func next() -> UInt64 {
        state = state &* 6_364_136_223_846_793_005 &+ 1_442_695_040_888_963_407
        return state
    }
}
