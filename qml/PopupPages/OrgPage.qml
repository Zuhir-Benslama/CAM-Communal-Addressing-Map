import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0
import Components 1.0

ColumnLayout {
    id: root
    property string pageKey: "org"
    signal saveRequested()
    signal catChanged(string value)

    spacing: Theme.spacing

    function setFormData(data) {
        if (data.category !== undefined) orgCatCombo.selectByValue(data.category)
        if (data.type !== undefined) orgTypeCombo.selectByValue(data.type)
        if (data.name !== undefined) orgNameField.text = data.name
    }

    function getFormData() {
        return {
            category: orgCatCombo.currentValue(),
            type: orgTypeCombo.currentValue(),
            name: orgNameField.text
        }
    }

    function setComboOptions(options) {
        if (options.orgCats !== undefined) orgCatCombo.model = options.orgCats
        if (options.orgTypes !== undefined) orgTypeCombo.model = options.orgTypes
    }

    StyledGroupBox {
        title: qsTr("Organization Information")
        Layout.fillWidth: true

        GridLayout {
            columns: 2
            columnSpacing: 8
            rowSpacing: 8
            Layout.fillWidth: true

            StyledLabel { text: qsTr("Category:") + " *"; font.bold: true }
            StyledComboBox {
                id: orgCatCombo
                Layout.fillWidth: true
                onActivated: root.catChanged(currentValue())
            }

            StyledLabel { text: qsTr("Type:") + " *"; font.bold: true }
            StyledComboBox { id: orgTypeCombo; Layout.fillWidth: true }

            StyledLabel { text: qsTr("Name:") + " *"; font.bold: true }
            StyledTextField { id: orgNameField; Layout.fillWidth: true }
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
