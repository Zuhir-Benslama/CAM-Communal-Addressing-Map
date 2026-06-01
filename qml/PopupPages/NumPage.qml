import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0
import Components 1.0

ColumnLayout {
    id: root
    property string pageKey: "num"
    signal saveRequested()
    signal selectReferenceRequested(string layerName)
    signal catChanged(string value)

    spacing: Theme.spacing

    function setFormData(data) {
        if (data.refType !== undefined) refTypeCombo.selectByValue(data.refType)
        if (data.refName !== undefined) refNameLabel.text = data.refName
        if (data.number !== undefined) numValField.text = data.number
        if (data.repetition !== undefined) repetitionField.text = data.repetition
        if (data.state !== undefined) stateCombo.selectByValue(data.state)
        if (data.activityCat !== undefined) activityCatCombo.selectByValue(data.activityCat)
        if (data.activityType !== undefined) activityTypeCombo.selectByValue(data.activityType)
    }

    function getFormData() {
        return {
            refType: refTypeCombo.currentValue(),
            refName: refNameLabel.text,
            number: numValField.text,
            repetition: repetitionField.text,
            state: stateCombo.currentValue(),
            activityCat: activityCatCombo.currentValue(),
            activityType: activityTypeCombo.currentValue()
        }
    }

    function setComboOptions(options) {
        if (options.refTypes !== undefined) refTypeCombo.model = options.refTypes
        if (options.states !== undefined) stateCombo.model = options.states
        if (options.activityCats !== undefined) activityCatCombo.model = options.activityCats
        if (options.activityTypes !== undefined) activityTypeCombo.model = options.activityTypes
    }

    function setReferenceName(name) {
        refNameLabel.text = name
    }

    Flickable {
        Layout.fillWidth: true
        Layout.fillHeight: true
        contentHeight: contentCol.implicitHeight
        clip: true
        ScrollIndicator.vertical: ScrollIndicator { }

        ColumnLayout {
            id: contentCol
            width: parent.width
            spacing: Theme.spacing

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

            StyledGroupBox {
                title: qsTr("Number")
                Layout.fillWidth: true

                GridLayout {
                    columns: 2
                    columnSpacing: 8
                    rowSpacing: 8
                    Layout.fillWidth: true

                    StyledLabel { text: qsTr("Number:"); font.bold: true }
                    StyledTextField { id: numValField; Layout.fillWidth: true }

                    StyledLabel { text: qsTr("Duplicated:"); font.bold: true }
                    StyledTextField { id: repetitionField; Layout.fillWidth: true }

                    StyledLabel { text: qsTr("State:"); font.bold: true }
                    StyledComboBox { id: stateCombo; Layout.fillWidth: true }
                }
            }

            StyledGroupBox {
                title: qsTr("Performed Activity")
                Layout.fillWidth: true

                GridLayout {
                    columns: 2
                    columnSpacing: 8
                    rowSpacing: 8
                    Layout.fillWidth: true

                    StyledLabel { text: qsTr("Category:"); font.bold: true }
                    StyledComboBox {
                        id: activityCatCombo
                        Layout.fillWidth: true
                        onActivated: root.catChanged(currentValue())
                    }

                    StyledLabel { text: qsTr("Type:"); font.bold: true }
                    StyledComboBox { id: activityTypeCombo; Layout.fillWidth: true }
                }
            }
        }
    }

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
