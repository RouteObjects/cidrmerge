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

import Foundation

@main
enum CorpusGenerator {
    static func main() throws {
        let arguments = CommandLine.arguments
        guard arguments.count == 3,
            let scenario = Scenario(rawValue: arguments[1]),
            let count = Int(arguments[2]),
            count > 0
        else {
            throw GeneratorError.usage
        }

        var generator = Generator(scenario: scenario, count: count)
        try generator.write(to: .standardOutput)
    }
}

private struct Generator {
    let scenario: Scenario
    let count: Int
    private var randomState: UInt64 = 0xC1D2_4E20_2607_11
    private var buffer = Data()

    init(scenario: Scenario, count: Int) {
        self.scenario = scenario
        self.count = count
        buffer.reserveCapacity(64 * 1_024)
    }

    mutating func write(to handle: FileHandle) throws {
        for index in 0..<count {
            append(line(at: index))
            if buffer.count >= 64 * 1_024 {
                try handle.write(contentsOf: buffer)
                buffer.removeAll(keepingCapacity: true)
            }
        }
        if !buffer.isEmpty {
            try handle.write(contentsOf: buffer)
        }
    }

    private mutating func line(at index: Int) -> String {
        switch scenario {
        case .disjoint:
            return ipv4(UInt32(truncatingIfNeeded: index &* 2)) + "/32"
        case .siblings:
            return ipv4(UInt32(truncatingIfNeeded: index)) + "/32"
        case .subsumed:
            switch index % 4 {
            case 0:
                return "10.0.0.0/8"
            case 1:
                return "10.\((index >> 8) & 0xFF).\(index & 0xFF).0/24"
            case 2:
                return "10.0.0.0/8"
            default:
                return "10.\((index >> 8) & 0xFF).\(index & 0xFF).1/32"
            }
        case .bgpLike:
            let lengths = [24, 24, 24, 24, 23, 22, 21, 20, 19, 18, 16, 25, 26, 27, 32]
            return randomizedIPv4(prefixLength: lengths[Int(nextRandom() % UInt64(lengths.count))])
        case .rpkiLike:
            let lengths = [24, 24, 24, 23, 22, 20, 16, 21, 25, 32]
            if index > 0, index % 7 == 0 {
                return "203.0.113.0/24"
            }
            return randomizedIPv4(prefixLength: lengths[Int(nextRandom() % UInt64(lengths.count))])
        case .mixed:
            if index.isMultiple(of: 2) {
                return ipv4(UInt32(truncatingIfNeeded: index &* 2)) + "/32"
            }
            let value = UInt64(index)
            return "2001:db8:\(String(value >> 16, radix: 16)):\(String(value & 0xFFFF, radix: 16))::/64"
        }
    }

    private mutating func randomizedIPv4(prefixLength: Int) -> String {
        let address = UInt32(truncatingIfNeeded: nextRandom())
        let mask = prefixLength == 0 ? UInt32(0) : UInt32.max << (32 - prefixLength)
        return ipv4(address & mask) + "/\(prefixLength)"
    }

    private func ipv4(_ address: UInt32) -> String {
        "\((address >> 24) & 0xFF).\((address >> 16) & 0xFF).\((address >> 8) & 0xFF).\(address & 0xFF)"
    }

    private mutating func nextRandom() -> UInt64 {
        randomState = randomState &* 6_364_136_223_846_793_005 &+ 1_442_695_040_888_963_407
        return randomState
    }

    private mutating func append(_ line: String) {
        buffer.append(contentsOf: line.utf8)
        buffer.append(0x0A)
    }
}

private enum Scenario: String {
    case disjoint
    case siblings
    case subsumed
    case bgpLike = "bgp-like"
    case rpkiLike = "rpki-like"
    case mixed
}

private enum GeneratorError: Error, CustomStringConvertible {
    case usage

    var description: String {
        """
        Usage: CorpusGenerator <scenario> <count>
        Scenarios: disjoint, siblings, subsumed, bgp-like, rpki-like, mixed
        """
    }
}
