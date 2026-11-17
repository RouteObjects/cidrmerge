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

import SystemPackage

#if canImport(Darwin)
    import Darwin
#endif

#if canImport(FoundationEssentials)
    import FoundationEssentials
#else
    import Foundation
#endif

/// Keeps the failed operation with its captured error number for compatible diagnostics.
struct DescriptorIOFailure: Error {
    enum Operation: Sendable {
        case openForReading
        case read
        case write
    }

    let code: Errno
    let operation: Operation
    let path: String?
}

enum DescriptorIO {
    static func openForReading(_ path: String) throws -> FileDescriptor {
        do {
            let descriptor = try FileDescriptor.open(FilePath(URL(fileURLWithPath: path).path), .readOnly)
            #if canImport(Darwin)
                // CHANGE: Darwin FileHandle rejects directory operands while opening them.
                // Check the opened descriptor so a path replacement cannot change this decision.
                var metadata = stat()
                while fstat(descriptor.rawValue, &metadata) != 0 {
                    let error = Errno(rawValue: errno)
                    if error == .interrupted { continue }
                    try? descriptor.close()
                    throw error
                }
                if metadata.st_mode & S_IFMT == S_IFDIR {
                    // Darwin FileHandle's directory rejection reports the inherited errno,
                    // even when it is zero. Capture that value before closing the descriptor
                    // to preserve this platform diagnostic quirk rather than invent an error.
                    let error = Errno(rawValue: errno)
                    try? descriptor.close()
                    throw error
                }
            #endif
            return descriptor
        } catch let error as Errno {
            throw DescriptorIOFailure(code: error, operation: .openForReading, path: path)
        }
    }

    static func read(from descriptor: FileDescriptor, into buffer: UnsafeMutableRawBufferPointer) throws -> Int {
        do {
            // CHANGE: Read directly into caller-owned storage and retry interrupted system calls.
            return try descriptor.read(into: buffer)
        } catch let error as Errno {
            throw DescriptorIOFailure(code: error, operation: .read, path: nil)
        }
    }

    static func readToEnd(from descriptor: FileDescriptor) throws -> Data {
        // CHANGE: Searchbot still owns the complete document, but its read scratch is reusable.
        let buffer = UnsafeMutableRawBufferPointer.allocate(byteCount: 64 * 1_024, alignment: 16)
        defer { buffer.deallocate() }
        var result = Data()
        while true {
            let count = try read(from: descriptor, into: buffer)
            guard count > 0 else { return result }
            result.append(buffer.bindMemory(to: UInt8.self).baseAddress!, count: count)
        }
    }

    static func write(_ data: Data, to descriptor: FileDescriptor) throws {
        do {
            // CHANGE: Borrow the existing contiguous output bytes; writeAll handles short writes.
            try data.withUnsafeBytes { (buffer: UnsafeRawBufferPointer) in
                _ = try descriptor.writeAll(buffer)
            }
        } catch let error as Errno {
            throw DescriptorIOFailure(code: error, operation: .write, path: nil)
        }
    }
}
