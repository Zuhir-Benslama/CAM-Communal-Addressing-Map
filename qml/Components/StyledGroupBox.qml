import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

Pane {
    id: root
    property string title: ""

    background: Rectangle {
        color: "transparent"
        border.color: Theme.activeBorder()
        border.width: 1
        radius: Theme.radiusLg
    }

    contentItem: ColumnLayout {
        spacing: Theme.spacingSm

        Label {
            text: root.title
            visible: root.title !== ""
            color: Theme.activeAccent()
            font.bold: true
            font.pixelSize: Theme.fontHeadline
            leftPadding: 2
            bottomMargin: 4
        }
    }

    padding: Theme.paddingMd
    topPadding: title !== "" ? Theme.paddingLg : 0
}
