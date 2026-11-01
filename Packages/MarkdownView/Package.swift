// swift-tools-version: 6.0

import PackageDescription

/// Lakr233/MarkdownView 4.8.5, vendored: the chat transcript's Markdown view.
/// README.md says where it came from, what changed, and why. Upstream
/// declares iOS 16; this floor is 15, and the only 16.0 API in the two
/// shipped targets sits in a `canImport(AppKit)` branch that no iOS build
/// compiles, so the sources are upstream's as released.
let package = Package(
    name: "MarkdownView",
    defaultLocalization: "en",
    platforms: [
        .iOS(.v15),
    ],
    products: [
        .library(name: "MarkdownView", targets: ["MarkdownView"]),
        .library(name: "MarkdownParser", targets: ["MarkdownParser"]),
    ],
    dependencies: [
        .package(url: "https://github.com/Lakr233/Litext", from: "3.6.5"),
        .package(url: "https://github.com/mgriebling/SwiftMath", from: "1.7.3"),
        .package(url: "https://github.com/apple/swift-collections", from: "1.7.1"),
        .package(url: "https://github.com/swiftlang/swift-cmark", from: "0.9.0"),
        .package(url: "https://github.com/nicklockwood/LRUCache", from: "1.3.0"),
    ],
    targets: [
        .target(
            name: "MarkdownView",
            dependencies: [
                "Litext",
                .product(name: "LitextAnimation", package: "Litext"),
                "MarkdownParser",
                "SwiftMath",
                "LRUCache",
                .product(name: "DequeModule", package: "swift-collections"),
                .product(name: "OrderedCollections", package: "swift-collections"),
            ],
            resources: [.process("Resources")],
        ),
        .target(name: "MarkdownParser", dependencies: [
            .product(name: "cmark-gfm", package: "swift-cmark"),
            .product(name: "cmark-gfm-extensions", package: "swift-cmark"),
        ]),
    ],
)
