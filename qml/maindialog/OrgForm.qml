import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

Item {
    id: root

    signal comboChanged(string objectName, int index, string currentData)
    signal formSubmitted(string pageName)
    signal listRequested(string type)

    property alias orgCatCombo: orgCatCombo
    property alias orgTypeCombo: orgTypeCombo

    function getFieldText(name) {
        if (name === "org_name") return orgNameField.text
        return ""
    }

    ColumnLayout {
        anchors.fill: parent

        GridLayout {
            columns: 2
            columnSpacing: Theme.spacingSm
            rowSpacing: Theme.spacingSm
            Layout.fillWidth: true

            Text { text: "Category:"; font.bold: true; color: Theme.activeText() }
            ComboBox {
                id: orgCatCombo
                objectName: "org_cat"
                Layout.fillWidth: true
                editable: true
                textRole: "text"
                valueRole: "value"
                onCurrentIndexChanged: root.comboChanged("org_cat", currentIndex, currentValue)
                background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
            }

            Text { text: "Type:"; font.bold: true; color: Theme.activeText() }
            ComboBox {
                id: orgTypeCombo
                objectName: "org_type"
                Layout.fillWidth: true
                editable: true
                textRole: "text"
                valueRole: "value"
                onCurrentIndexChanged: root.comboChanged("org_type", currentIndex, currentValue)
                background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
            }

            Text { text: "Name:"; font.bold: true; color: Theme.activeText() }
            TextField {
                id: orgNameField
                objectName: "org_name"
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
                onClicked: root.formSubmitted("org")
                background: Rectangle { color: Theme.activeAccent(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            }

            Button {
                text: "Facilities List"
                Layout.minimumWidth: 150
                onClicked: root.listRequested("orgs")
                background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.text; color: Theme.activeText(); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
