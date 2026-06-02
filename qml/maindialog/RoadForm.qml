import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

Item {
    id: root

    signal comboChanged(string objectName, int index, string currentData)
    signal formSubmitted(string pageName)
    signal listRequested(string type)

    property alias roadTypeCombo: roadTypeCombo

    function getFieldText(name) {
        if (name === "road_name") return roadNameField.text
        return ""
    }

    ColumnLayout {
        anchors.fill: parent

        GridLayout {
            columns: 2
            columnSpacing: Theme.spacingSm
            rowSpacing: Theme.spacingSm
            Layout.fillWidth: true

            Text { text: "Type:"; font.bold: true; color: Theme.activeText() }
            ComboBox {
                id: roadTypeCombo
                objectName: "type_road"
                Layout.fillWidth: true
                editable: true
                textRole: "text"
                valueRole: "value"
                onCurrentIndexChanged: root.comboChanged("type_road", currentIndex, currentValue)
                background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
            }

            Text { text: "Name:"; font.bold: true; color: Theme.activeText() }
            TextField {
                id: roadNameField
                objectName: "road_name"
                Layout.fillWidth: true
                color: Theme.activeText()
                background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
            }
        }

        Item { Layout.fillHeight: true }

        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: Theme.spacingLg

            Button {
                text: "Save"
                Layout.minimumWidth: 180
                onClicked: root.formSubmitted("road")
                background: Rectangle { color: Theme.activeAccent(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            }

            Button {
                text: "Roads List"
                Layout.minimumWidth: 140
                onClicked: root.listRequested("roads")
                background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.text; color: Theme.activeText(); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
