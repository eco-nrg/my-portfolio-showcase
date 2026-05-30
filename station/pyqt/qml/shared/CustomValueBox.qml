import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3


Rectangle {
    property string title: ""
    property variant value: ""
    property variant bgColor: "#E73A00"
    property variant textColor: "#fff"
    
    width: 355
    height: 300
    color: bgColor
    
    Layout.fillWidth: true
    Layout.fillHeight: true
    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
    Layout.leftMargin: 15
    Layout.rightMargin: 15
    Layout.topMargin: 15
    Layout.bottomMargin: 15

    Text {
        anchors.centerIn: parent
        text: title + "\n" + value
        color: textColor
        font.pixelSize: 35
        font.family: webFontLight.name
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
