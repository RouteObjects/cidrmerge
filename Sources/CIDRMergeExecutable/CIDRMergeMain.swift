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

import CIDRMergeCLI

@main
enum CIDRMergeMain {
    static func main() {
        // Keep process startup separate from the importable, testable command module.
        CIDRMergeCommand.main()
    }
}
