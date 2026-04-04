import QtQuick
import org.kde.plasma.plasma5support as Plasma5Support

Item {
    Plasma5Support.DataSource {
        id: ds
        engine: "kwin"
        onNewData: (source, data) => {
            console.log("Source: " + source);
            console.log("Data: " + JSON.stringify(data));
            Qt.quit();
        }
        Component.onCompleted: {
            console.log("KWin Sources: " + sources);
            if (sources.length === 0) {
                console.log("No sources found!");
                Qt.quit();
            }
        }
    }
}
