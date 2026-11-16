# ARM64 Linux raw UTF-8 code generation

The ordinary candidate Release binary's `OutputRenderer.raw` calls the concrete IPv4 and IPv6 append closures. Each closure contains two direct calls to the corresponding public address writer for range endpoints and one direct call to the public CIDR writer for network entries. Neither candidate closure calls a description getter. The temporary storage is passed from the raw renderer's stack frame in this build; this is observed code generation, not a universal allocation guarantee.

Both ordinary baseline/candidate selected functions and their complete original assembly/symbol captures are preserved. `summary.json` binds binary and capture hashes, concrete caller/callee names, addresses and assembly line numbers. The original source still returns a complete `Data`; output reservation, merge arrays, JSON and commitment semantics were not changed. This inspection does not execute a target or establish a throughput, RSS or zero-allocation claim.
