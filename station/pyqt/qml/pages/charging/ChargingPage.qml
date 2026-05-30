import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.3

import "../../shared"


Rectangle {
    width: parent.width
    height: parent.height
    color: "#00124C"

    property string prefixNumber: stateManager.prefixNumber
    property string leftTime: stateManager.leftTime
    property string currentAm: stateManager.currentAm
    property string totalKwh: stateManager.totalKwh
    property string currentKwh: stateManager.currentKwh


        GridLayout {
            id: grid
            rows: 2
            columns: 3
            width: parent.width
            height: parent.height


            CustomValueBox {
                Layout.columnSpan: 1
                Layout.rowSpan: 1
                title: "Осталось времени:"
                value: leftTime
            }

            AnimatedImage {
                id: animation
                Layout.columnSpan: 1
                Layout.rowSpan: 2
                source: "./gif/"+prefixNumber+".gif"
            }

            CustomValueBox {
                Layout.columnSpan: 1
                Layout.rowSpan: 1
                title: "Ток, А:"
                value: currentAm
            }

            CustomValueBox {
                Layout.columnSpan: 1
                Layout.rowSpan: 1
                title: "Использовано, кВт:"
                value: totalKwh
            }

            CustomValueBox {
                Layout.columnSpan: 1
                Layout.rowSpan: 1
                title: "Мощность, кВт/ч:"
                value: currentKwh
            }
        }
    }
