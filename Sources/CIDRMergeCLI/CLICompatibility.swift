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

#if canImport(Darwin)
    import Darwin
    import Foundation
#else
    import FoundationEssentials
    import Glibc
#endif

/// Preserves the existing CLI text contract without loading full Foundation on Linux.
enum CLICompatibility {
    static func trimBoundaryWhitespace(_ text: Substring) -> String {
        #if canImport(Darwin)
            return text.trimmingCharacters(in: .whitespacesAndNewlines)
        #else
            // Foundation's whitespace set also contains ZERO WIDTH SPACE, which Unicode's
            // White_Space property does not. Trim scalars, including within grapheme clusters.
            let scalars = text.unicodeScalars
            var lower = scalars.startIndex
            var upper = scalars.endIndex
            while lower != upper && isBoundaryWhitespace(scalars[lower]) {
                scalars.formIndex(after: &lower)
            }
            while lower != upper {
                let previous = scalars.index(before: upper)
                guard isBoundaryWhitespace(scalars[previous]) else { break }
                upper = previous
            }
            return String(scalars[lower..<upper])
        #endif
    }

    #if !canImport(Darwin)
        private static func isBoundaryWhitespace(_ scalar: Unicode.Scalar) -> Bool {
            scalar.properties.isWhitespace || scalar.value == 0x200B
        }
    #endif

    static func percentage(_ magnitude: Double) -> String {
        #if canImport(Darwin)
            return String(format: "%.1f%%", locale: Locale(identifier: "en_US_POSIX"), magnitude)
        #else
            // The original POSIX-locale Foundation formatter rounds the shortest decimal
            // representation to even. Binary printf and multiplying by ten disagree at ties.
            // Work with decimal digits so percentages larger than Int.max also remain exact.
            let parts = String(magnitude).split(separator: "e", omittingEmptySubsequences: false)
            let exponent = parts.count == 2 ? Int(parts[1])! : 0
            let significand = Array(parts[0].utf8)
            let decimalPosition = (significand.firstIndex(of: 0x2E) ?? significand.count) + exponent
            var digits = significand.filter { $0 != 0x2E }
            let keptCount = decimalPosition + 1
            guard keptCount > 0 else { return "0.0%" }
            if keptCount >= digits.count {
                digits.append(contentsOf: repeatElement(0x30, count: keptCount - digits.count))
            } else {
                let firstDiscarded = digits[keptCount]
                let roundUp =
                    firstDiscarded > 0x35
                    || (firstDiscarded == 0x35
                        && (digits[(keptCount + 1)...].contains { $0 != 0x30 }
                            || digits[keptCount - 1] % 2 == 1))
                digits.removeSubrange(keptCount...)
                if roundUp {
                    var index = digits.count
                    var carry = true
                    while index > 0 {
                        index -= 1
                        if digits[index] < 0x39 {
                            digits[index] += 1
                            carry = false
                            break
                        }
                        digits[index] = 0x30
                    }
                    if carry { digits.insert(0x31, at: 0) }
                }
            }
            while digits.count > 2 && digits[0] == 0x30 { digits.removeFirst() }
            if digits.count == 1 { digits.insert(0x30, at: 0) }
            digits.insert(0x2E, at: digits.count - 1)
            return String(decoding: digits, as: UTF8.self) + "%"
        #endif
    }

    static func errorDescription(_ error: any Error) -> String {
        if let failure = error as? DescriptorIOFailure {
            return descriptorErrorDescription(failure)
        }
        #if canImport(Darwin)
            return error.localizedDescription
        #else
            if let cocoa = error as? CocoaError {
                return cocoaDescription(code: cocoa.code.rawValue, userInfo: cocoa.userInfo)
            }
            if let posix = error as? POSIXError {
                return "The operation could not be completed. \(String(cString: strerror(posix.code.rawValue)))"
            }
            if let localized = error as? any LocalizedError {
                if let description = localized.errorDescription { return description }
                if let reason = localized.failureReason {
                    return "The operation could not be completed. \(reason)"
                }
            }
            // These standard-library Error witnesses also underpin Foundation's bridging.
            // Preserve the actual enum case's error code instead of assuming every error is 1.
            return "The operation could not be completed. (\(error._domain) error \(error._code).)"
        #endif
    }

