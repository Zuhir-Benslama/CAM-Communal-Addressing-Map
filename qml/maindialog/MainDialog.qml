import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import maindialog 1.0
import Theme 1.0

Item {
    id: root

    property string currentPage: "login"

    signal switchToPage(string pageName)
    signal comboChanged(string objectName, int index, string currentData)
    signal submitForm(string pageName)
    signal selectRef(string objectName, string layerName)

    function switchPage(pageName) {
        currentPage = pageName
    }

    function setSettingsTabIndex(index) {
        mainPage.setSettingsTabIndex(index)
    }

    function setFormStackIndex(index) {
        mainPage.setFormStackIndex(index)
    }

    function setFieldText(objectName, text) {
        var obj = findField(objectName)
        if (obj) obj.text = text
    }

    function setComboIndex(objectName, index) {
        var obj = findField(objectName)
        if (obj && obj.currentIndex !== undefined)
            obj.currentIndex = index
    }

    function _ensureModel(obj) {
        if (obj.model !== undefined && obj.model !== null) return obj.model
        var lm = Qt.createQmlObject("import QtQuick 2.15; ListModel {}", obj)
        obj.model = lm
        return lm
    }

    function setComboOptions(objectName, options) {
        var obj = findField(objectName)
        if (!obj) { console.warn("setComboOptions: field not found:", objectName); return }
        console.warn("setComboOptions:", objectName, "type:", obj.toString(), "model:", obj.model, "options.length:", options.length)
        var model = _ensureModel(obj)
        model.clear()
        for (var i = 0; i < options.length; i++) {
            model.append({ text: options[i].text, value: options[i].value })
        }
        if (obj.currentIndex < 0 && model.count > 0) {
            obj.currentIndex = 0
        }
        console.warn("setComboOptions DONE:", objectName, "model.count:", model.count, "combo.currentIndex:", obj.currentIndex)
    }

    function clearCombo(objectName) {
        var obj = findField(objectName)
        if (!obj) return
        var model = _ensureModel(obj)
        model.clear()
    }

    function addComboItem(objectName, text, value) {
        var obj = findField(objectName)
        if (!obj) return
        var model = _ensureModel(obj)
        model.append({ text: text, value: value })
    }

    function setLabelText(objectName, text) {
        var obj = findField(objectName)
        if (obj) obj.text = text
    }

    function getFieldText(objectName) {
        var obj = findField(objectName)
        return obj ? obj.text : ""
    }

    function getComboIndex(objectName) {
        var obj = findField(objectName)
        return obj && obj.currentIndex !== undefined ? obj.currentIndex : -1
    }

    function getComboData(objectName, index) {
        var obj = findField(objectName)
        if (!obj || index < 0) return ""
        var model = obj.model
        if (!model || !model.get) return ""
        var item = model.get(index)
        return item ? item.value : ""
    }

    function getComboText(objectName, index) {
        var obj = findField(objectName)
        if (!obj || index < 0) return ""
        var model = obj.model
        if (!model || !model.get) return ""
        var item = model.get(index)
        return item ? item.text : ""
    }

    function getComboCount(objectName) {
        var obj = findField(objectName)
        if (!obj) return 0
        var model = obj.model
        return model && model.count !== undefined ? model.count : 0
    }

    function setComboItemText(objectName, index, text) {
        var obj = findField(objectName)
        if (!obj || index < 0) return
        var model = obj.model
        if (model && model.setProperty)
            model.setProperty(index, "text", text)
    }

    function findComboByData(objectName, value) {
        var obj = findField(objectName)
        if (!obj) return -1
        var model = obj.model
        if (!model || !model.count) return -1
        for (var i = 0; i < model.count; i++) {
            var item = model.get(i)
            if (String(item.value) === String(value)) return i
        }
        return -1
    }

    function findField(objectName) {
        return findItem(root, objectName)
    }

    function findItem(parent, name) {
        if (parent.objectName === name) {
            console.warn("findItem FOUND:", name, "type:", parent.toString())
            return parent
        }
        if (parent.children) {
            for (var i = 0; i < parent.children.length; i++) {
                var result = findItem(parent.children[i], name)
                if (result) return result
            }
        }
        return null
    }

    StackLayout {
        anchors.fill: parent
        currentIndex: {
            if (currentPage === "login") return 0
            if (currentPage === "add_usr") return 1
            if (currentPage === "main") return 2
            return 0
        }

        LoginPage {
            id: loginPage
            onSignInClicked: root.submitForm("login")
            onAddUserClicked: root.switchToPage("add_usr")
            onRestoreDbClicked: root.submitForm("restore_db")
            onComboChanged: function(name, index, data) {
                root.comboChanged(name, index, data)
            }
        }

        AddUserPage {
            id: addUserPage
            onSaveClicked: root.submitForm("add_usr")
            onCancelClicked: root.switchToPage("login")
            onWilayaChanged: function(index, data) {
                root.comboChanged("wilaya_list", index, data)
            }
        }

        MainPage {
            id: mainPage
            onFormSubmitted: function(pageName) { root.submitForm(pageName) }
            onComboChanged: function(name, index, data) { root.comboChanged(name, index, data) }
            onSelectRef: function(objName, layerName) { root.selectRef(objName, layerName) }
            onListRequested: function(type) { root.submitForm("list_" + type) }
            onFeatureChanged: function(index, data) { root.comboChanged("feature_combo", index, data) }
            onSaveNewType: root.submitForm("save_new_type")
            onActionChanged: function(index, data) { root.comboChanged("_action_combo", index, data) }
            onSaveAction: root.submitForm("save_action")
            onGearClicked: root.submitForm("toggle_settings")
            onTabChanged: function(index) { root.comboChanged("menu", index, "") }
            onDrawClicked: root.submitForm("draw")
            onSelectClicked: root.submitForm("select")
            onEditClicked: root.submitForm("edit")
            onMeasureClicked: root.submitForm("measure")
            onThemeChanged: function(index, data) { root.comboChanged("_theme_combo", index, data) }
            onLocaleChanged: function(index, data) { root.comboChanged("_locale_combo", index, data) }
        }
    }
}
