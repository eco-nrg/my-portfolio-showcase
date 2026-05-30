import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: root
    visible: true
    visibility: "FullScreen"
    width: 800
    height: 600
    flags: Qt.FramelessWindowHint

    property string currentState: stateManager.currentState
    property string pathToPage: "qml/pages/"

    FontLoader { id: webFontBold
     source: "fonts/MyriadPro-Bold.ttf" }
    FontLoader { id: webFontLight 
    source: "fonts/MyriadPro-Light.otf" }
    FontLoader { id: webFontRegular
     source: "fonts/MyriadPro-Regular.otf" }

    Rectangle {
        width: parent.width
        height: parent.height
        visible: currentState !== ""

        Loader {
            id: contentLoader
            width: parent.width
            height: parent.height
        }

        states: [
            State {
                name: "qr-code"
                PropertyChanges { target: contentLoader; source: pathToPage+"activation/ActivationPage.qml" }
            },
            State {
                name: "booked"
                PropertyChanges { target: contentLoader; source: pathToPage+"booked/BookedPage.qml" }
            },
            State {
                name: "system-start"
                PropertyChanges { target: contentLoader; source: pathToPage+"welcome/WelcomePage.qml" }
            },
            State {
                name: "charging_start"
                PropertyChanges { target: contentLoader; source: pathToPage+"charging/ChargingPage.qml" }
            },
            State {
                name: "warning"
                PropertyChanges { target: contentLoader; source: pathToPage+"no_service/NoServicePage.qml" }
            },
            State {
                name: "charging"
                PropertyChanges { target: contentLoader; source: pathToPage+"charging_instruction/ChargingInstructionsPage.qml" }
            },
            State {
                name: "charging_down"
                PropertyChanges { target: contentLoader; source: pathToPage+"charging_down/ChargingDownPage.qml" }
            },
            State {
                name: "charging_end"
                PropertyChanges { target: contentLoader; source: pathToPage+"charging_end/ChargingEndPage.qml" }
            }
        ]

        state: currentState
    }
}
