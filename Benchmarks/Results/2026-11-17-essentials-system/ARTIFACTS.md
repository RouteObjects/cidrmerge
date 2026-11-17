# Artifact sizes and linked libraries

All sizes are exact bytes from existing receipts. Comparisons are within a platform/profile; stripping differs between platforms. Final x86-64 shipping, qualification and runtime-resolution receipts are included. All three platform indices are complete; performance comparisons remain in the separate report dataset.

| Platform | Artifact | B bytes | R3 bytes | Change |
|---|---|---:|---:|---:|
| macos | ordinary_unstripped | 2,443,496 | 2,955,992 | +20.97% |
| macos | ordinary_stripped | 1,290,512 | 1,515,776 | +17.46% |
| macos | shipping_stripped | 1,290,512 | 1,515,776 | +17.46% |
| arm64 | ordinary_unstripped | 17,304,928 | 19,099,072 | +10.37% |
| arm64 | ordinary_stripped | 3,322,808 | 3,608,192 | +8.59% |
| arm64 | shipping_stripped | 60,849,832 | 17,260,632 | -71.63% |
| x86_64 | ordinary_unstripped | 17,694,808 | 19,479,048 | +10.08% |
| x86_64 | ordinary_stripped | 3,721,800 | 4,024,520 | +8.13% |
| x86_64 | shipping_stripped | 62,619,384 | 18,837,680 | -69.92% |
| x86_64 | shipping_unstripped | 89,338,824 | 41,791,264 | -53.22% |

| Platform | Dependent-file closure | B bytes | R3 bytes |
|---|---|---:|---:|
| macos | ordinary | Not recorded | Not recorded |
| macos | shipping | Not recorded | Not recorded |
| arm64 | ordinary | 84,535,576 | 30,724,480 |
| arm64 | shipping | 5,285,608 | 5,285,608 |
| x86_64 | ordinary | 85,108,832 | 31,621,792 |
| x86_64 | shipping | Not recorded | Not recorded |

Dependent-file sums exclude the executable and describe complete on-disk files, not resident memory, loaded pages or bytes embedded in a static executable. macOS system/shared-cache dylib byte sums were not recorded. x86-64 ordinary sums agree between the recorded per-file runtime sizes and the completed actual-resolution receipt; shipping sums were not recorded in either retrieved shipping receipt.

macOS retains Foundation and CryptoKit and adds the direct `libswift_errno.dylib` dependency in R3. The ordinary Linux closures on both architectures remove `libFoundation.so`, `libFoundationInternationalization.so`, `lib_FoundationICU.so` and `libswiftDispatch.so`. They retain FoundationEssentials and still transitively include `libdispatch.so` and `libBlocksRuntime.so`. ARM shipping B and R3 have the same five system-library dependencies; neither has dynamic Swift/Foundation dependencies. The x86 shipping B and R3 receipts likewise list the same five system libraries (`libm`, `libstdc++`, `libgcc_s`, `libc` and the loader), with no dynamic Swift/Foundation dependencies.

Source receipts: `macos/ordinary-artifacts/receipts.json`; `macos/release-style/control/{artifacts,artifacts-R3}.json`; `arm64/runtime/{manifest,release-style-R3}.json`; `x86_64/retrieved/metadata-01/control/build-tests-{B,R3}/{B,R3}-build-release.json`; `x86_64/retrieved/metadata-01/control/release-style-B/complete.json`; `x86_64/retrieved/metadata-02/control/release-style-R3/complete.json`. `ARTIFACTS.json` records exact per-field provenance, hashes copied from these receipts, complete library sets and differences.

## Linux tiny-process RSS limitation

Independent ARM64 and x86-64 `/bin/true` controls passed with three observations per parent-memory group, after timing ended. Each host used its unchanged executable and frozen Popen/wait4 runner:

| Host | Extra Python parent allocation | Reported child peak RSS bytes | Median MiB |
|---|---|---|---:|
| ARM64 | 0 MiB | 18,092,032, 18,092,032, 18,092,032 | 17.254 |
| ARM64 | 32 MiB | 51,695,616, 51,781,632, 51,781,632 | 49.383 |
| ARM64 | 96 MiB | 118,812,672, 118,882,304, 118,882,304 | 113.375 |
| x86-64 | 0 MiB | 20,402,176, 20,402,176, 20,402,176 | 19.457 |
| x86-64 | 32 MiB | 52,670,464, 52,670,464, 52,801,536 | 50.230 |
| x86-64 | 96 MiB | 119,832,576, 119,832,576, 119,963,648 | 114.281 |

Unchanged `/bin/true` reports larger lifetime peak RSS when parent Python memory is increased on both hosts, confirming inherited/pre-exec parent-memory influence in this measurement method. Tiny-process peaks are not isolated application-only RSS. Do not subtract the control floor or correct, pool, or discard original samples. These are measurement-method controls, not cidrmerge performance. They do not invalidate elapsed measurements or establish equality of application-only memory.

Evidence: `arm64/harness-controls/rss-fork-floor/summary.json` and `x86_64/retrieved/final-v2/correctness/rss-fork-floor/summary.json`. `ARTIFACTS.json` retains all eighteen observations in `startup_rss_controls`; the earlier singular ARM field remains for compatibility.

## x86-64 actual runtime resolution

The post-timing check used the unchanged measurement `LD_LIBRARY_PATH`. B resolves 20 dependent files totaling 85,108,832 bytes; R3 resolves 16 totaling 31,621,792 bytes. All resolved hashes match both the premeasurement originals and preserved copies. Swift runtime libraries load from the frozen runtime directory, while `libstdc++.so.6` and the ELF interpreter resolve through host paths. The latter are recorded, hash-verified host dependencies, not frozen-directory loads. File-byte sums are not RSS.

Evidence: `x86_64/retrieved/final-v2/control/actual-runtime-closure.json`; compact names, bytes, hashes and actual resolution flags are copied into `ARTIFACTS.json`. Final x86 qualification is independently summarized in `COMPATIBILITY.md` and `analysis/x86_64-report-index.json`.
