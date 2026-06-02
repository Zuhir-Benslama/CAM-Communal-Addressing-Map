pragma Singleton
import QtQuick 2.15

QtObject {
    readonly property color bg: "#1a1b26"
    readonly property color surface: "#24253a"
    readonly property color overlay: "#2f3048"
    readonly property color border: "#3b3d54"
    readonly property color text: "#c9d1d9"
    readonly property color textSec: "#8b949e"
    readonly property color accent: "#58a6ff"
    readonly property color accentHover: "#79b8ff"
    readonly property color success: "#3fb950"
    readonly property color danger: "#f85149"
    readonly property color selection: "#264f78"

    readonly property color background: bg
    readonly property color primary: accent
    readonly property int borderRadius: 8
    readonly property int spacing: 12
    readonly property int padding: 12

    // Apple HIG design tokens — 8pt spacing grid
    readonly property int spacingXs: 4
    readonly property int spacingSm: 8
    readonly property int spacingMd: 12
    readonly property int spacingLg: 16
    readonly property int spacingXl: 24

    readonly property int paddingSm: 8
    readonly property int paddingMd: 12
    readonly property int paddingLg: 16

    readonly property int radiusSm: 4
    readonly property int radiusMd: 6
    readonly property int radiusLg: 8

    readonly property int fontCaption: 10
    readonly property int fontCaption2: 11
    readonly property int fontBody: 12
    readonly property int fontSubhead: 13
    readonly property int fontHeadline: 14
    readonly property int fontTitle: 20

    readonly property color lightBg: "#f6f8fa"
    readonly property color lightSurface: "#ffffff"
    readonly property color lightOverlay: "#eaeef2"
    readonly property color lightBorder: "#d0d7de"
    readonly property color lightText: "#1f2328"
    readonly property color lightTextSec: "#656d76"
    readonly property color lightAccent: "#0969da"
    readonly property color lightAccentHover: "#0550ae"
    readonly property color lightSuccess: "#1a7f37"
    readonly property color lightDanger: "#cf222e"
    readonly property color lightSelection: "#b6d4fe"

    property bool isDark: true

    function activeBg() { return isDark ? bg : lightBg }
    function activeSurface() { return isDark ? surface : lightSurface }
    function activeOverlay() { return isDark ? overlay : lightOverlay }
    function activeBorder() { return isDark ? border : lightBorder }
    function activeText() { return isDark ? text : lightText }
    function activeTextSec() { return isDark ? textSec : lightTextSec }
    function activeAccent() { return isDark ? accent : lightAccent }
    function activeAccentHover() { return isDark ? accentHover : lightAccentHover }
    function activeSuccess() { return isDark ? success : lightSuccess }
    function activeDanger() { return isDark ? danger : lightDanger }
    function activeSelection() { return isDark ? selection : lightSelection }
}
