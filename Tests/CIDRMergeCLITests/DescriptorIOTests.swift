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
import SystemPackage
import Testing

@testable import CIDRMergeCLI

struct DescriptorIOTests {
    @Test("Descriptor reads preserve all bytes across small buffers and EOF")
    func boundedReads() throws {
        let pipe = Pipe()
        let expected = Data((0..<251).map(UInt8.init))
        try pipe.fileHandleForWriting.write(contentsOf: expected)
        try pipe.fileHandleForWriting.close()
        defer { try? pipe.fileHandleForReading.close() }
        let descriptor = FileDescriptor(rawValue: pipe.fileHandleForReading.fileDescriptor)
        let buffer = UnsafeMutableRawBufferPointer.allocate(byteCount: 7, alignment: 16)
        defer { buffer.deallocate() }
        var received = Data()
        while true {
            let count = try DescriptorIO.read(from: descriptor, into: buffer)
            if count == 0 { break }
            #expect(count > 0 && count <= 7)
            received.append(contentsOf: buffer[..<count])
        }
        #expect(received == expected)
        #expect(try DescriptorIO.read(from: descriptor, into: buffer) == 0)
        // CHANGE: The reader borrows standard-input-style descriptors and must not close them.
        let duplicate = try descriptor.duplicate()
        try duplicate.close()
    }

    @Test("Descriptor output preserves exact bytes and leaves borrowed output open")
    func outputBytes() throws {
        let pipe = Pipe()
        defer { try? pipe.fileHandleForReading.close() }
        let descriptor = FileDescriptor(rawValue: pipe.fileHandleForWriting.fileDescriptor)
        let expected = Data([0, 10, 13, 127, 128, 255])
        try DescriptorIO.write(expected, to: descriptor)
        try DescriptorIO.write(Data(), to: descriptor)
        let duplicate = try descriptor.duplicate()
        try duplicate.close()
        try pipe.fileHandleForWriting.close()
        #expect(try pipe.fileHandleForReading.readToEnd() == expected)
    }

    @Test("Descriptor failures retain the captured error and failed operation")
    func capturedFailures() throws {
        let descriptor = FileDescriptor(rawValue: -1)
        let buffer = UnsafeMutableRawBufferPointer.allocate(byteCount: 16, alignment: 16)
        defer { buffer.deallocate() }
        do {
            _ = try DescriptorIO.read(from: descriptor, into: buffer)
            Issue.record("Reading an invalid descriptor unexpectedly succeeded")
        } catch let error as DescriptorIOFailure {
            #expect(error.code == .badFileDescriptor)
            #expect(error.operation == .read)
            #expect(error.path == nil)
        }
        do {
            try DescriptorIO.write(Data([1]), to: descriptor)
            Issue.record("Writing an invalid descriptor unexpectedly succeeded")
        } catch let error as DescriptorIOFailure {
            #expect(error.code == .badFileDescriptor)
            #expect(error.operation == .write)
            #expect(error.path == nil)
        }
    }
}
