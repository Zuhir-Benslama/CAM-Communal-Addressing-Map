import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

Item {
    id: root

    signal comboChanged(string objectName, int index, string currentData)
    signal formSubmitted(string pageName)

    property alias zoneTypeCombo: zoneTypeCombo

    function getFieldText(name) {
        if (name === "nom_zone") return zoneNameField.text
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
                id: zoneTypeCombo
                objectName: "zone_type"
                Layout.fillWidth: true
                editable: true
                textRole: "text"
                valueRole: "value"
                onCurrentIndexChanged: root.comboChanged("zone_type", currentIndex, currentValue)
                background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
            }

            Text { text: "Name:"; font.bold: true; color: Theme.activeText() }
            TextField {
                id: zoneNameField
                objectName: "nom_zone"
                Layout.fillWidth: true
                color: Theme.activeText()
                background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
            }
        }

        Item { Layout.fillHeight: true }

        Button {
            text: "Save"
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
            Layout.minimumWidth: 200
            onClicked: root.formSubmitted("zone")
            background: Rectangle { color: Theme.activeAccent(); radius: Theme.radiusMd }
            contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
        }

        Item { Layout.fillHeight: true }
    }
}
