import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0
import Components 1.0

ColumnLayout {
    id: root
    property string pageKey: "city"
    signal saveRequested()

    spacing: Theme.spacing

    function setFormData(data) {
        if (data.type !== undefined) subdTypeCombo.selectByValue(data.type)
        if (data.name !== undefined) subdNameField.text = data.name
    }

    function getFormData() {
        return {
            type: subdTypeCombo.currentValue(),
            name: subdNameField.text
        }
    }

    function setComboOptions(options) {
        if (options.subdTypes !== undefined) subdTypeCombo.model = options.subdTypes
    }

    StyledGroupBox {
        title: qsTr("Subdivision Information")
        Layout.fillWidth: true

        GridLayout {
            columns: 2
            columnSpacing: 8
            rowSpacing: 8
            Layout.fillWidth: true

            StyledLabel { text: qsTr("Type:") + " *"; font.bold: true }
            StyledComboBox { id: subdTypeCombo; Layout.fillWidth: true }

            StyledLabel { text: qsTr("Name:") + " *"; font.bold: true }
            StyledTextField { id: subdNameField; Layout.fillWidth: true }
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
