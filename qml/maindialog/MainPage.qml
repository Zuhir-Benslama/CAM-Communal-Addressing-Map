import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

Item {
    id: root
    objectName: "main"

    property alias layerSelectorModel: layerSelector.model
    property alias layerSelectorIndex: layerSelector.currentIndex

    signal formSubmitted(string pageName)
    signal comboChanged(string objectName, int index, string currentData)
    signal selectRef(string objectName, string layerName)
    signal listRequested(string type)
    signal featureChanged(int index, string currentData)
    signal saveNewType
    signal actionChanged(int index, string currentData)
    signal saveAction
    signal gearClicked
    signal tabChanged(int index)
    signal drawClicked
    signal selectClicked
    signal editClicked
    signal measureClicked
    signal themeChanged(int index, string currentData)
    signal localeChanged(int index, string currentData)

    function getFieldText(name) {
        if (name === "label_username") return usernameLabel.text
        if (name === "nom_zone") return zoneForm.getFieldText(name)
        if (name === "road_name") return roadForm.getFieldText(name)
        if (name === "org_name") return orgForm.getFieldText(name)
        if (name === "subd_name") return subdForm.getFieldText(name)
        if (name === "road_ref") return numForm.getFieldText(name)
        if (name === "num_val") return numForm.getFieldText(name)
        if (name === "repetition") return numForm.getFieldText(name)
        if (name === "ref_name") return numForm.getFieldText(name)
        if (name === "ref_name2") return panForm.getFieldText(name)
        if (name === "lineEdit_type") return settingsTab.getFieldText(name)
        if (name === "lineEdit_by") return settingsTab.getFieldText(name)
        if (name === "lineEdit_nummokh") return settingsTab.getFieldText(name)
        if (name === "new_type") return settingsTab.getFieldText(name)
        if (name.startsWith("_")) {
            if (name === "_action_combo") return _safeComboValue(actionCombo)
        }
        return ""
    }

    function setFieldText(name, text) {
        if (name === "ref_name") numForm.setFieldText(name, text)
        else if (name === "ref_name2") panForm.setFieldText(name, text)
        else if (name === "lineEdit_type") settingsTab.setFieldText(name, text)
        else if (name === "lineEdit_by") settingsTab.setFieldText(name, text)
        else if (name === "lineEdit_nummokh") settingsTab.setFieldText(name, text)
        else if (name === "new_type") settingsTab.setFieldText(name, text)
        else if (name === "label_username") usernameLabel.text = text
    }

    function setComboIndex(name, index) {
        var combo = findCombo(name)
        if (combo) combo.currentIndex = index
    }

    function setComboOptions(name, options) {
        var combo = findCombo(name)
        if (!combo) return
        var model = []
        for (var i = 0; i < options.length; i++) {
            model.push({ text: options[i].text, value: options[i].value })
        }
        combo.model = model
    }

    function clearCombo(name) {
        var combo = findCombo(name)
        if (combo) combo.model = []
    }

    function addComboItem(name, text, value) {
        var combo = findCombo(name)
        if (!combo) return
        var m = combo.model
        m.push({ text: text, value: value })
        combo.model = m
    }

    function getComboIndex(name) {
        var combo = findCombo(name)
        return combo ? combo.currentIndex : -1
    }

    function getComboData(name, index) {
        var combo = findCombo(name)
        if (!combo || index < 0) return ""
        var item = combo.model[index]
        return item ? item.value : ""
    }

    function getComboText(name, index) {
        var combo = findCombo(name)
        if (!combo || index < 0) return ""
        var item = combo.model[index]
        return item ? item.text : ""
    }

    function getComboCount(name) {
        var combo = findCombo(name)
        return combo ? combo.model.length : 0
    }

    function setComboItemText(name, index, text) {
        var combo = findCombo(name)
        if (!combo || index < 0) return
        var m = combo.model
        if (index < m.length) {
            m[index].text = text
            combo.model = m
        }
    }

    function findComboByData(name, value) {
        var combo = findCombo(name)
        if (!combo) return -1
        for (var i = 0; i < combo.model.length; i++) {
            if (String(combo.model[i].value) === String(value)) return i
        }
        return -1
    }

    function findCombo(name) {
        var map = {
            "layer_selector": layerSelector,
            "zone_type": zoneForm.zoneTypeCombo,
            "type_road": roadForm.roadTypeCombo,
            "org_cat": orgForm.orgCatCombo,
            "org_type": orgForm.orgTypeCombo,
            "subd_type": subdForm.subdTypeCombo,
            "road_ref": numForm.roadRefCombo,
            "num_state": numForm.numStateCombo,
            "activity_cat": numForm.activityCatCombo,
            "activity_type": numForm.activityTypeCombo,
            "mount_status": panForm.mountStatusCombo,
            "panel_ref": panForm.panelRefCombo,
            "feature_combo": settingsTab.featureCombo,
            "subtype_combo": settingsTab.subtypeCombo,
            "paper": settingsTab.paperCombo,
        }
        return map[name] || null
    }

    function _safeComboValue(combo) {
        return combo.currentIndex >= 0 ? combo.currentValue : combo.displayText
    }

    function setFormStackIndex(index) {
        formStack.currentIndex = index
    }

    function setSettingsTabIndex(index) {
        mainTabBar.currentIndex = index
    }

    function toggleSettingsTab() {
        mainTabBar.currentIndex = mainTabBar.currentIndex === 0 ? 1 : 0
    }

    function setCurrentLayerName(name) {
        var m = layerSelector.model
        var cnt = m.count !== undefined ? m.count : (m.length !== undefined ? m.length : 0)
        for (var i = 0; i < cnt; i++) {
            var item = m.get ? m.get(i) : m[i]
            if (item && item.text === name) {
                layerSelector.currentIndex = i
                return
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        color: Theme.activeSurface()

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            Rectangle {
                id: toolbarFrame
                Layout.fillWidth: true
                Layout.minimumHeight: 48
                color: Theme.activeSurface()
                border.color: Theme.activeBorder()

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Theme.paddingMd
                    anchors.rightMargin: Theme.paddingMd
                    spacing: Theme.spacingSm

                    Text {
                        id: usernameLabel
                        objectName: "label_username"
                        font.bold: true
                        color: Theme.activeText()
                        Layout.fillWidth: true
                        verticalAlignment: Text.AlignVCenter
                    }

                    Button {
                        id: gearBtn
                        text: "\u2699"
                        font.pixelSize: 18
                        onClicked: root.gearClicked()
                        background: Rectangle {
                            color: "transparent"
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

            Rectangle {
                id: formPanel
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Theme.activeSurface()
                border.color: Theme.activeBorder()

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    ComboBox {
                        id: layerSelector
                        objectName: "layer_selector"
                        Layout.fillWidth: true
                        Layout.leftMargin: Theme.paddingMd
                        Layout.rightMargin: Theme.paddingMd
                        textRole: "text"
                        valueRole: "value"
                        onCurrentIndexChanged: root.comboChanged("layer_selector", currentIndex, currentValue)
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

                    RowLayout {
                        Layout.fillWidth: true
                        Layout.leftMargin: Theme.paddingMd
                        Layout.rightMargin: Theme.paddingMd
                        spacing: Theme.spacingSm

                        Button {
                            id: drawBtn
                            text: qsTr("Draw")
                            font.bold: true
                            Layout.minimumWidth: 100
                            onClicked: root.drawClicked()
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
                        Button {
                            id: selectBtn
                            text: qsTr("Select")
                            font.bold: true
                            Layout.minimumWidth: 100
                            onClicked: root.selectClicked()
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
                        Button {
                            id: editBtn
                            text: qsTr("Edit")
                            font.bold: true
                            Layout.minimumWidth: 100
                            onClicked: root.editClicked()
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
                        Button {
                            id: measureBtn
                            text: qsTr("Measure Distance")
                            Layout.minimumWidth: 100
                            onClicked: root.measureClicked()
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

                    StackLayout {
                        id: formStack
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.leftMargin: Theme.paddingMd
                        Layout.rightMargin: Theme.paddingMd

                        ZoneForm {
                            id: zoneForm
                            onComboChanged: root.comboChanged(objectName, index, currentData)
                            onFormSubmitted: root.formSubmitted(pageName)
                        }

                        RoadForm {
                            id: roadForm
                            onComboChanged: root.comboChanged(objectName, index, currentData)
                            onFormSubmitted: root.formSubmitted(pageName)
                            onListRequested: root.listRequested(type)
                        }

                        OrgForm {
                            id: orgForm
                            onComboChanged: root.comboChanged(objectName, index, currentData)
                            onFormSubmitted: root.formSubmitted(pageName)
                            onListRequested: root.listRequested(type)
                        }

                        CityForm {
                            id: subdForm
                            onComboChanged: root.comboChanged(objectName, index, currentData)
                            onFormSubmitted: root.formSubmitted(pageName)
                            onListRequested: root.listRequested(type)
                        }

                        NumForm {
                            id: numForm
                            onComboChanged: root.comboChanged(objectName, index, currentData)
                            onFormSubmitted: root.formSubmitted(pageName)
                            onListRequested: root.listRequested(type)
                            onSelectRef: root.selectRef(objectName, layerName)
                        }

                        PanForm {
                            id: panForm
                            onComboChanged: root.comboChanged(objectName, index, currentData)
                            onFormSubmitted: root.formSubmitted(pageName)
                            onListRequested: root.listRequested(type)
                            onSelectRef: root.selectRef(objectName, layerName)
                        }
                    }

                    Item { Layout.fillHeight: true }
                }
            }

            Item {
                id: settingsTab
                    function getFieldText(name) {
                        var map = {
                            "lineEdit_type": typeField.text,
                            "lineEdit_by": byField.text,
                            "lineEdit_nummokh": numMokhField.text,
                            "new_type": newTypeField.text,
                        }
                        return map[name] !== undefined ? map[name] : ""
                    }
                    function setFieldText(name, text) {
                        if (name === "lineEdit_type") typeField.text = text
                        else if (name === "lineEdit_by") byField.text = text
                        else if (name === "lineEdit_nummokh") numMokhField.text = text
                        else if (name === "new_type") newTypeField.text = text
                    }
                    property alias featureCombo: featureCombo
                    property alias subtypeCombo: subtypeCombo
                    property alias paperCombo: paperCombo

                    Flickable {
                        anchors.fill: parent
                        contentHeight: settingsColumn.height + 20
                        clip: true

                        ColumnLayout {
                            id: settingsColumn
                            width: parent.width - Theme.spacingLg
                            anchors.horizontalCenter: parent.horizontalCenter
                            spacing: Theme.spacingMd

                            Frame {
                                Layout.fillWidth: true
                                Layout.leftMargin: Theme.paddingSm
                                Layout.rightMargin: Theme.paddingSm
                                padding: Theme.paddingMd
                                topPadding: Theme.paddingLg
                                background: Rectangle {
                                    color: Theme.activeBg()
                                    radius: Theme.radiusLg
                                    border.color: Theme.activeBorder()
                                }

                                ColumnLayout {
                                    anchors.fill: parent
                                    spacing: Theme.spacingSm

                                    Text { text: "Maps, Reports and Backup"; font.bold: true; font.pixelSize: Theme.fontHeadline; color: Theme.activeAccent() }
                                    Rectangle { height: 1; color: Theme.activeBorder(); Layout.fillWidth: true; Layout.topMargin: 2; Layout.bottomMargin: 4 }

                                    ComboBox {
                                        id: actionCombo
                                        objectName: "_action_combo"
                                        Layout.fillWidth: true
                                        textRole: "text"
                                        valueRole: "value"
                                        onCurrentIndexChanged: root.actionChanged(currentIndex, currentValue)
                                        background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                                        contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
                                    }

                                    ComboBox {
                                        id: paperCombo
                                        objectName: "paper"
                                        visible: false
                                        Layout.fillWidth: true
                                        textRole: "text"
                                        valueRole: "value"
                                        background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                                        contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
                                    }

                                    Button {
                                        id: saveActionBtn
                                        text: "Save"
                                        font.bold: true
                                        Layout.fillWidth: true
                                        onClicked: root.saveAction()
                                        background: Rectangle { color: Theme.activeAccent(); radius: Theme.radiusMd }
                                        contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                    }
                                }
                            }

                            Frame {
                                Layout.fillWidth: true
                                Layout.leftMargin: Theme.paddingSm
                                Layout.rightMargin: Theme.paddingSm
                                padding: Theme.paddingMd
                                topPadding: Theme.paddingLg
                                background: Rectangle {
                                    color: Theme.activeBg()
                                    radius: Theme.radiusLg
                                    border.color: Theme.activeBorder()
                                }

                                ColumnLayout {
                                    anchors.fill: parent
                                    spacing: Theme.spacingSm

                                    Text { text: "Study Area"; font.bold: true; font.pixelSize: Theme.fontHeadline; color: Theme.activeAccent() }
                                    Rectangle { height: 1; color: Theme.activeBorder(); Layout.fillWidth: true; Layout.topMargin: 2; Layout.bottomMargin: 4 }

                                    GridLayout {
                                        columns: 2
                                        columnSpacing: Theme.spacingSm
                                        rowSpacing: Theme.spacingSm
                                        Layout.fillWidth: true
                                        Text { text: "Study Area:"; color: Theme.activeText() }
                                        TextField { id: typeField; objectName: "lineEdit_type"; Layout.fillWidth: true; color: Theme.activeText(); background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd } }
                                        Text { text: "Produced by:"; color: Theme.activeText() }
                                        TextField { id: byField; objectName: "lineEdit_by"; Layout.fillWidth: true; color: Theme.activeText(); background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd } }
                                        Text { text: "Plan Number:"; color: Theme.activeText() }
                                        TextField { id: numMokhField; objectName: "lineEdit_nummokh"; Layout.fillWidth: true; color: Theme.activeText(); background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd } }
                                        Text { text: "Date:"; color: Theme.activeText() }
                                        TextField { id: dateField; objectName: "dateEdit"; Layout.fillWidth: true; color: Theme.activeText(); background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd } }
                                    }

                                }
                            }

                            Frame {
                                Layout.fillWidth: true
                                Layout.leftMargin: Theme.paddingSm
                                Layout.rightMargin: Theme.paddingSm
                                padding: Theme.paddingMd
                                topPadding: Theme.paddingLg
                                background: Rectangle {
                                    color: Theme.activeBg()
                                    radius: Theme.radiusLg
                                    border.color: Theme.activeBorder()
                                }

                                ColumnLayout {
                                    anchors.fill: parent
                                    spacing: Theme.spacingSm

                                    Text { text: "Add New Feature"; font.bold: true; font.pixelSize: Theme.fontHeadline; color: Theme.activeAccent() }
                                    Rectangle { height: 1; color: Theme.activeBorder(); Layout.fillWidth: true; Layout.topMargin: 2; Layout.bottomMargin: 4 }

                                    GridLayout {
                                        columns: 2
                                        columnSpacing: Theme.spacingSm
                                        rowSpacing: Theme.spacingSm
                                        Layout.fillWidth: true
                                        Text { text: "Category:"; font.bold: true; color: Theme.activeText(); Layout.minimumWidth: 100 }
                                        ComboBox {
                                            id: featureCombo
                                            objectName: "feature_combo"
                                            Layout.fillWidth: true
                                            textRole: "text"
                                            valueRole: "value"
                                            onCurrentIndexChanged: root.featureChanged(currentIndex, currentValue)
                                            background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                                            contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
                                        }
                                        Text { text: "Type:"; font.bold: true; color: Theme.activeText(); Layout.minimumWidth: 100 }
                                        ComboBox {
                                            id: subtypeCombo
                                            objectName: "subtype_combo"
                                            Layout.fillWidth: true
                                            editable: true
                                            textRole: "text"
                                            valueRole: "value"
                                            background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                                            contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
                                        }
                                        Text { text: "Subtype:"; objectName: "label_subtype"; font.bold: true; color: Theme.activeText(); Layout.minimumWidth: 100 }
                                        TextField {
                                            id: newTypeField
                                            objectName: "new_type"
                                            Layout.fillWidth: true
                                            visible: true
                                            color: Theme.activeText()
                                            background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                                        }
                                    }
                                    Button {
                                        text: "Save"
                                        font.bold: true
                                        Layout.fillWidth: true
                                        onClicked: root.saveNewType()
                                        background: Rectangle { color: Theme.activeAccent(); radius: Theme.radiusMd }
                                        contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                    }
                                }
                            }

                            Frame {
                                Layout.fillWidth: true
                                Layout.leftMargin: Theme.paddingSm
                                Layout.rightMargin: Theme.paddingSm
                                padding: Theme.paddingMd
                                topPadding: Theme.paddingLg
                                background: Rectangle {
                                    color: Theme.activeBg()
                                    radius: Theme.radiusLg
                                    border.color: Theme.activeBorder()
                                }

                                ColumnLayout {
                                    anchors.fill: parent
                                    spacing: Theme.spacingSm

                                    Text { text: "Theme and Language"; font.bold: true; font.pixelSize: Theme.fontHeadline; color: Theme.activeAccent() }
                                    Rectangle { height: 1; color: Theme.activeBorder(); Layout.fillWidth: true; Layout.topMargin: 2; Layout.bottomMargin: 4 }

                                    GridLayout {
                                        columns: 2
                                        columnSpacing: Theme.spacingSm
                                        rowSpacing: Theme.spacingSm
                                        Layout.fillWidth: true
                                        Text { text: "Theme:"; color: Theme.activeText() }
                                        ComboBox {
                                            id: themeCombo
                                            objectName: "_theme_combo"
                                            Layout.fillWidth: true
                                            textRole: "text"
                                            valueRole: "value"
                                            onCurrentIndexChanged: root.themeChanged(currentIndex, currentValue)
                                            background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                                            contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
                                        }
                                        Text { text: "Language:"; color: Theme.activeText() }
                                        ComboBox {
                                            id: localeCombo
                                            objectName: "_locale_combo"
                                            Layout.fillWidth: true
                                            textRole: "text"
                                            valueRole: "value"
                                            onCurrentIndexChanged: root.localeChanged(currentIndex, currentValue)
                                            background: Rectangle { color: Theme.activeSurface(); border.color: Theme.activeBorder(); radius: Theme.radiusMd }
                                            contentItem: Text { text: parent.displayText; color: Theme.activeText(); verticalAlignment: Text.AlignVCenter }
                                        }
                                    }
                                }
                            }

                            Item { height: Theme.spacingLg }
                        }
                    }
                }

            Rectangle {
                id: footerFrame
                Layout.fillWidth: true
                Layout.minimumHeight: 36
                Layout.maximumHeight: 36
                color: Theme.activeSurface()
                border.color: Theme.activeBorder()

                Text {
                    anchors.left: parent.left
                    anchors.leftMargin: Theme.paddingMd
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Space Applications Center 2025 \u00a9"
                    font.pixelSize: Theme.fontCaption
                    font.bold: true
                    color: Theme.activeText()
                }
            }
        }
    }
}
