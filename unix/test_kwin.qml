import QtQuick
import org.kde.kwin as KWin

Item {
    Component.onCompleted: {
        console.log("KWin Workspace desktops: " + KWin.Workspace.desktops.length);
        Qt.quit();
    }
}
