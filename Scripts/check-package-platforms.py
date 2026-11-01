#!/usr/bin/env python3
"""Fail when a package declares a deployment floor other than the app's.

The app's floor is `IPHONEOS_DEPLOYMENT_TARGET` in
`Configuration/Base.xcconfig`, and it is what the package depends on
(`firmware (>= <floor>)`). A local Swift package declares its own minimum in
`platforms:`; whatever it says, Xcode builds its targets against the app's
setting, so a declaration that disagrees with the floor is a stale number, not
a different reality. Lowering the floor is one decision and every package
that reaches iOS changes with it, so `make check` compares them all.

Two forms are read: a literal (`.iOS(.v15)`, `.iOS("15.0")`) and one that
comes from an xcconfig the manifest parses at load time
(`Packages/ApelinToolchain`), which is followed to that file.

Usage: check-package-platforms.py <floor> <repository root>
"""

import os
import re
import sys

SKIP_DIRECTORY_NAMES = {".build", "build", "vendor-audit", ".git", "DerivedData"}
IOS_LITERAL = re.compile(r"\.iOS\(\.v(\d+)\)|\.iOS\(\"([0-9.]+)\"\)")
IOS_FROM_SETTINGS = re.compile(r"\.iOS\((?!\"|\.v)[A-Za-z_]")
XCCONFIG_VALUE = "IPHONEOS_DEPLOYMENT_TARGET"


def version(key):
    parts = [int(part) for part in key.split(".")[:3]]
    return tuple(parts + [0] * (3 - len(parts)))


def xcconfig_floor(path):
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            fields = line.split("=", 1)
            if len(fields) == 2 and fields[0].strip() == XCCONFIG_VALUE:
                return fields[1].strip()
    return None


def declared_floors(manifest):
    """Every iOS floor this manifest declares, as (value, how it was found)."""
    with open(manifest, encoding="utf-8") as handle:
        text = handle.read()
    found = []
    for groups in IOS_LITERAL.findall(text):
        constant, literal = groups
        found.append((f"{constant}.0" if constant else literal, f".iOS({constant or literal})"))
    if not found and IOS_FROM_SETTINGS.search(text):
        # The manifest reads its platforms from an xcconfig beside it.
        settings = os.path.join(os.path.dirname(manifest), "Configuration", "Platforms.xcconfig")
        value = xcconfig_floor(settings) if os.path.isfile(settings) else None
        if value is None:
            return None, f"{manifest} names no literal iOS floor and no Configuration/Platforms.xcconfig to read"
        found.append((value, f"Configuration/Platforms.xcconfig ({XCCONFIG_VALUE})"))
    return found, None


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__.strip().splitlines()[-1])
    floor, root = sys.argv[1], os.path.realpath(sys.argv[2])
    shown = lambda path: os.path.relpath(path, root).replace(os.sep, "/")
    failures = []
    checked = 0
    for directory, names, files in os.walk(root):
        names[:] = [name for name in names if name not in SKIP_DIRECTORY_NAMES]
        if "Package.swift" not in files:
            continue
        manifest = os.path.join(directory, "Package.swift")
        checked += 1
        floors, note = declared_floors(manifest)
        if note:
            failures.append(note)
            continue
        if not floors:
            # A manifest with no `platforms:` at all: SwiftPM's own defaults,
            # which are older than any floor this app could ship, so nothing
            # raises the app's minimum. It says nothing about this one either.
            print(f"check-package-platforms: {shown(manifest)} declares no iOS platform")
            continue
        for value, where in floors:
            if version(value) != version(floor):
                failures.append(f"{shown(manifest)}: {where} is {value}, the app's floor is {floor}")
    if checked == 0:
        sys.exit("error: check-package-platforms: no Package.swift under " + root)
    for failure in failures:
        print("error: " + failure, file=sys.stderr)
    if failures:
        sys.exit(65)
    print(f"check-package-platforms: {checked} packages, every iOS floor is {floor}")


if __name__ == "__main__":
    main()
