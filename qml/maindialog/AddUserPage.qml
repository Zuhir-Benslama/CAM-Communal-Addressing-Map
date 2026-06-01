import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

Item {
    id: root
    objectName: "add_usr"

    property alias wilayaModel: wilayaCombo.model
    property alias communeModel: communeCombo.model

    signal saveClicked
    signal cancelClicked
    signal wilayaChanged(int index, string currentData)

    property var _fields: ({})

    function registerField(field) {
        _fields[field.objectName] = field
    }

    function getFieldText(name) {
        return _fields[name] ? _fields[name].text : ""
    }

    function setFieldText(name, text) {
        if (_fields[name]) _fields[name].text = text
    }

    Rectangle {
        anchors.fill: parent
        color: Theme.surface

        Flickable {
            anchors.fill: parent
            contentHeight: formBox.height + 40
            clip: true

            Rectangle {
                id: formBox
                width: Math.min(parent.width - 40, 550)
                height: childrenRect.height + 40
                anchors.centerIn: parent
                radius: 8
                color: Theme.background
                border.color: Theme.border

                ColumnLayout {
                    x: 20; y: 20
                    width: parent.width - 40
                    spacing: 12

                    Text {
                        text: "Add User"
                        font.pixelSize: 20
                        font.bold: true
                        color: Theme.text
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Rectangle { height: 1; color: Theme.border; Layout.fillWidth: true }

                    Repeater {
                        model: [
                            { label: "fname", text: "First Name *:" },
                            { label: "lname", text: "Last Name *:" },
                            { label: "email", text: "Email *:" },
                            { label: "pnum", text: "Phone *:" },
                            { label: "uname", text: "Username *:" },
                            { label: "pwd", text: "Password *:" },
                        ]

                        GridLayout {
                            columns: 2
                            columnSpacing: 10
                            rowSpacing: 8
                            Layout.fillWidth: true

                            Text {
                                text: modelData.text
                                font.bold: true
                                color: Theme.text
                                Layout.minimumWidth: 120
                                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                            }

                            TextField {
                                objectName: modelData.label
                                Layout.fillWidth: true
                                Layout.maximumWidth: 400
                                echoMode: modelData.label === "pwd" ? TextInput.Password : TextInput.Normal
                                color: Theme.text
                                placeholderText: modelData.text
                                background: Rectangle {
                                    color: Theme.surface
                                    border.color: Theme.border
                                    radius: 4
                                }
                                Component.onCompleted: root.registerField(this)
                            }
                        }
                    }

                    Rectangle { height: 1; color: Theme.border; Layout.fillWidth: true }

                    GridLayout {
                        columns: 2
                        columnSpacing: 10
                        rowSpacing: 8
                        Layout.fillWidth: true

                        Text { text: "State *:"; font.bold: true; color: Theme.text; Layout.minimumWidth: 120; Layout.alignment: Qt.AlignRight | Qt.AlignVCenter }
                        ComboBox {
                            id: wilayaCombo
                            objectName: "wilaya_list"
                            Layout.fillWidth: true
                            Layout.maximumWidth: 400
                            editable: true
                            textRole: "text"
                            valueRole: "value"
                            onCurrentIndexChanged: root.wilayaChanged(currentIndex, currentValue)
                            background: Rectangle {
                                color: Theme.surface
                                border.color: Theme.border
                                radius: 4
                            }
                            contentItem: Text {
                                text: parent.displayText
                                color: Theme.text
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }

                    GridLayout {
                        columns: 2
                        columnSpacing: 10
                        rowSpacing: 8
                        Layout.fillWidth: true

                        Text { text: "Municipality *:"; font.bold: true; color: Theme.text; Layout.minimumWidth: 120; Layout.alignment: Qt.AlignRight | Qt.AlignVCenter }
                        ComboBox {
                            id: communeCombo
                            objectName: "commune_of_wilaya"
                            Layout.fillWidth: true
                            Layout.maximumWidth: 400
                            editable: true
                            textRole: "text"
                            valueRole: "value"
                            background: Rectangle {
                                color: Theme.surface
                                border.color: Theme.border
                                radius: 4
                            }
                            contentItem: Text {
                                text: parent.displayText
                                color: Theme.text
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }

                    Rectangle { height: 1; color: Theme.border; Layout.fillWidth: true }

                    RowLayout {
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 20

                        Button {
                            text: "Cancel"
                            onClicked: root.cancelClicked()
                            background: Rectangle {
                                color: Theme.danger
                                radius: 4
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "white"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }

                        Button {
                            text: "Save"
                            font.bold: true
                            Layout.minimumWidth: 200
                            onClicked: root.saveClicked()
                            background: Rectangle {
                                color: Theme.primary
                                radius: 4
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "white"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }
            }
        }
    }
}
