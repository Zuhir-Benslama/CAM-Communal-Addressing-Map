import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

Rectangle {
    id: root

    property var bridge: null
    property string listTitle: ''

    color: Theme.activeBg()

    function setPageData(data) {
        tableModel.clear()
        headerModel.clear()

        for (var i = 0; i < data.labels.length; i++) {
            headerModel.append({ columnLabel: data.labels[i], columnIndex: i })
        }

        for (var i = 0; i < data.rows.length; i++) {
            var item = {}
            for (var j = 0; j < data.fields.length; j++) {
                item['col' + j] = String(
                    data.rows[i][j] !== null && data.rows[i][j] !== undefined
                    ? data.rows[i][j] : 'N/A'
                )
            }
            tableModel.append(item)
        }

        var totalPages = Math.max(1, Math.ceil(data.total / data.pageSize))
        pageLabel.text = (data.page + 1) + ' / ' + totalPages
        totalLabel.text = qsTr('Total') + ': ' + data.total
        prevBtn.enabled = data.page > 0
        nextBtn.enabled = (data.page + 1) < totalPages
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            color: Theme.activeSurface()
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            border.color: Theme.activeBorder()
            border.width: 1
            radius: 8

            Label {
                anchors.centerIn: parent
                text: listTitle
                color: Theme.activeText()
                font.bold: true
                font.pixelSize: 14
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded

            Column {
                id: tableColumn
                width: parent.width
                spacing: 0
                topPadding: 4
                bottomPadding: 4

                Rectangle {
                    width: parent.width
                    height: 32
                    color: Theme.activeOverlay()
                    radius: 4
                    visible: headerModel.count > 0

                    Row {
                        anchors.fill: parent
                        anchors.leftMargin: 1
                        spacing: 0

                        Repeater {
                            model: headerModel

                            Rectangle {
                                width: tableColumn.width / Math.max(1, headerModel.count) - 1
                                height: parent.height
                                color: 'transparent'

                                Text {
                                    anchors.centerIn: parent
                                    text: columnLabel
                                    color: Theme.activeText()
                                    font.bold: true
                                    font.pixelSize: 11
                                    elide: Text.ElideRight
                                }
                            }
                        }
                    }
                }

                Repeater {
                    model: tableModel

                    delegate: Item {
                        id: rowItem
                        property var rowData: model

                        width: tableColumn.width
                        height: 30

                        Rectangle {
                            anchors.fill: parent
                            color: index % 2 === 0 ? Theme.activeBg() : Theme.activeSurface()

                            Row {
                                anchors.fill: parent
                                anchors.leftMargin: 1
                                spacing: 0

                                Repeater {
                                    model: headerModel

                                    Text {
                                        width: rowItem.width / Math.max(1, headerModel.count) - 1
                                        height: parent.height
                                        verticalAlignment: Text.AlignVCenter
                                        leftPadding: 8
                                        text: {
                                            var val = rowItem.rowData['col' + model.columnIndex]
                                            return val !== undefined ? val : 'N/A'
                                        }
                                        color: Theme.activeText()
                                        font.pixelSize: 11
                                        elide: Text.ElideRight
                                    }
                                }
                            }
                        }
                    }
                }

                Item { width: 1; height: 8 }
            }
        }

        Rectangle {
            color: Theme.activeSurface()
            Layout.fillWidth: true
            Layout.preferredHeight: 100
            border.color: Theme.activeBorder()
            border.width: 1
            radius: 8

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8

                Label {
                    id: totalLabel
                    text: qsTr('Total') + ': 0'
                    color: Theme.activeTextSec()
                    font.pixelSize: 11
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 12

                    Button {
                        id: prevBtn
                        text: qsTr('Previous')
                        enabled: false
                        implicitWidth: 120
                        implicitHeight: 34

                        contentItem: Text {
                            text: parent.text
                            color: parent.enabled ? Theme.activeText() : Theme.activeTextSec()
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        background: Rectangle {
                            color: parent.enabled
                                   ? (parent.pressed ? Theme.activeSelection() : Theme.activeSurface())
                                   : Theme.activeOverlay()
                            border.color: parent.enabled ? Theme.activeBorder() : 'transparent'
                            border.width: 1
                            radius: Theme.borderRadius
                        }

                        onClicked: {
                            if (bridge) bridge.prevPage()
                        }
                    }

                    Label {
                        id: pageLabel
                        text: '1 / 1'
                        color: Theme.activeText()
                        font.bold: true
                        font.pixelSize: 12
                        horizontalAlignment: Text.AlignHCenter
                    }

                    Button {
                        id: nextBtn
                        text: qsTr('Next')
                        enabled: false
                        implicitWidth: 120
                        implicitHeight: 34

                        contentItem: Text {
                            text: parent.text
                            color: parent.enabled ? Theme.activeText() : Theme.activeTextSec()
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        background: Rectangle {
                            color: parent.enabled
                                   ? (parent.pressed ? Theme.activeSelection() : Theme.activeSurface())
                                   : Theme.activeOverlay()
                            border.color: parent.enabled ? Theme.activeBorder() : 'transparent'
                            border.width: 1
                            radius: Theme.borderRadius
                        }

                        onClicked: {
                            if (bridge) bridge.nextPage()
                        }
                    }
                }

                Label {
                    text: qsTr('Space Applications Center 2025 (c)')
                    color: Theme.activeTextSec()
                    font.pixelSize: 10
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }
            }
        }
    }

    ListModel { id: tableModel }
    ListModel { id: headerModel }
}
