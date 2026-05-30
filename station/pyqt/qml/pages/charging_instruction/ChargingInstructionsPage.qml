import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3


Rectangle {
    width: parent.width
    height: parent.height
    property string chargingStation: stateManager.chargingStation
    visible: chargingStation !== ""
    
    Image {
        source: "./img/conn-"+chargingStation+".jpg"
        fillMode: Image.PreserveAspectFit
        anchors.fill: parent
    }
}