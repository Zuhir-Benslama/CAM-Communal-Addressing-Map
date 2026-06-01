import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0
import Components 1.0

ColumnLayout {
    id: root
    property string pageKey: "roads"
    signal saveRequested()

    spacing: Theme.spacing

    function setFormData(data) {
        if (data.type !== undefined) roadTypeCombo.selectByValue(data.type)
        if (data.name !== undefined) roadNameField.text = data.name
    }

    function getFormData() {
        return {
            type: roadTypeCombo.currentValue(),
            name: roadNameField.text
        }
    }

    function setComboOptions(options) {
        if (options.roadTypes !== undefined) roadTypeCombo.model = options.roadTypes
    }

    StyledGroupBox {
        title: qsTr("Road Information")
        Layout.fillWidth: true

        GridLayout {
            columns: 2
            columnSpacing: 8
            rowSpacing: 8
            Layout.fillWidth: true

            StyledLabel { text: qsTr("Type:") + " *"; font.bold: true }
            StyledComboBox { id: roadTypeCombo; Layout.fillWidth: true }

            StyledLabel { text: qsTr("Name:") + " *"; font.bold: true }
            StyledTextField { id: roadNameField; Layout.fillWidth: true }
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
