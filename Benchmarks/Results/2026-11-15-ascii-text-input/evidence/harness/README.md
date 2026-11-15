# Portable evidence helpers

Python scripts in this directory are byte-identical to the retained originals; their hashes are listed in manifest.json. differential.py is standalone and accepts --baseline, --candidate and --output arguments. Linux helpers belong in a fresh platform root's control/ directory with sources/, fixtures/, bin/ and build/ siblings. The macOS pair uses a configured control/context.json and its original reference run. Do not run a timing helper from this report directory.

All private host paths in example JSON are symbolic placeholders. Resolve those for a new host and regenerate its freezes; transformed public JSON does not retain the original files' byte hashes. Original source artifacts and their hashes remain separately listed in the top-level manifest.json. These helpers do not include binaries, fixtures, raw stdout, test logs, caches, toolchains or profiler recordings.
