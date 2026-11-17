Borrowed-line regression: source-only investigation

This analysis is limited to frozen R3/S2 source and the installed Xcode 27.2 SDK Swift interface. No new build, profile, timing, binary inspection, or large-file hashing was performed. The parent reported a 12–32% Mac elapsed regression in ten text configurations for S2 versus R3, with a fixed follow-up running; that measurement was not independently analyzed here. Cross-platform S2 conclusions remain pending.

The working recommendation is to retain R3 as the provisional preferred candidate, subject to the follow-up and platform results. R3 reuses bounded read scratch and the existing concrete Array line parser. S2 adds a distinct generic/slice optimization; its regression does not invalidate the earlier independent scratch-buffer stage. Preserve S2's complete observations rather than mixing an unmeasured correction into its results.

The relevant application delta is [TextInput.swift](../sources/S2/Sources/CIDRMergeCLI/TextInput.swift), lines218–308, compared with [R3](../sources/R3/Sources/CIDRMergeCLI/TextInput.swift). S2 supplies `Slice<UnsafeRawBufferPointer>` for complete lines and changes `consumeLine` from `[UInt8]` to a generic RandomAccessCollection constrained to Int indices. The ASCII loop still iterates `rawBytes.indices`. Its String initializer receives a slice of the same base type. R3 instead consumes its reusable `[UInt8]` pending buffer and supplies ArraySlice to String.

The inspected SDK interface is:

`/Applications/Xcode-27.2.0.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/lib/swift/Swift.swiftmodule/arm64e-apple-macos.swiftinterface`

| Verified interface fact | Lines | Implication |
| --- | --- | --- |
| UTF8 `String(decoding:as:)` first tries `withContiguousStorageIfAvailable`; the Array-materializing fallback is used only after contiguous paths fail. | 29112–29164 | A generic parameter does not itself imply a temporary Array. |
| Slice forwards contiguous storage to its base, calculates the slice offset and returns a rebased typed buffer. | 22304–22311 | Slicing does not inherently lose contiguous-storage support. |
| UnsafeRawBufferPointer supplies contiguous storage using a scoped UInt8 memory rebound. | 47962–47966 | The raw-buffer slice path can use the same contiguous UTF8 String constructor. No mandatory fallback Array allocation was established. |
| ArraySlice supplies contiguous storage via its unsafe buffer access. | 2056–2062 | R3 also uses a contiguous input path. |
| Slice's `indices` getter has no exported `@inlinable` body in this interface. | 22275–22277 | A generic Slice.indices call can remain an opaque per-line call, unlike a visible direct index range. |
| RandomAccessCollection's Range-valued `indices` getter is inlinable and constructs `startIndex..<endIndex`. | 18282–18286 | The concrete Array path gives the optimizer a directly visible range. |
| Slice element subscript performs `_failEarlyRangeCheck` before reading the base element. | 22263–22268 | Additional range checks exist at the source level. |
| Slice forwards early range checks to its base; the general Collection implementation performs preconditions. Raw-buffer Collection does not override that check. | 22298–22303; 5104–5122; 47789–47854 | S2's raw-buffer slices can retain real per-element range checks unless optimization proves them redundant. |
| Array's `_failEarlyRangeCheck` implementation is empty. | 821–826 | Array uses its own optimized bounds mechanisms instead of this extra generic check. |

The strongest source-supported hypothesis is the combination of opaque `Slice.indices` and per-element slice range checks. If the optimizer cannot relate the opaque returned Range to the slice's stored bounds, it may keep redundant tests inside the ASCII byte scan. A per-line generic getter call and additional slice offset/range work can also contribute. This explains a plausible mechanism; source/interface inspection does not prove the generated loop retains those checks or quantify their cost.

Generic specialization, closure inlining and code layout are additional possibilities, but none has been established. Seeing a generic `consumeLine` declaration is not evidence that release specialization failed. Scoped memory rebinding is not a 64-KiB data copy, and no such copy should be claimed from the interface alone.

R3 already reserves pending storage and clears it with `keepingCapacity: true`. For ordinary short ASCII lines, S2 therefore removes per-byte copying into reused capacity; it does not eliminate a newly allocated Array on every line. S2 still constructs one owned token String and calls the existing parsers. Both variants scan for line boundaries and scan each token for ASCII/comment handling. The expected benefit is narrower than eliminating a per-line heap allocation.

If a later experiment is warranted, the smallest discriminating change is to replace only `rawBytes.indices` with `rawBytes.startIndex..<rawBytes.endIndex`, preserving every other S2 choice. That avoids the opaque Slice.indices accessor and may allow bounds-check elimination. Inspect the resulting release code after timing work is finished, then run a separately named matched candidate. A concrete rebased typed-buffer parser overload is a second distinct experiment if needed. Neither change is implemented or validated by this investigation.
