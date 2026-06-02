import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

Item {
    id: root

    signal comboChanged(string objectName, int index, string currentData)
    signal formSubmitted(string pageName)
    signal listRequested(string type)
    signal selectRef(string objectName, string layerName)

    property alias mountStatusCombo: mountStatusCombo
    property alias panelRefCombo: panelRefCombo

    function _safeComboValue(combo) {
        return combo.currentIndex >= 0 ? combo.currentValue : combo.displayText
    }

    function getFieldText(name) {
        if (name === "mount_status") return _safeComboValue(mountStatusCombo)
        if (name === "panel_ref") return _safeComboValue(panelRefCombo)
        if (name === "ref_name2") return refName2Label.text
        return ""
    }

    function setFieldText(name, text) {
        if (name === "ref_name2") refName2Label.text = text
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacingSm

        GridLayout {
            columns: 2
            columnSpacing: Theme.spacingSm
            rowSpacing: Theme.spacingSm
            Layout.fillWidth: true

            Text { text: "Mounting State:"; font.bold: true; color: Theme.activeText() }
            ComboBox {
                id: mountStatusCombo
                objectName: "mount_status"
                Layout.fillWidth: true
                editable: true
                textRole: "text"
                valueRole: "value"
                background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
            }

            Text { text: "Reference Type:"; font.bold: true; color: Theme.activeText() }
            ColumnLayout {
                Layout.fillWidth: true

                ComboBox {
                    id: panelRefCombo
                    objectName: "panel_ref"
                    Layout.fillWidth: true
                    editable: true
                    textRole: "text"
                    valueRole: "value"
                    background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                    contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
                }

                Button {
                    text: "Select Reference"
                    font.bold: true
                    Layout.fillWidth: true
                    onClicked: root.selectRef("panel_ref", _safeComboValue(panelRefCombo))
                    background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                    contentItem: Text { text: parent.text; color: Theme.activeText(); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                }

                Text {
                    id: refName2Label
                    objectName: "ref_name2"
                    font.bold: true
                    color: Theme.activeText()
                    wrapMode: Text.WordWrap
                }
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
                onClicked: root.formSubmitted("pan")
                background: Rectangle { color: Theme.activeAccent(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            }

            Button {
                text: "Panels List"
                Layout.minimumWidth: 150
                onClicked: root.listRequested("panels")
                background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                contentItem: Text { text: parent.text; color: Theme.activeText(); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
