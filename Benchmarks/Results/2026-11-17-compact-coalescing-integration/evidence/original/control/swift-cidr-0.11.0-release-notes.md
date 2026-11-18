# swift-cidr 0.11.0

Changes since 0.10.1.

## Compact coalescing storage

`IPAddressRange.coalescing(_:)` compacts its sorted array in place. When no
ranges disappear, it returns that storage directly. When ranges merge, it
copies the reduced result into fresh storage, avoiding an input-sized retained
result buffer after substantial collapse.

Exact coverage, ascending order, duplicate/containment/adjacency handling,
maximum endpoints, caller-owned values and the generic Sequence API are
preserved. The accepted policy is deterministic and has no shrink threshold.
Five focused tests cover single-pass input, aliases, boundary and sparse-merge
cases across IPv4, IPv6 and a custom UInt16 family.

The preserved three-platform experiment is workload-specific. It measured a
27.15% macOS range-derived peak-RSS reduction and eliminated the initial
prototype's observed Linux range-derived memory regressions. Its x86-64 sparse-merge paired CPU-time medians of +2.39% initially and +3.34%
in the separate follow-up remain an accepted tradeoff. These historical
measurements are not a promise of a general speedup or identical RSS savings
for every application.

## Borrowed octet initializers

Add failable IPv4 and IPv6 `init(octets: Span<UInt8>, prefixLength:)` overloads.
They require exactly four or sixteen network-byte-order octets, preserve an
explicit prefix and host bits, and copy the address into an owned value without
retaining borrowed storage. Invalid widths return nil.

Swift 6.4 and later use checked RawSpan loads; Swift 6.2/6.3 use safe indexed
reads through the existing fixed-size octet constructors. The octet adapters
retain their Apple OS 26 availability. The package's Swift 6.2 minimum,
macOS 15/iOS 18 deployment floors, four library products and dependency pins
are unchanged.

## Validation

Fresh qualification of the released source tree passed 311 Debug and 311
Release tests on macOS ARM64, native ARM64 Linux and x86-64 Linux with Swift
6.4.2. Swift 6.2.4 ARM64 Debug/Release also passed all 311 tests each. All four
products and Apple deployment-floor builds passed; source and dependency pins
remained unchanged.

The complete macOS default benchmark threshold check reported two improvements
and no regression deviations. Its improvement-only exit status and all 79
unchanged historical thresholds are preserved. Four new Span cases were observed
separately: allocation/ARC percentiles were zero, with isolated malloc samples
retained, so this is not an unconditional zero-allocation claim.

[Final merged-commit CI](https://github.com/RouteObjects/swift-cidr/actions/runs/44233125016)
passed all five jobs, including minimum-toolchain and macOS 15 compatibility
checks and every benchmark build under Swift 6.3. The optional CPU/NIO research
benchmark targets retain existing actor-isolation build errors under Swift
6.4.2; default/summarization/Profile benchmark builds passed on that toolchain.

- [Compact-coalescing implementation and integration](https://github.com/RouteObjects/swift-cidr/pull/25)
- [Accepted experiment and limitations](https://github.com/RouteObjects/swift-cidr/blob/0.11.0/Benchmarks/Results/2026-11-16-compact-coalescing/RESULTS.md)
- [Span octet API implementation](https://github.com/RouteObjects/swift-cidr/pull/24)
- [Full comparison](https://github.com/RouteObjects/swift-cidr/compare/0.10.1...0.11.0)
