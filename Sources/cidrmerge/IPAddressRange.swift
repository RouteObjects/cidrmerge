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

typealias IPv4AddressRange = IPAddressRange<V4>
typealias IPv6AddressRange = IPAddressRange<V6>

/// An inclusive, ordered interval of addresses from one IP address family.
///
/// Endpoints are address identities rather than address-with-prefix values. Construction therefore
/// rebuilds each endpoint with the family's host prefix (`/32` for IPv4 or `/128` for IPv6). An
/// explicitly supplied non-host prefix length is intentionally discarded.
struct IPAddressRange<Family: IPAddressFamily>: Sendable, Hashable, LosslessStringConvertible,
    Codable
{
    private let lowerAddress: Family.Storage
    private let upperAddress: Family.Storage

    var lowerBound: IPAddress<Family> {
        IPAddress(address: lowerAddress)
    }

    var upperBound: IPAddress<Family> {
        IPAddress(address: upperAddress)
    }

    init?(lowerBound: IPAddress<Family>, upperBound: IPAddress<Family>) {
        guard lowerBound.address <= upperBound.address else { return nil }

        // CHANGE: A range endpoint is one address; retaining CIDR prefix context would make equal
        // address intervals hash differently even though they cover the same addresses.
        self.lowerAddress = lowerBound.address
        self.upperAddress = upperBound.address
    }

    init(_ address: IPAddress<Family>) {
        self.lowerAddress = address.address
        self.upperAddress = address.address
    }

    init<Prefix: IPPrefix>(covering prefix: Prefix) where Prefix.Family == Family {
        self.lowerAddress = prefix.first.address
        self.upperAddress = prefix.last.address
    }

    init?(_ description: String) {
        guard let delimiter = description.range(of: "..."),
            description[delimiter.upperBound...].range(of: "...") == nil
        else {
            return nil
        }

        let lowerText = String(description[..<delimiter.lowerBound])
        let upperText = String(description[delimiter.upperBound...])
        guard !lowerText.isEmpty,
            !upperText.isEmpty,
            let lowerAddress = Family.parseAddress(lowerText),
            let upperAddress = Family.parseAddress(upperText)
        else {
            return nil
        }

        self.init(
            lowerBound: IPAddress(address: lowerAddress),
            upperBound: IPAddress(address: upperAddress)
        )
    }

    var description: String {
        "\(Family.formatAddress(lowerAddress))...\(Family.formatAddress(upperAddress))"
    }

    var closedRange: ClosedRange<IPAddress<Family>> {
        lowerBound...upperBound
    }

    /// The number of covered addresses when the result fits in `UInt128`.
    var rangeSizeIfRepresentable: UInt128? {
        // CHANGE: Widen IPv4 before adding one so its complete address space remains representable.
        let lower = UInt128(exactly: lowerAddress)!
        let upper = UInt128(exactly: upperAddress)!
        let (size, overflow) = (upper - lower).addingReportingOverflow(1)
        return overflow ? nil : size
    }

    func contains(_ address: IPAddress<Family>) -> Bool {
        lowerAddress <= address.address && address.address <= upperAddress
    }

    func contains(_ other: Self) -> Bool {
        lowerAddress <= other.lowerAddress && other.upperAddress <= upperAddress
    }

    func overlaps(_ other: Self) -> Bool {
        lowerAddress <= other.upperAddress && other.lowerAddress <= upperAddress
    }

    func isAdjacent(to other: Self) -> Bool {
        areSuccessive(upperAddress, other.lowerAddress)
            || areSuccessive(other.upperAddress, lowerAddress)
    }

    func merged(with other: Self) -> Self? {
        guard overlaps(other) || isAdjacent(to: other) else { return nil }

        return Self(
            uncheckedLowerAddress: min(lowerAddress, other.lowerAddress),
            upperAddress: max(upperAddress, other.upperAddress)
        )
    }

    /// Coalesces a collection into the smallest sorted list with the same exact address coverage.
    static func coalescing<Ranges: Sequence>(_ ranges: Ranges) -> [Self]
    where Ranges.Element == Self {
        let sorted = ranges.sorted { lhs, rhs in
            if lhs.lowerAddress == rhs.lowerAddress {
                return lhs.upperAddress > rhs.upperAddress
            }
            return lhs.lowerAddress < rhs.lowerAddress
        }
        guard sorted.count > 1 else { return sorted }

        var result: [Self] = []
        result.reserveCapacity(sorted.count)
        var current = sorted[0]

        for range in sorted.dropFirst() {
            // CHANGE: Sorted input only needs a forward boundary comparison. Keeping one active
            // interval avoids repeated result-array mutation for heavily subsumed data.
            if current.connectsToFollowing(range) {
                current = Self(
                    uncheckedLowerAddress: current.lowerAddress,
                    upperAddress: max(current.upperAddress, range.upperAddress)
                )
            } else {
                result.append(current)
                current = range
            }
        }
        result.append(current)

        return result
    }

    init(from decoder: any Decoder) throws {
        let container = try decoder.singleValueContainer()
        let description = try container.decode(String.self)
        guard let range = Self(description) else {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Invalid \(Family.familyName) address range '\(description)'."
            )
        }
        self = range
    }

    func encode(to encoder: any Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(description)
    }

    private init(
        uncheckedLowerAddress lowerAddress: Family.Storage,
        upperAddress: Family.Storage
    ) {
        self.lowerAddress = lowerAddress
        self.upperAddress = upperAddress
    }

    private func areSuccessive(_ lower: Family.Storage, _ upper: Family.Storage) -> Bool {
        let (successor, overflow) = lower.addingReportingOverflow(1)
        return !overflow && successor == upper
    }

    private func connectsToFollowing(_ other: Self) -> Bool {
        other.lowerAddress <= upperAddress || areSuccessive(upperAddress, other.lowerAddress)
    }
}

