import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

ComboBox {
    id: control
    editable: true

    property bool isValid: currentIndex >= 0 || currentText !== ""
    property string valueRole: "value"
    property string displayRole: "text"

    function selectByValue(val) {
        for (var i = 0; i < count; i++) {
            var item = model[i]
            var itemVal = typeof item === "object" ? item[valueRole] : item
            if (String(itemVal) === String(val)) {
                currentIndex = i
                return true
            }
        }
        return false
    }

    function currentValue() {
        if (currentIndex < 0 || currentIndex >= count) return currentText
        var item = model[currentIndex]
        return typeof item === "object" ? item[valueRole] : currentText
    }

    contentItem: Text {
        leftPadding: 8
        rightPadding: 8
        topPadding: 6
        bottomPadding: 6
        text: control.displayText
        font: control.font
        color: control.enabled ? Theme.activeText() : Theme.activeTextSec()
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        implicitHeight: 34
        color: control.editable ? Theme.activeSurface() : Theme.activeOverlay()
        border.color: control.activeFocus ? Theme.activeAccent() : Theme.activeBorder()
        border.width: control.activeFocus ? 2 : 1
        radius: Theme.radiusMd
    }

    popup: Popup {
        y: control.height + 2
        width: control.width
        implicitHeight: Math.min(contentItem.implicitHeight, 300)
        padding: 1

        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: control.delegateModel
            currentIndex: control.highlightedIndex
            ScrollIndicator.vertical: ScrollIndicator { }
        }

        background: Rectangle {
            color: Theme.activeSurface()
            border.color: Theme.activeBorder()
            border.width: 1
            radius: Theme.radiusMd
        }
    }

    delegate: ItemDelegate {
        width: ListView.view.width
        contentItem: Text {
            text: {
                var m = modelData !== undefined ? modelData : model
                return typeof m === "object" ? m[control.displayRole] : String(m)
            }
            color: Theme.activeText()
            font: control.font
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
            leftPadding: 8
            rightPadding: 8
        }
        background: Rectangle {
            color: index === ListView.view.currentIndex ? Theme.activeSelection() : "transparent"
        }
        highlighted: ListView.isCurrentItem
    }
}
