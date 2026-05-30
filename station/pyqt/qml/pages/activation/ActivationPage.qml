import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3
import Qt.labs.qmlmodels 1.0


Rectangle {
    width: parent.width
    height: parent.height
    property string chargingStation: stateManager.chargingStation
    property string nameConnector: stateManager.nameConnector
    property string price_kwh: stateManager.price_kwh
    property string price_idle: stateManager.price_idle

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
                source: "./img/qrcode_activate.png"
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
                text: "Этот терминал\nсвободен, \nчтобы начать\nзарядку\nсканируйте\nQR-код\nи следуйте\nинструкциям."
                color: "#fff"
                width: 140
                lineHeight: 0.7
                font.family: "Helvetica"
                font.bold: true
                font.pixelSize: 23
                Layout.alignment: Qt.AlignHCenter
                bottomPadding: 30
            }

            TableView {
                Layout.alignment: Qt.AlignHCenter
                width: 150
                height: 80

                model: TableModel {
                    TableModelColumn { display: "type" }
                    TableModelColumn { display: "price" }

                    rows: [
                    {
                        type: "<span style='color: #fff'>стоимость<br>зарядки</span>",
                        price: price_kwh + " Р/кВт/ч"
                    },
                    {
                        type: "<span style='color: #fff'>стоимость<br>простоя</span><span style='color: #E52A12'>*</span>",
                        price: price_idle + " Р/час"
                    },
                    ]
                }

                delegate: DelegateChooser {
                    DelegateChoice {
                        column: 0
                        delegate: Rectangle {
                            implicitWidth: 60
                            implicitHeight: 30
                            color: "transparent"
                            border.color: "white"
                            Text {
                                anchors.centerIn: parent
                                text: model.display
                                font.pixelSize: 10
                                textFormat: Text.RichText
                            }
                        }
                    }
                    DelegateChoice {
                        column: 1
                        delegate: Rectangle {
                            implicitWidth: 80
                            implicitHeight: 30
                            color: "transparent"
                            border.color: "white"
                            Text {
                                anchors.centerIn: parent
                                text: model.display
                                color: "white"
                                font.pixelSize: 9
                                font.bold: true
                            }
                        }
                    }
                }
            }

            Image {
                Layout.preferredWidth: 145
                Layout.preferredHeight: 145
                source: "./img/conn-" + chargingStation + ".svg"
                fillMode: Image.PreserveAspectFit
                Layout.alignment: Qt.AlignHCenter
            }

            Text {
                text: nameConnector
                color: "#fff"
                font.family: "Helvetica"
                font.pointSize: 16
                Layout.alignment: Qt.AlignHCenter
                font.bold: true
            }

            Text {
                text: "<span style='color: #E52A12'>*</span> <span style='color: #fff'>Внимание!!! Если ток заряда падает<br>"
                + "ниже 15А (3, 5кВт/ч) кроме стоимости<br>"
                + "электро энергии начисляется оплата<br>за простой</span>"
                font.family: "Helvetica"
                font.pointSize: 7.5
                Layout.alignment: Qt.AlignHCenter
                topPadding: 5
                textFormat: Text.RichText
            }

        }
    }


