import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0
import Components 1.0

ColumnLayout {
    id: root
    property string pageKey: "pan"
    signal saveRequested()
    signal selectReferenceRequested(string layerName)

    spacing: Theme.spacing

    function setFormData(data) {
        if (data.mountStatus !== undefined) mountStatusCombo.selectByValue(data.mountStatus)
        if (data.refType !== undefined) refTypeCombo.selectByValue(data.refType)
        if (data.refName !== undefined) refNameLabel.text = data.refName
    }

    function getFormData() {
        return {
            mountStatus: mountStatusCombo.currentValue(),
            refType: refTypeCombo.currentValue(),
            refName: refNameLabel.text
        }
    }

    function setComboOptions(options) {
        if (options.mountStatuses !== undefined) mountStatusCombo.model = options.mountStatuses
        if (options.refTypes !== undefined) refTypeCombo.model = options.refTypes
    }

    function setReferenceName(name) {
        refNameLabel.text = name
    }

    StyledGroupBox {
        title: qsTr("Panel Information")
        Layout.fillWidth: true

        ColumnLayout {
            spacing: Theme.spacing
            Layout.fillWidth: true

            GridLayout {
                columns: 2
                columnSpacing: 8
                rowSpacing: 8
                Layout.fillWidth: true

                StyledLabel { text: qsTr("Mounting State:") + " *"; font.bold: true }
                StyledComboBox { id: mountStatusCombo; Layout.fillWidth: true }
            }

            StyledGroupBox {
                title: qsTr("Reference")
                Layout.fillWidth: true

                ColumnLayout {
                    spacing: Theme.spacing
                    Layout.fillWidth: true

                    GridLayout {
                        columns: 2
                        columnSpacing: 8
                        rowSpacing: 8
                        Layout.fillWidth: true

                        StyledLabel { text: qsTr("Reference Type:") + " *"; font.bold: true }
                        StyledComboBox { id: refTypeCombo; Layout.fillWidth: true }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        StyledButton {
                            text: qsTr("Select Reference")
                            onClicked: root.selectReferenceRequested(refTypeCombo.currentValue())
                        }
                        StyledLabel {
                            id: refNameLabel
                            text: ""
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }
    }

    Item { Layout.fillHeight: true }

    RowLayout {
        Layout.fillWidth: true
        Item { Layout.fillWidth: true }
        StyledButton {
            isPrimary: true
            text: qsTr("Save")
            onClicked: root.saveRequested()
        }
        Item { Layout.fillWidth: true }
    }
}
