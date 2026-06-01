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
        radius: Theme.borderRadius
    }

    contentItem: ColumnLayout {
        spacing: 4

        Label {
            text: root.title
            visible: root.title !== ""
            color: Theme.activeAccent()
            font.bold: true
            font.pixelSize: 12
            leftPadding: 2
            bottomMargin: 4
        }
    }

    padding: Theme.padding
    topPadding: title !== "" ? Theme.padding : Theme.padding
}
