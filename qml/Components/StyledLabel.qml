import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Theme 1.0

Label {
    property bool isHeading: false
    property bool isCaption: false

    color: Theme.activeText()
    font.pixelSize: isHeading ? Theme.fontHeadline : (isCaption ? Theme.fontCaption2 : Theme.fontBody)
    linkColor: Theme.activeAccent()
}
