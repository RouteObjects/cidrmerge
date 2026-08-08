# ``CIDRMergeCore``

Build deterministic, mixed-family exact address coverage from canonical
swift-cidr values.

## Overview

CIDRMergeCore is the reusable library behind the offline `cidrmerge` policy
compiler. ``CIDRMergeCoverage`` partitions input by address family and delegates
range normalization, containment, and range-to-CIDR summarization to
[`swift-cidr`](https://github.com/RouteObjects/swift-cidr).

Coverage retains exact address membership: duplicate, contained, overlapping,
and adjacent intervals coalesce, but an uncovered gap is never filled to make
output shorter. Family-erased results are deterministic and always order IPv4
before IPv6.

The package also includes an executable that reads local files or standard
input. Its implementation target remains private to the package, but the
workflow article below documents how that executable compiles compatible
crawler-prefix data into the same exact coverage model.

## Topics

### Exact Coverage

- ``CIDRMergeCoverage``

### Package Workflows

- <doc:CompilingSearchbotPrefixLists>
