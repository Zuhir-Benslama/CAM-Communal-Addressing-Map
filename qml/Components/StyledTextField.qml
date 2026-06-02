import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

TextField {
    id: control

    property bool isValid: text.length > 0

    color: Theme.activeText()
    placeholderTextColor: Theme.activeTextSec()
    selectionColor: Theme.activeSelection()
    selectedTextColor: Theme.activeText()

    background: Rectangle {
        implicitHeight: 34
        color: Theme.activeSurface()
        border.color: control.activeFocus ? Theme.activeAccent() : Theme.activeBorder()
        border.width: control.activeFocus ? 2 : 1
        radius: Theme.radiusMd
    }

    leftPadding: 8
    rightPadding: 8
    topPadding: 6
    bottomPadding: 6
}
