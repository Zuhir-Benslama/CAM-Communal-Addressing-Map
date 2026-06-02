import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

Item {
    id: root

    signal comboChanged(string objectName, int index, string currentData)
    signal formSubmitted(string pageName)
    signal listRequested(string type)

    property alias subdTypeCombo: subdTypeCombo

    function getFieldText(name) {
        if (name === "subd_name") return subdNameField.text
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
                id: subdTypeCombo
                objectName: "subd_type"
                Layout.fillWidth: true
                editable: true
                textRole: "text"
                valueRole: "value"
                onCurrentIndexChanged: root.comboChanged("subd_type", currentIndex, currentValue)
                background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
            }

            Text { text: "Name:"; font.bold: true; color: Theme.activeText() }
            TextField {
                id: subdNameField
                objectName: "subd_name"
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
                font.bold: true
                Layout.minimumWidth: 200
                onClicked: root.formSubmitted("city")
                background: Rectangle { color: Theme.activeAccent(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            }

            Button {
                text: "Subdivisions List"
                Layout.minimumWidth: 150
                onClicked: root.listRequested("subds")
                background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.text; color: Theme.activeText(); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
