# Compiling Searchbot Prefix Lists

Compile saved crawler-prefix JSON into deterministic ranges or CIDR networks
without adding network access to the merge operation.

## Understand the Input Grammar

`--input-format searchbot` identifies the de facto Google/Bing/Apple/OpenAI-
compatible crawler-prefix JSON grammar. It is not a formal standard, a generic
vendor decoder, or proof that a local document came from a particular publisher.

Each operand is one complete UTF-8 JSON document with a top-level `prefixes`
array. Every entry selects exactly one string-valued `ipv4Prefix` or
`ipv6Prefix`:

```json
{
  "creationTime": "2026-01-01T00:00:00Z",
  "prefixes": [
    { "ipv4Prefix": "192.0.2.0/24" },
    { "ipv6Prefix": "2001:db8::/32" }
  ]
}
```

The example uses IPv4 and IPv6 documentation prefixes. `creationTime` and other
unknown metadata are ignored. Missing, ambiguous, duplicate, wrong-family, or
non-string prefix members reject the complete operation before output is
committed.

## Follow the Offline Pipeline

The selected grammar affects only input decoding. All accepted prefixes then
enter the same swift-cidr-backed exact-coverage and rendering pipeline:

```text
saved UTF-8 JSON
        |
        v
searchbot grammar decode
        |
        v
canonical swift-cidr ranges
        |
        v
mixed-family exact coverage
        |
        +----> ranges ----+
        |                 |
        +----> CIDRs -----+----> raw text or JSON
```

The result preserves address membership rather than source metadata, publisher
identity, or original prefix fragmentation. Output is deterministic, with IPv4
before IPv6.

## Acquire, Then Compile

Download an official document as an explicit acquisition step, then run
`cidrmerge` against the saved file:

```sh
curl --fail --location \
  --output openai-searchbot.json \
  https://openai.com/searchbot.json

cidrmerge --input-format searchbot \
  --raw --representation ranges \
  --output allow.txt \
  openai-searchbot.json
```

The ordinary merge command never downloads data, authenticates the saved
document, verifies a connecting bot, or assigns an admission role. Acquisition,
provenance checks, and choosing whether the resulting artifact is an allow or
deny list remain explicit responsibilities of the surrounding workflow.

Raw line-oriented output is the pipeline interchange intended for admission
list consumers such as `swift-cidr-admission`. The structured JSON emitted by
`cidrmerge --json` describes compiler output; it is not an admission-policy
document.