/// A family-erased inclusive address interval.
enum AnyIPAddressRange: Sendable, Hashable, CustomStringConvertible,
    CustomDebugStringConvertible, LosslessStringConvertible, Codable
{
    case v4(IPv4AddressRange)
    case v6(IPv6AddressRange)

    init(_ range: IPv4AddressRange) {
        self = .v4(range)
    }

    init(_ range: IPv6AddressRange) {
        self = .v6(range)
    }

    init(_ address: AnyIPAddress) {
        switch address {
        case .v4(let address):
            self = .v4(IPv4AddressRange(address))
        case .v6(let address):
            self = .v6(IPv6AddressRange(address))
        }
    }

    init(covering network: AnyIPNetwork) {
        switch network {
        case .v4(let network):
            self = .v4(IPv4AddressRange(covering: network))
        case .v6(let network):
            self = .v6(IPv6AddressRange(covering: network))
        }
    }

    init?(_ description: String) {
        self.init(description, parseOrder: .ipv4ThenIPv6)
    }

    init?(
        _ description: String,
        parseOrder: AddressFamilyParseOrder = .ipv4ThenIPv6
    ) {
        switch parseOrder {
        case .ipv4ThenIPv6:
            if let range = IPv4AddressRange(description) {
                self = .v4(range)
                return
            }
            if let range = IPv6AddressRange(description) {
                self = .v6(range)
                return
            }
        case .ipv6ThenIPv4:
            if let range = IPv6AddressRange(description) {
                self = .v6(range)
                return
            }
            if let range = IPv4AddressRange(description) {
                self = .v4(range)
                return
            }
        }
        return nil
    }

    var ianaValue: Int32 {
        switch self {
        case .v4: V4.ianaValue
        case .v6: V6.ianaValue
        }
    }

    var familyName: String {
        switch self {
        case .v4: V4.familyName
        case .v6: V6.familyName
        }
    }

    var isIPv4: Bool {
        if case .v4 = self { return true }
        return false
    }

    var isIPv6: Bool {
        if case .v6 = self { return true }
        return false
    }

    var lowerBound: AnyIPAddress {
        switch self {
        case .v4(let range): AnyIPAddress(range.lowerBound)
        case .v6(let range): AnyIPAddress(range.lowerBound)
        }
    }

    var upperBound: AnyIPAddress {
        switch self {
        case .v4(let range): AnyIPAddress(range.upperBound)
        case .v6(let range): AnyIPAddress(range.upperBound)
        }
    }

    var rangeSizeIfRepresentable: UInt128? {
        switch self {
        case .v4(let range): range.rangeSizeIfRepresentable
        case .v6(let range): range.rangeSizeIfRepresentable
        }
    }

    var v4: IPv4AddressRange? {
        guard case .v4(let range) = self else { return nil }
        return range
    }

    var v6: IPv6AddressRange? {
        guard case .v6(let range) = self else { return nil }
        return range
    }

    func contains(_ address: AnyIPAddress) -> Bool {
        switch (self, address) {
        case (.v4(let range), .v4(let address)):
            range.contains(address)
        case (.v6(let range), .v6(let address)):
            range.contains(address)
        default:
            false
        }
    }

    func contains(_ other: Self) -> Bool {
        switch (self, other) {
        case (.v4(let lhs), .v4(let rhs)):
            lhs.contains(rhs)
        case (.v6(let lhs), .v6(let rhs)):
            lhs.contains(rhs)
        default:
            false
        }
    }

    func overlaps(_ other: Self) -> Bool {
        switch (self, other) {
        case (.v4(let lhs), .v4(let rhs)):
            lhs.overlaps(rhs)
        case (.v6(let lhs), .v6(let rhs)):
            lhs.overlaps(rhs)
        default:
            false
        }
    }

    func isAdjacent(to other: Self) -> Bool {
        switch (self, other) {
        case (.v4(let lhs), .v4(let rhs)):
            lhs.isAdjacent(to: rhs)
        case (.v6(let lhs), .v6(let rhs)):
            lhs.isAdjacent(to: rhs)
        default:
            false
        }
    }

    func merged(with other: Self) -> Self? {
        switch (self, other) {
        case (.v4(let lhs), .v4(let rhs)):
            lhs.merged(with: rhs).map(Self.v4)
        case (.v6(let lhs), .v6(let rhs)):
            lhs.merged(with: rhs).map(Self.v6)
        default:
            nil
        }
    }

    static func coalescing<Ranges: Sequence>(_ ranges: Ranges) -> [Self]
    where Ranges.Element == Self {
        var ipv4: [IPv4AddressRange] = []
        var ipv6: [IPv6AddressRange] = []

        for range in ranges {
            switch range {
            case .v4(let range): ipv4.append(range)
            case .v6(let range): ipv6.append(range)
            }
        }

        // CHANGE: Family partitioning makes the erased result deterministic without introducing
        // mixed-family ordering or arithmetic into the family-bound range engine.
        return IPv4AddressRange.coalescing(ipv4).map(Self.v4)
            + IPv6AddressRange.coalescing(ipv6).map(Self.v6)
    }

    var description: String {
        switch self {
        case .v4(let range): range.description
        case .v6(let range): range.description
        }
    }

    var debugDescription: String {
        switch self {
        case .v4(let range): "AnyIPAddressRange.v4(\(range.description))"
        case .v6(let range): "AnyIPAddressRange.v6(\(range.description))"
        }
    }

    init(from decoder: any Decoder) throws {
        let container = try decoder.singleValueContainer()
        let description = try container.decode(String.self)
        guard let range = Self(description) else {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Invalid mixed-family IP address range '\(description)'."
            )
        }
        self = range
    }

    func encode(to encoder: any Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(description)
    }
}