    private static func descriptorErrorDescription(_ failure: DescriptorIOFailure) -> String {
        let reading: Bool
        switch failure.operation {
        case .read:
            reading = true
        case .write:
            reading = false
        case .openForReading:
            // Darwin FileHandle's open initializer uses the write-error mapping even
            // for a read-only descriptor. Preserve that existing diagnostic behavior.
            #if canImport(Darwin)
                reading = false
            #else
                reading = true
            #endif
        }
        let code = cocoaCode(for: failure.code.rawValue, reading: reading)
        #if canImport(Darwin)
            var userInfo: [String: Any] = [
                NSUnderlyingErrorKey: NSError(domain: NSPOSIXErrorDomain, code: Int(failure.code.rawValue))
            ]
            if let path = failure.path { userInfo[NSFilePathErrorKey] = URL(fileURLWithPath: path).path }
            return NSError(domain: NSCocoaErrorDomain, code: code, userInfo: userInfo).localizedDescription
        #else
            return cocoaDescription(code: code, userInfo: [:])
        #endif
    }

    // Error mappings and English diagnostic strings follow swift-corelibs-foundation:
    // Sources/Foundation/{FoundationErrors,NSError}.swift. Copyright (c) 2014 - 2017
    // Apple Inc. and the Swift project authors. Apache License 2.0 with Runtime Library
    // Exception. Adapted here to render Essentials errors without NSError bridging.
    // https://github.com/swiftlang/swift-corelibs-foundation/tree/main/Sources/Foundation
    private static func cocoaCode(for code: Int32, reading: Bool) -> Int {
        if reading {
            switch code {
            case EFBIG: return 263
            case ENOENT: return 260
            case EPERM, EACCES: return 257
            default: return 256
            }
        }
        switch code {
        case ENOENT: return 4
        case EPERM, EACCES: return 513
        case ENAMETOOLONG: return 514
        case EDQUOT, ENOSPC: return 640
        case EROFS: return 642
        case EEXIST: return 516
        default: return 512
        }
    }

    #if !canImport(Darwin)
        private static func cocoaDescription(code: Int, userInfo: [String: Any]) -> String {
            if let description = userInfo["NSLocalizedDescription"] as? String { return description }
            let reason = userInfo["NSLocalizedFailureReason"] as? String ?? cocoaFailureReason(code)
            return "The operation could not be completed. " + (reason ?? "(NSCocoaErrorDomain error \(code).)")
        }

        private static func cocoaFailureReason(_ code: Int) -> String? {
            switch code {
            case 4, 260: return "The file doesn’t exist."
            case 255: return "The file couldn’t be locked."
            case 257, 513: return "You don’t have permission."
            case 258, 514: return "The file name is invalid."
            case 259: return "The file isn’t in the correct format."
            case 261, 517: return "The specified text encoding isn’t applicable."
            case 262, 518: return "The specified URL type isn’t supported."
            case 263: return "The item is too large."
            case 264: return "The text encoding of the contents couldn’t be determined."
            case 516: return "A file with the same name already exists."
            case 640: return "There isn’t enough space."
            case 642: return "The volume is read only."
            case 1024, 2048: return "The value is invalid."
            case 3072: return "The operation was cancelled."
            case 3328: return "The requested operation is not supported."
            case 3840: return "The data is not in the correct format."
            case 3841: return "The data is in a format that this application doesn’t understand."
            case 3842: return "An error occurred in the source of the data."
            case 3851: return "An error occurred in the destination for the data."
            case 3852: return "An error occurred in the content of the data."
            case 4353: return "The file is not available on iCloud yet."
            case 4354: return "There isn’t enough space in your account."
            case 4355: return "The iCloud servers might be unreachable or your settings might be incorrect."
            case 4864, 4866: return "The data isn’t in the correct format."
            case 4865: return "The data is missing."
            default: return nil
            }
        }
    #endif
}
