# MarkdownView

The chat transcript's Markdown view, vendored from source so the app can
run on iOS 15. Upstream `Lakr233/MarkdownView` declares `.iOS(.v16)` for its
whole package; this floor is 15, and the audit below is why that is honest.

| Directory | What it is | Origin | License |
| --- | --- | --- | --- |
| `Sources/MarkdownView` | The UIKit Markdown view, its tables, code blocks and streaming text | [Lakr233/MarkdownView](https://github.com/Lakr233/MarkdownView) 4.8.5 (`3941f185`), as released | MIT (`LICENSE`) |
| `Sources/MarkdownParser` | The cmark-gfm parse tree Apelin's transcript renders | the same commit, as released | MIT (`LICENSE`) |

The package keeps upstream's dependencies at upstream's versions: Litext
(for its text labels), SwiftMath, swift-collections, swift-cmark and
LRUCache. What it drops is everything that is not shipped: the
`WatchMarkdownView` target and product, the `MarkdownViewBenchmark` and
`MarkdownViewCatalog` executables, and the test targets — Apelin renders
Markdown in UIKit, not on watchOS, and `make check` keeps the harness on
packages it can build without UIKit.

## What changed from upstream

Nothing in the sources. The 16.0 floor was audited against iOS 15 API by
API, and the only 16.0-only call in the two shipped targets —
`scrollView.automaticallyAdjustsContentInsets` in
`Components/CodeView/CodeViewConfiguration.swift` — sits in a
`#elseif canImport(AppKit)` branch, which no iOS build compiles. The rest
of what reads as 16 is 15: `UISheetPresentationController`'s `detents` and
`prefersGrabberVisible` came with iOS 15 itself, and the one 16.0-only
delegate method (`TableView+Selection.swift`, "Copy as Markdown" in the
edit menu) already carries upstream's `@available(iOS 16.0, …)`; on 15 the
table's menu keeps the system's suggested actions. `TableRowLimit.swift`
guards its iOS 17 detail the same way upstream wrote it.

Only `Package.swift` is rewritten: two library products, `.iOS(.v15)`, no
watchOS target, no executables, no test targets.

## Updating

Fold upstream's changes into `Sources/` by hand (the file list above is
what ships), re-audit any new API against the floor the same way, and
re-render the license copy: `Licenses/MarkdownView/` holds the notice and
the same `LICENSE` text, and `Licenses/review.json` hashes it — a changed
license text fails the build until it is reviewed again.
