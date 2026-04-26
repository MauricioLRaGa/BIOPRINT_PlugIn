import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import UM 1.6 as UM

UM.Dialog {
    id: root

    title:         "Bioimpresion — Configuracion de Biotinta"
    width:         520
    height:        500
    minimumWidth:  480
    minimumHeight: 460
    modality:      Qt.NonModal

    property var    currentProfile: ({})
    property string selectedBioink: ""

    onVisibleChanged: {
        if (visible && bioinkSelector.count > 0) {
            bioinkSelector.currentIndex = 0
            root.updateProfile(bioinkSelector.currentText)
        }
    }

    function updateProfile(name) {
        selectedBioink = name
        currentProfile = manager.getBioinkProfile(name)
    }

    ColumnLayout {
        anchors.fill:    parent
        anchors.margins: 16
        spacing:         12

        // Encabezado
        Rectangle {
            Layout.fillWidth: true
            height: 52
            radius: 6
            color:  "#1A6B4A"

            RowLayout {
                anchors { fill: parent; margins: 12 }
                spacing: 10
                Text {
                    text: "Gestion de Biotintas"
                    color: "white"
                    font { pixelSize: 15; bold: true }
                    verticalAlignment: Text.AlignVCenter
                }
                Text {
                    text:  "Bioimpresoras de extrusion por jeringa"
                    color: "#B2DFCB"
                    font.pixelSize: 11
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }

        // Selector
        GroupBox {
            Layout.fillWidth: true
            title: "Seleccionar biotinta"

            ColumnLayout {
                anchors.fill: parent
                spacing: 8

                ComboBox {
                    id:               bioinkSelector
                    Layout.fillWidth: true
                    model:            manager.bioinkNames
                    onCurrentTextChanged: {
                        if (currentText !== "") root.updateProfile(currentText)
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height:  descText.implicitHeight + 16
                    color:   "#F0F7F4"
                    radius:  4
                    border { color: "#B2DFCB"; width: 1 }
                    Text {
                        id: descText
                        anchors { left: parent.left; right: parent.right; margins: 8; verticalCenter: parent.verticalCenter }
                        text:     currentProfile.description || "Selecciona una biotinta."
                        wrapMode: Text.WordWrap
                        color:    "#2D6A4F"
                        font.pixelSize: 11
                    }
                }
            }
        }

        // Parámetros
        GroupBox {
            Layout.fillWidth: true
            title: "Parametros sugeridos"

            GridLayout {
                anchors.fill:  parent
                columns:       2
                rowSpacing:    8
                columnSpacing: 16

                Text { text: "Altura de capa (mm):" }
                Text { text: currentProfile.layer_height !== undefined ? currentProfile.layer_height.toFixed(2) : "--"; font.bold: true; color: "#1A6B4A" }

                Text { text: "Velocidad (mm/s):" }
                Text { text: currentProfile.speed_print !== undefined ? currentProfile.speed_print : "--"; font.bold: true; color: "#1A6B4A" }

                Text { text: "Temperatura (C):" }
                Text { text: currentProfile.material_print_temperature !== undefined ? currentProfile.material_print_temperature : "--"; font.bold: true; color: "#1A6B4A" }

                Text { text: "Relleno (%):" }
                Text { text: currentProfile.infill_sparse_density !== undefined ? currentProfile.infill_sparse_density : "--"; font.bold: true; color: "#1A6B4A" }

                Text { text: "Retraccion:" }
                Text {
                    text:  currentProfile.retraction_enable !== undefined ? (currentProfile.retraction_enable ? "Habilitada" : "Deshabilitada") : "--"
                    font.bold: true
                    color: currentProfile.retraction_enable ? "#1A6B4A" : "#C0392B"
                }
            }
        }

        Item { Layout.fillHeight: true }

        // Botones
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                id: applyBtn
                text: "Aplicar a Cura"
                Layout.fillWidth: true
                enabled: selectedBioink !== ""
                background: Rectangle {
                    color: applyBtn.pressed ? "#145A38" : applyBtn.hovered ? "#1E8449" : "#1A6B4A"
                    radius: 4
                }
                contentItem: Text {
                    text: applyBtn.text; color: "white"; font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                onClicked: {
                    manager.applyBioinkProfile(selectedBioink)
                    confirmMsg.visible = true
                    hideTimer.restart()
                }
            }

            Button {
                text: "Cerrar"
                Layout.fillWidth: true
                onClicked: root.hide()
            }
        }

        Text {
            id: confirmMsg
            visible: false
            Layout.fillWidth: true
            text:  "Parametros aplicados correctamente."
            color: "#1A6B4A"
            font { pixelSize: 12; bold: true }
            horizontalAlignment: Text.AlignHCenter
            Timer { id: hideTimer; interval: 3000; onTriggered: confirmMsg.visible = false }
        }
    }
}
