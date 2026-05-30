import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3


Rectangle {
    width: parent.width
    height: parent.height
    property string bookedRemainingTime: stateManager.bookedRemainingTime

    Image {
        source: "./img/background.jpg"
        fillMode: Image.PreserveAspectFit
        anchors.fill: parent
    }

    Column {
        anchors.left: parent.left
        spacing: 0

        Image {
            width: 600
            height: 600
            source: "./img/qrcode_booked.png"
            fillMode: Image.PreserveAspectFit
            anchors.horizontalCenter: parent.horizontalCenter
        }

    }

    ColumnLayout {
        x: 600
        spacing: 0
        width: 200

        Text {
            text: "Внимание!"
            color: "#fff"
            font.family: "Helvetica"
            font.pointSize: 22
            font.capitalization: Font.AllUppercase
            Layout.alignment: Qt.AlignHCenter
            font.bold: true
            bottomPadding: 10
        }

        Text {
            text: "Этот терминал\nв данное время \nзабронирован\nдругим\nпользователем,\nсейчас только\nон может его\nактивировать!"
            color: "#fff"
            width: 140
            lineHeight: 0.7
            font.family: "Helvetica"
            font.bold: true
            font.pixelSize: 23
            Layout.alignment: Qt.AlignHCenter
            bottomPadding: 30
        }


        Text {
            text: "Если терминал\nбронировали\nВы, сканируйте\nQR-код чтобы\nначать зарядку,\nв противном\nслучае бронь\nснимется через:"
            color: "#fff"
            width: 140
            lineHeight: 0.7
            font.family: "Helvetica"
            font.bold: true
            font.pixelSize: 23
            Layout.alignment: Qt.AlignHCenter
            bottomPadding: 30
        }

        

        Text {
            text: bookedRemainingTime
            color: "#0F1"
            font.family: "Helvetica"
            font.pointSize: 35
            Layout.alignment: Qt.AlignHCenter
            font.bold: true
        }

    }
}