# Releasing cidrmerge

This maintainer guide stages a signed `MAJOR.MINOR.PATCH` release, reviews its
four platform archives, and publishes it through GitHub, the RouteObjects
Homebrew tap, and Swift Package Index. Release workflows create drafts; a
maintainer publishes them only after explicit approval.

## Prepare and validate main

Start from a clean `main` that matches its remote. The version must not have a
leading `v`:

```sh
version=0.1.0
git switch main
git pull --ff-only origin main
git status --short --branch
./scripts/check-release.sh "${version}"
./scripts/audit-release-content.sh tree
```

Confirm every release commit has a valid signature and inspect all content that
will become public. Do not continue if the tree, history, workflow logs, or
artifacts expose credentials, private paths, or internal-only material.

## Run the private dry run

While the repository is private, let the push to `main` complete the automatic
Linux x86-64 and ARM64 CI jobs. Then manually dispatch `.github/workflows/ci.yml`
and require its macOS job, including the iOS Core simulator build, to pass.

Manually dispatch `.github/workflows/release.yml` with the intended version. A
manual run builds and inspects all four archives and creates the
`cidrmerge-<version>-release` workflow artifact; it cannot create or update a
GitHub Release.

```sh
gh workflow run ci.yml --repo RouteObjects/cidrmerge
gh workflow run release.yml --repo RouteObjects/cidrmerge -f version="${version}"
gh run list --repo RouteObjects/cidrmerge --workflow ci.yml --limit 3
gh run list --repo RouteObjects/cidrmerge --workflow release.yml --limit 3
gh run watch --repo RouteObjects/cidrmerge RUN_ID
gh run download RUN_ID \
  --repo RouteObjects/cidrmerge \
  --name "cidrmerge-${version}-release" \
  --dir "dist/${version}"
```

The artifact must contain exactly these release files:

- `cidrmerge-<version>-darwin-aarch64.tar.gz`
- `cidrmerge-<version>-darwin-x86_64.tar.gz`
- `cidrmerge-<version>-linux-aarch64.tar.gz`
- `cidrmerge-<version>-linux-x86_64.tar.gz`
- `SHA256SUMS`

Verify all checksums from inside the download directory with `sha256sum
--check SHA256SUMS` on Linux or `shasum -a 256 --check SHA256SUMS` on macOS.
Each archive must contain only `cidrmerge`, `LICENSE`, and
`THIRD_PARTY_NOTICES.txt`. Exercise a compatible archive's `--version`,
`--help`, an offline stdin merge, and `--checksum --output` before tagging.
Verify the generated detached checksum file with `sha256sum --check` or
`shasum -a 256 --check`, run from the output file's parent directory because
the checksum file intentionally records only its basename. Record each
stripped executable's byte size for the four release platforms as comparison
evidence, but do not impose a brittle cross-platform size threshold.

## Sign the tag and review the draft

Obtain explicit approval before changing repository visibility. After public
visibility and all required CI checks pass, confirm local and remote `main`
still identify the same commit, then create the annotated SSH-signed tag:

```sh
git fetch origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
git tag -s "${version}" -m "cidrmerge ${version}"
git tag -v "${version}"
git push origin "${version}"
```

The tag-triggered workflow verifies the tag, rebuilds the release assets, and
creates or updates a **draft** GitHub Release. It refuses to replace assets on
an already-published release. Download the draft assets, repeat the checksum
and archive tests, and review the generated notes. Mark the Release latest and
non-prerelease, but keep it as a draft until Craig gives explicit publication
approval.

After approval, publish the inspected draft. If immutable releases are enabled,
publication locks the tag and assets. In every configuration, treat a published
tag and its assets as immutable and issue a new patch version for corrections.

## Homebrew and Swift Package Index

Only after the GitHub Release is public:

1. Copy the four published hashes from `SHA256SUMS` into
   `Formula/cidrmerge.rb` in `RouteObjects/homebrew-tap`; use the corresponding
   versioned Release URLs and do not add a redundant `version` declaration.
2. Run Homebrew style, strict audit, livecheck, all-platform formula parsing,
   checksum downloads, installation, and the formula test. Push the signed tap
   commit only after `brew install RouteObjects/tap/cidrmerge` and `brew test`
   succeed without a Swift toolchain.
3. Submit `https://github.com/RouteObjects/cidrmerge.git` to Swift Package Index
   and record its platform and hosted `CIDRMergeCore` documentation results as
   pending or passed. Index backlog never blocks release distribution or
   downstream development; add public badges or links only after their URLs
   resolve.

Never move the released tag when publishing post-release documentation.

## Failure and rollback policy

- Before pushing the tag, fix the release candidate and rerun the complete dry
  run.
- After pushing the tag, never delete, move, or overwrite it: a public semantic
  tag is already available to SwiftPM consumers even while its GitHub Release
  remains a draft. Rerun transient workflow failures against the same tag, but
  correct release-content defects in the next patch version.
- After publication, do not replace release assets. Correct defects in the next
  patch release and document any security impact through the repository's
  security policy.
