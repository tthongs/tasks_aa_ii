import QtQuick
import QtQuick.DBus

Item {
    Component.onCompleted: {
        console.log("QtQuick.DBus is available!");
        Qt.quit();
    }
}
