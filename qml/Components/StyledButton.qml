import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

Button {
    id: control

    property bool isPrimary: false

    implicitHeight: 34
    implicitWidth: isPrimary ? 180 : 120

    contentItem: Text {
        text: control.text
        font.bold: control.isPrimary
        color: control.enabled
               ? (control.isPrimary ? "#ffffff" : Theme.activeText())
               : Theme.activeTextSec()
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        color: {
            if (!control.enabled) return Theme.activeOverlay()
            if (control.isPrimary) {
                return control.pressed ? Theme.activeAccentHover() : Theme.activeAccent()
            }
            return control.pressed ? Theme.activeSelection() : Theme.activeSurface()
        }
        border.color: control.isPrimary ? "transparent" : Theme.activeBorder()
        border.width: 1
        radius: Theme.borderRadius
    }
}
