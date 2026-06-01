import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0
import PopupPages 1.0

Rectangle {
    id: root

    property string layerNameValue: ""
    property string layerNameKey: ""
    property bool isDark: true

    property var pluginBridge: null

    color: Theme.activeBg()

    onIsDarkChanged: Theme.isDark = isDark

    onLayerNameValueChanged: {
        switchToPage(layerNameValue)
    }

    function switchToPage(pageKey) {
        for (var i = 0; i < stackLayout.children.length; i++) {
            var child = stackLayout.children[i]
            if (child.pageKey === pageKey) {
                stackLayout.currentIndex = i
                return
            }
        }
    }

    function setFormData(data) {
        var current = stackLayout.currentItem
        if (current && current.setFormData) current.setFormData(data)
    }

    function setComboOptions(options) {
        var current = stackLayout.currentItem
        if (current && current.setComboOptions) current.setComboOptions(options)
    }

    function setReferenceName(name) {
        var current = stackLayout.currentItem
        if (current && current.setReferenceName) current.setReferenceName(name)
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.padding
        spacing: Theme.spacing

        Label {
            text: layerNameKey
            color: Theme.activeText()
            font.bold: true
            font.pixelSize: 14
            Layout.fillWidth: true
        }

        StackLayout {
            id: stackLayout
            Layout.fillWidth: true
            Layout.fillHeight: true

            ZonePage {
                onSaveRequested: {
                    if (pluginBridge) pluginBridge.saveForm(pageKey, getFormData())
                }
            }
            RoadsPage {
                onSaveRequested: {
                    if (pluginBridge) pluginBridge.saveForm(pageKey, getFormData())
                }
            }
            OrgPage {
                onSaveRequested: {
                    if (pluginBridge) pluginBridge.saveForm(pageKey, getFormData())
                }
                onCatChanged: function(index) {
                    if (pluginBridge) pluginBridge.onOrgCatChanged(index)
                }
            }
            CityPage {
                onSaveRequested: {
                    if (pluginBridge) pluginBridge.saveForm(pageKey, getFormData())
                }
            }
            NumPage {
                onSaveRequested: {
                    if (pluginBridge) pluginBridge.saveForm(pageKey, getFormData())
                }
                onSelectReferenceRequested: function(layerName) {
                    if (pluginBridge) pluginBridge.selectReference(pageKey, layerName)
                }
                onCatChanged: function(index) {
                    if (pluginBridge) pluginBridge.onActivityCatChanged(index)
                }
            }
            PanPage {
                onSaveRequested: {
                    if (pluginBridge) pluginBridge.saveForm(pageKey, getFormData())
                }
                onSelectReferenceRequested: function(layerName) {
                    if (pluginBridge) pluginBridge.selectReference(pageKey, layerName)
                }
            }
        }

        Label {
            text: "Space Applications Center 2025 (c)"
            color: Theme.activeTextSec()
            font.pixelSize: 10
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
            Layout.topMargin: 4
        }
    }
}
