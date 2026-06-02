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

    property alias roadRefCombo: roadRefCombo
    property alias numStateCombo: numStateCombo
    property alias activityCatCombo: activityCatCombo
    property alias activityTypeCombo: activityTypeCombo

    function _safeComboValue(combo) {
        return combo.currentIndex >= 0 ? combo.currentValue : combo.displayText
    }

    function getFieldText(name) {
        if (name === "road_ref") return _safeComboValue(roadRefCombo)
        if (name === "num_val") return numValField.text
        if (name === "repetition") return repField.text
        if (name === "ref_name") return refNameLabel.text
        return ""
    }

    function setFieldText(name, text) {
        if (name === "ref_name") refNameLabel.text = text
    }

    Flickable {
        anchors.fill: parent
        contentHeight: numColumn.height
        clip: true

        ColumnLayout {
            id: numColumn
            width: parent.width
            spacing: Theme.spacingSm

            GridLayout {
                columns: 2
                columnSpacing: Theme.spacingSm
                rowSpacing: Theme.spacingSm
                Layout.fillWidth: true

                Text { text: "Reference Type:"; font.bold: true; color: Theme.activeText() }
                ColumnLayout {
                    Layout.fillWidth: true

                    ComboBox {
                        id: roadRefCombo
                        objectName: "road_ref"
                        Layout.fillWidth: true
                        editable: true
                        textRole: "text"
                        valueRole: "value"
                        onCurrentIndexChanged: root.comboChanged("road_ref", currentIndex, currentValue)
                        background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                        contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
                    }

                    Button {
                        text: "Select Reference"
                        font.bold: true
                        Layout.fillWidth: true
                        onClicked: root.selectRef("road_ref", _safeComboValue(roadRefCombo))
                        background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                        contentItem: Text { text: parent.text; color: Theme.activeText(); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    }

                    Text {
                        id: refNameLabel
                        objectName: "ref_name"
                        font.bold: true
                        color: Theme.activeText()
                        wrapMode: Text.WordWrap
                    }
                }
            }

            GridLayout {
                columns: 2
                columnSpacing: Theme.spacingSm
                rowSpacing: Theme.spacingSm
                Layout.fillWidth: true

                Text { text: "Number:"; font.bold: true; color: Theme.activeText() }
                TextField {
                    id: numValField
                    objectName: "num_val"
                    Layout.fillWidth: true
                    color: Theme.activeText()
                    background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                }

                Text { text: "Duplicated:"; font.bold: true; color: Theme.activeText() }
                TextField {
                    id: repField
                    objectName: "repetition"
                    Layout.fillWidth: true
                    color: Theme.activeText()
                    background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                }

                Text { text: "State:"; font.bold: true; color: Theme.activeText() }
                ComboBox {
                    id: numStateCombo
                    objectName: "num_state"
                    Layout.fillWidth: true
                    editable: true
                    textRole: "text"
                    valueRole: "value"
                    background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                    contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
                }
            }

            Rectangle {
                color: Theme.activeBorder()
                height: 1
                Layout.fillWidth: true
            }

            Text { text: "Activity"; font.bold: true; color: Theme.activeText() }

            GridLayout {
                columns: 2
                columnSpacing: Theme.spacingSm
                rowSpacing: Theme.spacingSm
                Layout.fillWidth: true

                Text { text: "Category:"; font.bold: true; color: Theme.activeText() }
                ComboBox {
                    id: activityCatCombo
                    objectName: "activity_cat"
                    Layout.fillWidth: true
                    editable: true
                    textRole: "text"
                    valueRole: "value"
                    onCurrentIndexChanged: root.comboChanged("activity_cat", currentIndex, currentValue)
                    background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                    contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
                }

                Text { text: "Type:"; font.bold: true; color: Theme.activeText() }
                ComboBox {
                    id: activityTypeCombo
                    objectName: "activity_type"
                    Layout.fillWidth: true
                    editable: true
                    textRole: "text"
                    valueRole: "value"
                    background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                    contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
                }
            }

            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: Theme.spacingLg

                Button {
                    text: "Save"
                    font.bold: true
                    Layout.minimumWidth: 200
                    onClicked: root.formSubmitted("num")
                    background: Rectangle { color: Theme.activeAccent(); radius: Theme.radiusMd }
                    contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                }

                Button {
                    text: "Entrances List"
                    Layout.minimumWidth: 150
                    onClicked: root.listRequested("nums")
                    background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                    contentItem: Text { text: parent.text; color: Theme.activeText(); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                }
            }
        }
    }
}
