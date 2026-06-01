import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

Item {
    id: root
    objectName: "login"

    property alias usernameText: usernameField.text
    property alias passwordText: passwordField.text
    property alias mapOptionsModel: mapOptionsListModel
    property alias mapOptionsIndex: mapOptionsCombo.currentIndex

    ListModel { id: mapOptionsListModel }

    signal signInClicked
    signal addUserClicked
    signal restoreDbClicked
    signal comboChanged(string objectName, int index, string currentData)

    function getFieldText(name) {
        if (name === "username") return usernameField.text
        if (name === "password") return passwordField.text
        if (name === "map_options") return mapOptionsCombo.currentValue
        return ""
    }

    function setFieldText(name, text) {
        if (name === "username") usernameField.text = text
        if (name === "password") passwordField.text = text
    }

    Rectangle {
        anchors.fill: parent
        color: Theme.surface

        Flickable {
            anchors.fill: parent
            contentHeight: loginBox.height + 40
            clip: true

            Rectangle {
                id: loginBox
                width: Math.min(parent.width - 40, 500)
                height: childrenRect.height + 40
                anchors.centerIn: parent
                radius: 8
                color: Theme.background
                border.color: Theme.border

                ColumnLayout {
                    x: 20; y: 20
                    width: parent.width - 40
                    spacing: 16

                    Text {
                        text: "Login"
                        font.pixelSize: 22
                        font.bold: true
                        color: Theme.text
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Rectangle { height: 1; color: Theme.border; Layout.fillWidth: true }

                    GridLayout {
                        columns: 2
                        columnSpacing: 10
                        rowSpacing: 10
                        Layout.fillWidth: true

                        Text { text: "Username:"; font.bold: true; color: Theme.text; Layout.minimumWidth: 100 }
                        TextField {
                            id: usernameField
                            objectName: "username"
                            Layout.fillWidth: true
                            Layout.maximumWidth: 400
                            placeholderText: "Username"
                            color: Theme.text
                            background: Rectangle {
                                color: Theme.surface
                                border.color: Theme.border
                                radius: 4
                            }
                        }
                    }

                    GridLayout {
                        columns: 2
                        columnSpacing: 10
                        rowSpacing: 10
                        Layout.fillWidth: true

                        Text { text: "Password:"; font.bold: true; color: Theme.text; Layout.minimumWidth: 100 }
                        TextField {
                            id: passwordField
                            objectName: "password"
                            Layout.fillWidth: true
                            Layout.maximumWidth: 400
                            placeholderText: "Password"
                            echoMode: TextInput.Password
                            color: Theme.text
                            background: Rectangle {
                                color: Theme.surface
                                border.color: Theme.border
                                radius: 4
                            }
                        }
                    }

                    Rectangle { height: 1; color: Theme.border; Layout.fillWidth: true }

                    GridLayout {
                        columns: 2
                        columnSpacing: 10
                        rowSpacing: 10
                        Layout.fillWidth: true

                        Text { text: "Select Map:"; font.bold: true; color: Theme.text; Layout.minimumWidth: 100 }
                        ComboBox {
                            id: mapOptionsCombo
                            objectName: "map_options"
                            model: mapOptionsListModel
                            Layout.fillWidth: true
                            Layout.maximumWidth: 400
                            textRole: "text"
                            valueRole: "value"
                            onCurrentIndexChanged: {
                                root.comboChanged("map_options", currentIndex, currentValue)
                            }
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

                    Button {
                        text: "Sign In"
                        font.bold: true
                        Layout.alignment: Qt.AlignHCenter
                        Layout.minimumWidth: 200
                        onClicked: root.signInClicked()
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

                    Rectangle { height: 1; color: Theme.border; Layout.fillWidth: true }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Button {
                            text: "Add User"
                            Layout.minimumWidth: 150
                            onClicked: root.addUserClicked()
                            background: Rectangle {
                                color: Theme.surface
                                border.color: Theme.border
                                radius: 4
                            }
                            contentItem: Text {
                                text: parent.text
                                color: Theme.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }

                        Button {
                            text: "Restore Database"
                            Layout.minimumWidth: 150
                            onClicked: root.restoreDbClicked()
                            background: Rectangle {
                                color: Theme.surface
                                border.color: Theme.border
                                radius: 4
                            }
                            contentItem: Text {
                                text: parent.text
                                color: Theme.text
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
