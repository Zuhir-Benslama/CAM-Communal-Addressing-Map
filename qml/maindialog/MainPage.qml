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
            if (name === "_action_combo") return actionCombo.currentValue
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

    function setFormStackIndex(index) {
        formStack.currentIndex = index
    }

    function setSettingsTabIndex(index) {
        mainTabBar.currentIndex = index
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
        color: Theme.surface

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            Rectangle {
                id: toolbarFrame
                Layout.fillWidth: true
                Layout.minimumHeight: 48
                color: Theme.surface
                border.color: Theme.border

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 5
                    anchors.rightMargin: 5
                    spacing: 5

                    Text {
                        id: usernameLabel
                        objectName: "label_username"
                        font.bold: true
                        color: Theme.text
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

            TabBar {
                id: mainTabBar
                visible: false
                onCurrentIndexChanged: root.tabChanged(currentIndex)
            }

            StackLayout {
                id: mainStack
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: mainTabBar.currentIndex

                Item {
                    id: operationsTab
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 4

                        ComboBox {
                            id: layerSelector
                            objectName: "layer_selector"
                            Layout.fillWidth: true
                            Layout.leftMargin: 4
                            Layout.rightMargin: 4
                            textRole: "text"
                            valueRole: "value"
                            onCurrentIndexChanged: root.comboChanged("layer_selector", currentIndex, currentValue)
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

                        RowLayout {
                            Layout.fillWidth: true
                            Layout.leftMargin: 4
                            Layout.rightMargin: 4
                            spacing: 4

                            Button {
                                id: drawBtn
                                text: "Draw"
                                font.bold: true
                                Layout.minimumWidth: 100
                                onClicked: root.drawClicked()
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
                            Button {
                                id: selectBtn
                                text: "Select"
                                font.bold: true
                                Layout.minimumWidth: 100
                                onClicked: root.selectClicked()
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
                            Button {
                                id: editBtn
                                text: "Edit"
                                font.bold: true
                                Layout.minimumWidth: 100
                                onClicked: root.editClicked()
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
                            Button {
                                id: measureBtn
                                text: "Measure Distance"
                                Layout.minimumWidth: 100
                                onClicked: root.measureClicked()
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

                        StackLayout {
                            id: formStack
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.leftMargin: 4
                            Layout.rightMargin: 4

                            // Page 0: Zone
                            Item {
                                id: zoneForm
                                property alias zoneTypeCombo: zoneTypeCombo
                                function getFieldText(name) {
                                    if (name === "nom_zone") return zoneNameField.text
                                    return ""
                                }
                                ColumnLayout {
                                    anchors.fill: parent
                                    GridLayout {
                                        columns: 2
                                        columnSpacing: 10
                                        rowSpacing: 10
                                        Layout.fillWidth: true
                                        Text { text: "Type:"; font.bold: true; color: Theme.text }
                                        ComboBox {
                                            id: zoneTypeCombo
                                            objectName: "zone_type"
                                            Layout.fillWidth: true
                                            editable: true
                                            textRole: "text"
                                            valueRole: "value"
                                            onCurrentIndexChanged: root.comboChanged("zone_type", currentIndex, currentValue)
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Text { text: "Name:"; font.bold: true; color: Theme.text }
                                        TextField {
                                            id: zoneNameField
                                            objectName: "nom_zone"
                                            Layout.fillWidth: true
                                            color: Theme.text
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                        }
                                    }
                                    Item { Layout.fillHeight: true }
                                    Button {
                                        text: "Save"
                                        font.bold: true
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.minimumWidth: 200
                                        onClicked: root.formSubmitted("zone")
                                        background: Rectangle { color: Theme.primary; radius: 4 }
                                        contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                    }
                                    Item { Layout.fillHeight: true }
                                }
                            }

                            // Page 1: Road
                            Item {
                                id: roadForm
                                property alias roadTypeCombo: roadTypeCombo
                                function getFieldText(name) {
                                    if (name === "road_name") return roadNameField.text
                                    return ""
                                }
                                ColumnLayout {
                                    anchors.fill: parent
                                    GridLayout {
                                        columns: 2
                                        columnSpacing: 10
                                        rowSpacing: 10
                                        Layout.fillWidth: true
                                        Text { text: "Type:"; font.bold: true; color: Theme.text }
                                        ComboBox {
                                            id: roadTypeCombo
                                            objectName: "type_road"
                                            Layout.fillWidth: true
                                            editable: true
                                            textRole: "text"
                                            valueRole: "value"
                                            onCurrentIndexChanged: root.comboChanged("type_road", currentIndex, currentValue)
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Text { text: "Name:"; font.bold: true; color: Theme.text }
                                        TextField {
                                            id: roadNameField
                                            objectName: "road_name"
                                            Layout.fillWidth: true
                                            color: Theme.text
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                        }
                                    }
                                    Item { Layout.fillHeight: true }
                                    RowLayout {
                                        Layout.alignment: Qt.AlignHCenter
                                        spacing: 20
                                        Button {
                                            text: "Save"
                                            font.bold: true
                                            Layout.minimumWidth: 200
                                            onClicked: root.formSubmitted("road")
                                            background: Rectangle { color: Theme.primary; radius: 4 }
                                            contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Button {
                                            text: "Roads List"
                                            Layout.minimumWidth: 150
                                            onClicked: root.listRequested("roads")
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.text; color: Theme.text; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                        }
                                    }
                                    Item { Layout.fillHeight: true }
                                }
                            }

                            // Page 2: Organization
                            Item {
                                id: orgForm
                                property alias orgCatCombo: orgCatCombo
                                property alias orgTypeCombo: orgTypeCombo
                                function getFieldText(name) {
                                    if (name === "org_name") return orgNameField.text
                                    return ""
                                }
                                ColumnLayout {
                                    anchors.fill: parent
                                    GridLayout {
                                        columns: 2
                                        columnSpacing: 10
                                        rowSpacing: 10
                                        Layout.fillWidth: true
                                        Text { text: "Category:"; font.bold: true; color: Theme.text }
                                        ComboBox {
                                            id: orgCatCombo
                                            objectName: "org_cat"
                                            Layout.fillWidth: true
                                            editable: true
                                            textRole: "text"
                                            valueRole: "value"
                                            onCurrentIndexChanged: root.comboChanged("org_cat", currentIndex, currentValue)
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Text { text: "Type:"; font.bold: true; color: Theme.text }
                                        ComboBox {
                                            id: orgTypeCombo
                                            objectName: "org_type"
                                            Layout.fillWidth: true
                                            editable: true
                                            textRole: "text"
                                            valueRole: "value"
                                            onCurrentIndexChanged: root.comboChanged("org_type", currentIndex, currentValue)
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Text { text: "Name:"; font.bold: true; color: Theme.text }
                                        TextField {
                                            id: orgNameField
                                            objectName: "org_name"
                                            Layout.fillWidth: true
                                            color: Theme.text
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                        }
                                    }
                                    Item { Layout.fillHeight: true }
                                    RowLayout {
                                        Layout.alignment: Qt.AlignHCenter
                                        spacing: 20
                                        Button {
                                            text: "Save"
                                            font.bold: true
                                            Layout.minimumWidth: 200
                                            onClicked: root.formSubmitted("org")
                                            background: Rectangle { color: Theme.primary; radius: 4 }
                                            contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Button {
                                            text: "Facilities List"
                                            Layout.minimumWidth: 150
                                            onClicked: root.listRequested("orgs")
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.text; color: Theme.text; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                        }
                                    }
                                    Item { Layout.fillHeight: true }
                                }
                            }

                            // Page 3: Subdivision / City
                            Item {
                                id: subdForm
                                property alias subdTypeCombo: subdTypeCombo
                                function getFieldText(name) {
                                    if (name === "subd_name") return subdNameField.text
                                    return ""
                                }
                                ColumnLayout {
                                    anchors.fill: parent
                                    GridLayout {
                                        columns: 2
                                        columnSpacing: 10
                                        rowSpacing: 10
                                        Layout.fillWidth: true
                                        Text { text: "Type:"; font.bold: true; color: Theme.text }
                                        ComboBox {
                                            id: subdTypeCombo
                                            objectName: "subd_type"
                                            Layout.fillWidth: true
                                            editable: true
                                            textRole: "text"
                                            valueRole: "value"
                                            onCurrentIndexChanged: root.comboChanged("subd_type", currentIndex, currentValue)
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Text { text: "Name:"; font.bold: true; color: Theme.text }
                                        TextField {
                                            id: subdNameField
                                            objectName: "subd_name"
                                            Layout.fillWidth: true
                                            color: Theme.text
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                        }
                                    }
                                    Item { Layout.fillHeight: true }
                                    RowLayout {
                                        Layout.alignment: Qt.AlignHCenter
                                        spacing: 20
                                        Button {
                                            text: "Save"
                                            font.bold: true
                                            Layout.minimumWidth: 200
                                            onClicked: root.formSubmitted("city")
                                            background: Rectangle { color: Theme.primary; radius: 4 }
                                            contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Button {
                                            text: "Subdivisions List"
                                            Layout.minimumWidth: 150
                                            onClicked: root.listRequested("subds")
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.text; color: Theme.text; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                        }
                                    }
                                    Item { Layout.fillHeight: true }
                                }
                            }

                            // Page 4: Numbering
                            Item {
                                id: numForm
                                property alias roadRefCombo: roadRefCombo
                                property alias numStateCombo: numStateCombo
                                property alias activityCatCombo: activityCatCombo
                                property alias activityTypeCombo: activityTypeCombo
                                function getFieldText(name) {
                                    if (name === "road_ref") return roadRefCombo.currentValue
                                    if (name === "num_val") return numValField.text
                                    if (name === "repetition") return repField.text
                                    if (name === "ref_name") return refNameLabel.text
                                    return ""
                                }
                                function setFieldText(name, text) {
                                    if (name === "ref_name") refNameLabel.text = text
                                }
                                Flickable {
                                    anchors.fill: parent
                                    contentHeight: numColumn.height
                                    clip: true
                                    ColumnLayout {
                                        id: numColumn
                                        width: parent.width
                                        spacing: 10
                                        GridLayout {
                                            columns: 2
                                            columnSpacing: 10
                                            rowSpacing: 10
                                            Layout.fillWidth: true
                                            Text { text: "Reference Type:"; font.bold: true; color: Theme.text }
                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                ComboBox {
                                                    id: roadRefCombo
                                                    objectName: "road_ref"
                                                    Layout.fillWidth: true
                                                    editable: true
                                                    textRole: "text"
                                                    valueRole: "value"
                                                    onCurrentIndexChanged: root.comboChanged("road_ref", currentIndex, currentValue)
                                                    background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                                    contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                                }
                                                Button {
                                                    text: "Select Reference"
                                                    font.bold: true
                                                    Layout.fillWidth: true
                                                    onClicked: root.selectRef("road_ref", roadRefCombo.currentValue)
                                                    background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                                    contentItem: Text { text: parent.text; color: Theme.text; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                                }
                                                Text {
                                                    id: refNameLabel
                                                    objectName: "ref_name"
                                                    font.bold: true
                                                    color: Theme.text
                                                    wrapMode: Text.WordWrap
                                                }
                                            }
                                        }
                                        GridLayout {
                                            columns: 2
                                            columnSpacing: 10
                                            rowSpacing: 10
                                            Layout.fillWidth: true
                                            Text { text: "Number:"; font.bold: true; color: Theme.text }
                                            TextField {
                                                id: numValField
                                                objectName: "num_val"
                                                Layout.fillWidth: true
                                                color: Theme.text
                                                background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            }
                                            Text { text: "Duplicated:"; font.bold: true; color: Theme.text }
                                            TextField {
                                                id: repField
                                                objectName: "repetition"
                                                Layout.fillWidth: true
                                                color: Theme.text
                                                background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            }
                                            Text { text: "State:"; font.bold: true; color: Theme.text }
                                            ComboBox {
                                                id: numStateCombo
                                                objectName: "num_state"
                                                Layout.fillWidth: true
                                                editable: true
                                                textRole: "text"
                                                valueRole: "value"
                                                background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                                contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                            }
                                        }
                                        Rectangle {
                                            color: Theme.border
                                            height: 1
                                            Layout.fillWidth: true
                                        }
                                        Text { text: "Activity"; font.bold: true; color: Theme.text }
                                        GridLayout {
                                            columns: 2
                                            columnSpacing: 10
                                            rowSpacing: 10
                                            Layout.fillWidth: true
                                            Text { text: "Category:"; font.bold: true; color: Theme.text }
                                            ComboBox {
                                                id: activityCatCombo
                                                objectName: "activity_cat"
                                                Layout.fillWidth: true
                                                editable: true
                                                textRole: "text"
                                                valueRole: "value"
                                                onCurrentIndexChanged: root.comboChanged("activity_cat", currentIndex, currentValue)
                                                background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                                contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                            }
                                            Text { text: "Type:"; font.bold: true; color: Theme.text }
                                            ComboBox {
                                                id: activityTypeCombo
                                                objectName: "activity_type"
                                                Layout.fillWidth: true
                                                editable: true
                                                textRole: "text"
                                                valueRole: "value"
                                                background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                                contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                            }
                                        }
                                        RowLayout {
                                            Layout.alignment: Qt.AlignHCenter
                                            spacing: 20
                                            Button {
                                                text: "Save"
                                                font.bold: true
                                                Layout.minimumWidth: 200
                                                onClicked: root.formSubmitted("num")
                                                background: Rectangle { color: Theme.primary; radius: 4 }
                                                contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                            }
                                            Button {
                                                text: "Entrances List"
                                                Layout.minimumWidth: 150
                                                onClicked: root.listRequested("nums")
                                                background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                                contentItem: Text { text: parent.text; color: Theme.text; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                            }
                                        }
                                    }
                                }
                            }

                            // Page 5: Panels
                            Item {
                                id: panForm
                                property alias mountStatusCombo: mountStatusCombo
                                property alias panelRefCombo: panelRefCombo
                                function getFieldText(name) {
                                    if (name === "mount_status") return mountStatusCombo.currentValue
                                    if (name === "panel_ref") return panelRefCombo.currentValue
                                    if (name === "ref_name2") return refName2Label.text
                                    return ""
                                }
                                function setFieldText(name, text) {
                                    if (name === "ref_name2") refName2Label.text = text
                                }
                                ColumnLayout {
                                    anchors.fill: parent
                                    GridLayout {
                                        columns: 2
                                        columnSpacing: 10
                                        rowSpacing: 10
                                        Layout.fillWidth: true
                                        Text { text: "Mounting State:"; font.bold: true; color: Theme.text }
                                        ComboBox {
                                            id: mountStatusCombo
                                            objectName: "mount_status"
                                            Layout.fillWidth: true
                                            editable: true
                                            textRole: "text"
                                            valueRole: "value"
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Text { text: "Reference Type:"; font.bold: true; color: Theme.text }
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            ComboBox {
                                                id: panelRefCombo
                                                objectName: "panel_ref"
                                                Layout.fillWidth: true
                                                editable: true
                                                textRole: "text"
                                                valueRole: "value"
                                                background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                                contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                            }
                                            Button {
                                                text: "Select Reference"
                                                font.bold: true
                                                Layout.fillWidth: true
                                                onClicked: root.selectRef("panel_ref", panelRefCombo.currentValue)
                                                background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                                contentItem: Text { text: parent.text; color: Theme.text; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                            }
                                            Text {
                                                id: refName2Label
                                                objectName: "ref_name2"
                                                font.bold: true
                                                color: Theme.text
                                                wrapMode: Text.WordWrap
                                            }
                                        }
                                    }
                                    Item { Layout.fillHeight: true }
                                    RowLayout {
                                        Layout.alignment: Qt.AlignHCenter
                                        spacing: 20
                                        Button {
                                            text: "Save"
                                            font.bold: true
                                            Layout.minimumWidth: 200
                                            onClicked: root.formSubmitted("pan")
                                            background: Rectangle { color: Theme.primary; radius: 4 }
                                            contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Button {
                                            text: "Panels List"
                                            Layout.minimumWidth: 150
                                            onClicked: root.listRequested("panels")
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.text; color: Theme.text; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                        }
                                    }
                                    Item { Layout.fillHeight: true }
                                }
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
                            width: parent.width - 8
                            anchors.horizontalCenter: parent.horizontalCenter
                            spacing: 12

                            Rectangle {
                                color: Theme.background
                                radius: 6
                                border.color: Theme.border
                                Layout.fillWidth: true
                                Layout.leftMargin: 4
                                Layout.rightMargin: 4

                                ColumnLayout {
                                    x: 10; y: 10
                                    width: parent.width - 20
                                    spacing: 8

                                    Text { text: "Maps, Reports and Backup"; font.bold: true; color: Theme.text }

                                    ComboBox {
                                        id: actionCombo
                                        objectName: "_action_combo"
                                        Layout.fillWidth: true
                                        textRole: "text"
                                        valueRole: "value"
                                        onCurrentIndexChanged: root.actionChanged(currentIndex, currentValue)
                                        background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                        contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                    }

                                    ComboBox {
                                        id: paperCombo
                                        objectName: "paper"
                                        visible: false
                                        Layout.fillWidth: true
                                        textRole: "text"
                                        valueRole: "value"
                                        background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                        contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                    }

                                    Button {
                                        id: saveActionBtn
                                        text: "Save"
                                        font.bold: true
                                        Layout.fillWidth: true
                                        onClicked: root.saveAction()
                                        background: Rectangle { color: Theme.primary; radius: 4 }
                                        contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                    }
                                }
                            }

                            Rectangle {
                                color: Theme.background
                                radius: 6
                                border.color: Theme.border
                                Layout.fillWidth: true
                                Layout.leftMargin: 4
                                Layout.rightMargin: 4

                                ColumnLayout {
                                    x: 10; y: 10
                                    width: parent.width - 20
                                    spacing: 8

                                    Text { text: "Study Area"; font.bold: true; color: Theme.text }
                                    GridLayout {
                                        columns: 2
                                        columnSpacing: 10
                                        rowSpacing: 8
                                        Layout.fillWidth: true
                                        Text { text: "Study Area:"; color: Theme.text }
                                        TextField { id: typeField; objectName: "lineEdit_type"; Layout.fillWidth: true; color: Theme.text; background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 } }
                                        Text { text: "Produced by:"; color: Theme.text }
                                        TextField { id: byField; objectName: "lineEdit_by"; Layout.fillWidth: true; color: Theme.text; background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 } }
                                        Text { text: "Plan Number:"; color: Theme.text }
                                        TextField { id: numMokhField; objectName: "lineEdit_nummokh"; Layout.fillWidth: true; color: Theme.text; background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 } }
                                        Text { text: "Date:"; color: Theme.text }
                                        TextField { id: dateField; objectName: "dateEdit"; Layout.fillWidth: true; color: Theme.text; background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 } }
                                    }
                                    Button {
                                        text: "Generate Panels Map"
                                        Layout.fillWidth: true
                                        background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                        contentItem: Text { text: parent.text; color: Theme.text; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                    }
                                    Button {
                                        text: "Generate Numbering Map"
                                        Layout.fillWidth: true
                                        background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                        contentItem: Text { text: parent.text; color: Theme.text; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                    }
                                }
                            }

                            Rectangle {
                                color: Theme.background
                                radius: 6
                                border.color: Theme.border
                                Layout.fillWidth: true
                                Layout.leftMargin: 4
                                Layout.rightMargin: 4

                                ColumnLayout {
                                    x: 10; y: 10
                                    width: parent.width - 20
                                    spacing: 8

                                    Text { text: "Add New Feature"; font.bold: true; color: Theme.text }

                                    GridLayout {
                                        columns: 2
                                        columnSpacing: 10
                                        rowSpacing: 8
                                        Layout.fillWidth: true
                                        Text { text: "Category:"; font.bold: true; color: Theme.text; Layout.minimumWidth: 100 }
                                        ComboBox {
                                            id: featureCombo
                                            objectName: "feature_combo"
                                            Layout.fillWidth: true
                                            textRole: "text"
                                            valueRole: "value"
                                            onCurrentIndexChanged: root.featureChanged(currentIndex, currentValue)
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Text { text: "Type:"; font.bold: true; color: Theme.text; Layout.minimumWidth: 100 }
                                        ComboBox {
                                            id: subtypeCombo
                                            objectName: "subtype_combo"
                                            Layout.fillWidth: true
                                            editable: true
                                            textRole: "text"
                                            valueRole: "value"
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Text { text: "Subtype:"; font.bold: true; color: Theme.text; Layout.minimumWidth: 100 }
                                        TextField {
                                            id: newTypeField
                                            objectName: "new_type"
                                            Layout.fillWidth: true
                                            visible: true
                                            color: Theme.text
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                        }
                                    }
                                    Button {
                                        text: "Save"
                                        font.bold: true
                                        Layout.fillWidth: true
                                        onClicked: root.saveNewType()
                                        background: Rectangle { color: Theme.primary; radius: 4 }
                                        contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                                    }
                                }
                            }

                            Rectangle {
                                color: Theme.background
                                radius: 6
                                border.color: Theme.border
                                Layout.fillWidth: true
                                Layout.leftMargin: 4
                                Layout.rightMargin: 4

                                ColumnLayout {
                                    x: 10; y: 10
                                    width: parent.width - 20
                                    spacing: 8

                                    Text { text: "Theme and Language"; font.bold: true; color: Theme.text }

                                    GridLayout {
                                        columns: 2
                                        columnSpacing: 10
                                        rowSpacing: 8
                                        Layout.fillWidth: true
                                        Text { text: "Theme:"; color: Theme.text }
                                        ComboBox {
                                            id: themeCombo
                                            objectName: "_theme_combo"
                                            Layout.fillWidth: true
                                            textRole: "text"
                                            valueRole: "value"
                                            onCurrentIndexChanged: root.themeChanged(currentIndex, currentValue)
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                        }
                                        Text { text: "Language:"; color: Theme.text }
                                        ComboBox {
                                            id: localeCombo
                                            objectName: "_locale_combo"
                                            Layout.fillWidth: true
                                            textRole: "text"
                                            valueRole: "value"
                                            onCurrentIndexChanged: root.localeChanged(currentIndex, currentValue)
                                            background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: 4 }
                                            contentItem: Text { text: parent.displayText; color: Theme.text; verticalAlignment: Text.AlignVCenter }
                                        }
                                    }
                                }
                            }

                            Item { height: 20 }
                        }
                    }
                }
            }

            Rectangle {
                id: footerFrame
                Layout.fillWidth: true
                Layout.minimumHeight: 36
                Layout.maximumHeight: 36
                color: Theme.surface
                border.color: Theme.border

                Text {
                    anchors.left: parent.left
                    anchors.leftMargin: 10
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Space Applications Center 2025 \u00a9"
                    font.pixelSize: 10
                    font.bold: true
                    color: Theme.text
                }
            }
        }
    }
}
