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
        color: Theme.activeSurface()

        Flickable {
            anchors.fill: parent
            contentHeight: loginBox.height + 40
            clip: true

            Rectangle {
                id: loginBox
                width: Math.min(parent.width - 40, 500)
                height: childrenRect.height + (Theme.paddingLg * 2)
                anchors.centerIn: parent
                radius: Theme.radiusLg
                color: Theme.activeBg()
                border.color: Theme.activeBorder()

                ColumnLayout {
                    x: Theme.paddingLg
                    y: Theme.paddingLg
                    width: parent.width - (Theme.paddingLg * 2)
                    spacing: Theme.spacingMd

                    Text {
                        text: "Login"
                        font.pixelSize: Theme.fontTitle
                        font.bold: true
                        color: Theme.activeAccent()
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Rectangle { height: 1; color: Theme.activeBorder(); Layout.fillWidth: true }

                    GridLayout {
                        columns: 2
                        columnSpacing: Theme.spacingSm
                        rowSpacing: Theme.spacingSm
                        Layout.fillWidth: true

                        Text { text: "Username:"; font.bold: true; color: Theme.activeText(); Layout.minimumWidth: 100 }
                        TextField {
                            id: usernameField
                            objectName: "username"
                            Layout.fillWidth: true
                            Layout.maximumWidth: 400
                            placeholderText: "Username"
                            color: Theme.activeText()
                            background: Rectangle {
                                color: Theme.activeSurface()
                                border.color: Theme.activeBorder()
                                radius: Theme.radiusMd
                            }
                        }
                    }

                    GridLayout {
                        columns: 2
                        columnSpacing: Theme.spacingSm
                        rowSpacing: Theme.spacingSm
                        Layout.fillWidth: true

                        Text { text: "Password:"; font.bold: true; color: Theme.activeText(); Layout.minimumWidth: 100 }
                        TextField {
                            id: passwordField
                            objectName: "password"
                            Layout.fillWidth: true
                            Layout.maximumWidth: 400
                            placeholderText: "Password"
                            echoMode: TextInput.Password
                            color: Theme.activeText()
                            background: Rectangle {
                                color: Theme.activeSurface()
                                border.color: Theme.activeBorder()
                                radius: Theme.radiusMd
                            }
                        }
                    }

                    Rectangle { height: 1; color: Theme.activeBorder(); Layout.fillWidth: true }

                    GridLayout {
                        columns: 2
                        columnSpacing: Theme.spacingSm
                        rowSpacing: Theme.spacingSm
                        Layout.fillWidth: true

                        Text { text: "Select Map:"; font.bold: true; color: Theme.activeText(); Layout.minimumWidth: 100 }
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
                                color: Theme.activeSurface()
                                border.color: Theme.activeBorder()
                                radius: Theme.radiusMd
                            }
                            contentItem: Text {
                                text: parent.displayText
                                color: Theme.activeText()
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }

                    Rectangle { height: 1; color: Theme.activeBorder(); Layout.fillWidth: true }

                    Button {
                        text: "Sign In"
                        font.bold: true
                        Layout.alignment: Qt.AlignHCenter
                        Layout.minimumWidth: 200
                        onClicked: root.signInClicked()
                        background: Rectangle {
                            color: Theme.activeAccent()
                            radius: Theme.radiusMd
                        }
                        contentItem: Text {
                            text: parent.text
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Rectangle { height: 1; color: Theme.activeBorder(); Layout.fillWidth: true }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingSm

                        Button {
                            text: "Add User"
                            Layout.minimumWidth: 150
                            onClicked: root.addUserClicked()
                            background: Rectangle {
                                color: Theme.activeSurface()
                                border.color: Theme.activeBorder()
                                radius: Theme.radiusMd
                            }
                            contentItem: Text {
                                text: parent.text
                                color: Theme.activeText()
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }

                        Button {
                            text: "Restore Database"
                            Layout.minimumWidth: 150
                            onClicked: root.restoreDbClicked()
                            background: Rectangle {
                                color: Theme.activeSurface()
                                border.color: Theme.activeBorder()
                                radius: Theme.radiusMd
                            }
                            contentItem: Text {
                                text: parent.text
                                color: Theme.activeText()
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
