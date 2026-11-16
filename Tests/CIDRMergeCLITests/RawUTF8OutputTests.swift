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

@testable import CIDRMergeCLI

@Suite("Raw UTF-8 Output Tests")
struct RawUTF8OutputTests {
    @Test("Raw range bytes preserve canonical literals, delimiters, and maximum widths")
    func canonicalRangeBytes() throws {
        let ipv4Cases = [
            ("255.255.255.255...255.255.255.255", "255.255.255.255...255.255.255.255"),
            ("0.0.0.0...0.0.0.0", "0.0.0.0...0.0.0.0"),
            ("0.0.0.0...255.255.255.255", "0.0.0.0...255.255.255.255"),
            ("10.20.3.4...10.20.30.40", "10.20.3.4...10.20.30.40"),
        ]
        let ipv6Cases = [
            (
                "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff...ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff",
                "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff...ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"
            ),
            ("::...::", "::...::"),
            ("::1...::1", "::1...::1"),
            ("1:0:0:2:0:0:3:4...1:0:0:2:0:0:3:5", "1::2:0:0:3:4...1::2:0:0:3:5"),
            ("1:2:3:4:5:6:0:8...1:2:3:4:5:6:0:9", "1:2:3:4:5:6:0:8...1:2:3:4:5:6:0:9"),
            ("1:2:3::...1:2:3::1", "1:2:3::...1:2:3::1"),
            ("::ffff:192.0.2.1...::ffff:192.0.2.255", "::ffff:c000:201...::ffff:c000:2ff"),
            ("2001:0DB8::A...2001:0DB8::F", "2001:db8::a...2001:db8::f"),
            ("::...ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff", "::...ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"),
        ]
        let ipv4 = try ipv4Cases.map { try #require(IPv4AddressRange($0.0)) }
        let ipv6 = try ipv6Cases.map { try #require(IPv6AddressRange($0.0)) }
        let expected = ipv4Cases.map { $0.1 } + ipv6Cases.map { $0.1 }

        // Long records immediately precede short records in each family.
        #expect(ipv4Cases[0].1.utf8.count + 1 == 34)
        #expect(ipv6Cases[0].1.utf8.count + 1 == 82)
        try checkRaw(
            makeResult(.ranges, ipv4: .ranges(ipv4), ipv6: .ranges(ipv6)),
            expectedLines: expected
        )
    }

    @Test("Raw CIDR bytes preserve canonical prefixes and decimal prefix-length boundaries")
    func canonicalCIDRBytes() throws {
        let ipv4Cases = [
            ("255.255.255.255/32", "255.255.255.255/32"),
            ("0.0.0.0/0", "0.0.0.0/0"),
            ("255.255.255.255/1", "128.0.0.0/1"),
            ("192.0.2.1/31", "192.0.2.0/31"),
            ("10.255.255.255/9", "10.128.0.0/9"),
            ("10.255.255.255/10", "10.192.0.0/10"),
        ]
        let ipv6Cases = [
            ("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128", "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128"),
            ("::/0", "::/0"),
            ("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/1", "8000::/1"),
            ("1:0:0:2:0:0:3:4/128", "1::2:0:0:3:4/128"),
            ("::ffff:192.0.2.1/128", "::ffff:c000:201/128"),
            ("1:2:3:4:5:6:0:8/128", "1:2:3:4:5:6:0:8/128"),
            ("::/9", "::/9"),
            ("::/10", "::/10"),
            ("::/99", "::/99"),
            ("::/100", "::/100"),
            ("::1/127", "::/127"),
            ("::1/128", "::1/128"),
        ]
        let ipv4 = try ipv4Cases.map { try #require(IPv4Network($0.0)) }
        let ipv6 = try ipv6Cases.map { try #require(IPv6Network($0.0)) }

        #expect(ipv4Cases[0].1.utf8.count + 1 == 19)
        #expect(ipv6Cases[0].1.utf8.count + 1 == 44)
        try checkRaw(
            makeResult(.cidr, ipv4: .cidr(ipv4), ipv6: .cidr(ipv6)),
            expectedLines: ipv4Cases.map { $0.1 } + ipv6Cases.map { $0.1 }
        )
    }

    @Test("Empty and single-family raw results preserve IPv4-first order and exact line endings")
    func emptyAndFamilyPartitionedResults() throws {
        let range4 = try #require(IPv4AddressRange("203.0.113.1...203.0.113.1"))
        let range6 = try #require(IPv6AddressRange("2001:db8::1...2001:db8::1"))
        let network4 = try #require(IPv4Network("203.0.113.1/32"))
        let network6 = try #require(IPv6Network("2001:db8::1/128"))

        for includeIPv4 in [false, true] {
            for includeIPv6 in [false, true] {
                let ranges = makeResult(
                    .ranges,
                    ipv4: .ranges(includeIPv4 ? [range4] : []),
                    ipv6: .ranges(includeIPv6 ? [range6] : [])
                )
                try checkRaw(
                    ranges,
                    expectedLines: (includeIPv4 ? ["203.0.113.1...203.0.113.1"] : [])
                        + (includeIPv6 ? ["2001:db8::1...2001:db8::1"] : [])
                )
                let networks = makeResult(
                    .cidr,
                    ipv4: .cidr(includeIPv4 ? [network4] : []),
                    ipv6: .cidr(includeIPv6 ? [network6] : [])
                )
                try checkRaw(
                    networks,
                    expectedLines: (includeIPv4 ? ["203.0.113.1/32"] : [])
                        + (includeIPv6 ? ["2001:db8::1/128"] : [])
                )
            }
        }
    }

    @Test("Every prefix length and seeded random networks match the description-based byte reference")
    func allPrefixLengthsAndRandomNetworks() throws {
        var generator = RawOutputGenerator()
        var ipv4: [IPv4Network] = []
        var ipv6: [IPv6Network] = []
        for length in 0...32 {
            ipv4.append(
                IPv4Network(
                    prefix: generator.nextIPv4(),
                    prefixLength: try #require(PrefixLength<V4>(length))
                )
            )
        }
        for length in 0...128 {
            ipv6.append(
                IPv6Network(
                    prefix: generator.nextIPv6(),
                    prefixLength: try #require(PrefixLength<V6>(length))
                )
            )
        }
        for _ in 0..<256 {
            let length4 = Int(generator.next() % 33)
            let length6 = Int(generator.next() % 129)
            ipv4.append(
                IPv4Network(
                    prefix: generator.nextIPv4(),
                    prefixLength: try #require(PrefixLength<V4>(length4))
                )
            )
            ipv6.append(
                IPv6Network(
                    prefix: generator.nextIPv6(),
                    prefixLength: try #require(PrefixLength<V6>(length6))
                )
            )
        }

        try checkRaw(makeResult(.cidr, ipv4: .cidr(ipv4), ipv6: .cidr(ipv6)))
    }

    @Test("Seeded random range endpoints and singleton ranges match the description-based byte reference")
    func randomRangeBytes() throws {
        var generator = RawOutputGenerator()
        var ipv4: [IPv4AddressRange] = []
        var ipv6: [IPv6AddressRange] = []
        for index in 0..<512 {
            let first4 = generator.nextIPv4()
            let second4 = index.isMultiple(of: 8) ? first4 : generator.nextIPv4()
            let first6 = generator.nextIPv6()
            let second6 = index.isMultiple(of: 8) ? first6 : generator.nextIPv6()
            ipv4.append(
                try #require(
                    IPv4AddressRange(
                        lowerBound: IPv4Address(address: min(first4, second4)),
                        upperBound: IPv4Address(address: max(first4, second4))
                    )
                )
            )
            ipv6.append(
                try #require(
                    IPv6AddressRange(
                        lowerBound: IPv6Address(address: min(first6, second6)),
                        upperBound: IPv6Address(address: max(first6, second6))
                    )
                )
            )
        }

        try checkRaw(makeResult(.ranges, ipv4: .ranges(ipv4), ipv6: .ranges(ipv6)))
    }

    @Test("Returned Data remains independent across later long, short, and empty renders")
    func returnedDataRemainsOwned() throws {
        let maximum4 = IPv4AddressRange(IPv4Address(address: .max))
        let maximum6 = IPv6AddressRange(IPv6Address(address: .max))
        let longResult = makeResult(.ranges, ipv4: .ranges([maximum4]), ipv6: .ranges([maximum6]))
        let shortResult = makeResult(
            .ranges,
            ipv4: .ranges([IPv4AddressRange(IPv4Address(address: 0))]),
            ipv6: .ranges([IPv6AddressRange(IPv6Address(address: 0))])
        )
        let cidrResult = makeResult(
            .cidr,
            ipv4: .cidr([try #require(IPv4Network("255.255.255.255/32"))]),
            ipv6: .cidr([try #require(IPv6Network("::/0"))])
        )
        let retainedLong = try checkRaw(longResult)
        let retainedShort = try checkRaw(shortResult)
        let retainedCIDR = try checkRaw(cidrResult)
        for _ in 0..<8 {
            try checkRaw(shortResult)
            try checkRaw(longResult)
            try checkRaw(cidrResult)
            try checkRaw(makeResult(.cidr, ipv4: .cidr([]), ipv6: .cidr([])))
        }
        #expect(retainedLong == referenceData(longResult))
        #expect(retainedShort == referenceData(shortResult))
        #expect(retainedCIDR == referenceData(cidrResult))
    }

    private func makeResult(
        _ representation: OutputRepresentation,
        ipv4: FamilyMergeOutput<V4>,
        ipv6: FamilyMergeOutput<V6>
    ) -> MergeResult {
        MergeResult(
            representation: representation,
            ipv4: ipv4,
            ipv6: ipv6,
            statistics: MergeStatistics(
                representation: representation,
                outputIPv4Count: ipv4.count,
                outputIPv6Count: ipv6.count
            )
        )
    }

    private func referenceLines<Family: IPAddressFamily>(_ output: FamilyMergeOutput<Family>) -> [String] {
        switch output {
        case .ranges(let ranges):
            ranges.map(\.description)
        case .cidr(let networks):
            networks.map(\.description)
        }
    }

    private func referenceData(_ result: MergeResult) -> Data {
        let lines = referenceLines(result.ipv4) + referenceLines(result.ipv6)
        return Data((lines.isEmpty ? "" : lines.joined(separator: "\n") + "\n").utf8)
    }

    @discardableResult
    private func checkRaw(_ result: MergeResult, expectedLines: [String]? = nil) throws -> Data {
        // The oracle deliberately uses the prior description/String path, never UTF-8 writers.
        let reference = referenceData(result)
        if let expectedLines {
            let expected = Data(
                (expectedLines.isEmpty ? "" : expectedLines.joined(separator: "\n") + "\n").utf8
            )
            #expect(reference == expected)
        }
        let actual = OutputRenderer.raw(result)
        #expect(actual == reference)
        #expect(try OutputRenderer.render(result, format: .raw) == reference)
        #expect(actual.count == reference.count)
        #expect(actual.filter { $0 == 0x0A }.count == result.ipv4.count + result.ipv6.count)
        #expect(actual.allSatisfy { $0 < 0x80 })
        if result.ipv4.count + result.ipv6.count == 0 {
            #expect(actual.isEmpty)
        } else {
            #expect(actual.last == UInt8(0x0A))
            #expect(actual.dropLast().last != UInt8(0x0A))
        }
        return actual
    }
}

private struct RawOutputGenerator {
    private var state: UInt64 = 0x6A09_E667_F3BC_C909

    mutating func next() -> UInt64 {
        state = state &* 6_364_136_223_846_793_005 &+ 1_442_695_040_888_963_407
        return state
    }

    mutating func nextIPv4() -> UInt32 {
        UInt32(truncatingIfNeeded: next())
    }

    mutating func nextIPv6() -> UInt128 {
        (UInt128(next()) << 64) | UInt128(next())
    }
}
