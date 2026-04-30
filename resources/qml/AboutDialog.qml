// AboutDialog.qml — Cura 5.7+
// Autor: Mauricio Ramos Gallegos — Tesis PUCP Ingenieria Biomedica

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import UM 1.6 as UM

UM.Dialog {
    id: aboutDialog
    title: "Acerca de — Bioprinting Plugin"
    width: 400
    height: 300
    minimumWidth: 380
    modality: Qt.NonModal

    Item {
        anchors.fill: parent

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 12

            Text {
                text: "Bioprinting Plugin"
                font.pixelSize: 20
                font.bold: true
                color: "#1A6B4A"
                Layout.alignment: Qt.AlignHCenter
            }

            Text {
                text: "Version 1.0.0  Cura 5.7+"
                font.pixelSize: 12
                color: "#666"
                Layout.alignment: Qt.AlignHCenter
            }

            Rectangle {
                height: 1
                Layout.fillWidth: true
                color: "#DDD"
            }

            Text {
                text: "Complemento de laminado con gestion de biotintas para bioimpresoras de extrusion por jeringa.\n\nDesarrollado como parte de la tesis de grado en Ingenieria Biomedica — PUCP, Lima, Peru."
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                font.pixelSize: 12
                color: "#333"
            }

            Text {
                text: "Autor: Mauricio Ramos Gallegos\nAsesora: Ana Cristina Midori Sanchez Sifuentes"
                font.pixelSize: 11
                color: "#555"
                Layout.alignment: Qt.AlignHCenter
            }

            Item {
                Layout.fillHeight: true
            }

            Button {
                text: "Cerrar"
                Layout.alignment: Qt.AlignHCenter
                onClicked: aboutDialog.hide()
            }
        }
    }
}
