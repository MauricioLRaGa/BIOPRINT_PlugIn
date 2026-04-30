// BioprintingDialog.qml - Cura 5.7+ Version 3.0
// Autor: Mauricio Ramos Gallegos - Tesis PUCP Ingenieria Biomedica

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import UM 1.6 as UM

UM.Dialog {
    id: root
    title: "Bioimpresion - Configuracion de Biotinta"
    width: 560
    height: 680
    minimumWidth: 520
    minimumHeight: 640
    modality: Qt.NonModal

    property var    currentProfile:  ({})
    property string selectedBioink:  ""
    property string selectedSupport: "petri"
    property var    selectedWells:   ({})

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

    function toggleWell(index) {
        var updated = Object.assign({}, selectedWells)
        updated[index] = !updated[index]
        selectedWells = updated
    }

    function isWellSelected(index) {
        return selectedWells[index] === true
    }

    function getSelectedWellIndices() {
        var result = []
        for (var k in selectedWells) {
            if (selectedWells[k] === true) result.push(parseInt(k))
        }
        return result
    }

    Item {
        anchors.fill: parent

        Connections {
            target: manager
            function onStatusMessageChanged() { statusLabel.text = manager.statusMessage }
            function onWellAssignChanged()    { statusLabel.text = manager.statusMessage }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 14
            spacing: 10

            Rectangle {
                Layout.fillWidth: true
                height: 48
                radius: 6
                color: "#1A6B4A"
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 8
                    Text {
                        text: "Gestion de Biotintas"
                        color: "white"
                        font.pixelSize: 13
                        font.bold: true
                        verticalAlignment: Text.AlignVCenter
                    }
                    Text {
                        text: "Bioimpresoras de extrusion por jeringa"
                        color: "#B2DFCB"
                        font.pixelSize: 10
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }

            GroupBox {
                Layout.fillWidth: true
                title: "Biotinta"
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 6
                    ComboBox {
                        id: bioinkSelector
                        Layout.fillWidth: true
                        model: manager.bioinkNames
                        onCurrentTextChanged: {
                            if (currentText !== "") root.updateProfile(currentText)
                        }
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        height: descText.implicitHeight + 12
                        color: "#F0F7F4"
                        radius: 4
                        border.color: "#B2DFCB"
                        border.width: 1
                        Text {
                            id: descText
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.margins: 8
                            anchors.verticalCenter: parent.verticalCenter
                            text: currentProfile.description || "Selecciona una biotinta."
                            wrapMode: Text.WordWrap
                            color: "#2D6A4F"
                            font.pixelSize: 11
                        }
                    }
                }
            }

            GroupBox {
                Layout.fillWidth: true
                title: "Tipo de soporte"
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        Repeater {
                            model: [
                                { id: "petri", label: "Placa Petri" },
                                { id: "6",     label: "Multipocillos 6" },
                                { id: "24",    label: "Multipocillos 24" }
                            ]
                            Button {
                                Layout.fillWidth: true
                                text: modelData.label
                                background: Rectangle {
                                    color: selectedSupport === modelData.id ? "#E8F5EE" : "transparent"
                                    radius: 4
                                    border.color: selectedSupport === modelData.id ? "#1A6B4A" : "#AAAAAA"
                                    border.width: selectedSupport === modelData.id ? 2 : 1
                                }
                                contentItem: Text {
                                    text: parent.text
                                    font.pixelSize: 11
                                    font.bold: selectedSupport === modelData.id
                                    color: selectedSupport === modelData.id ? "#1A6B4A" : "#666666"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                onClicked: {
                                    selectedSupport = modelData.id
                                    selectedWells = {}
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 150
                        color: "#F8F8F8"
                        radius: 6
                        border.color: "#DDDDDD"
                        border.width: 1

                        Item {
                            anchors.centerIn: parent
                            width: 180
                            height: 120
                            visible: selectedSupport === "petri"
                            Rectangle {
                                anchors.centerIn: parent
                                width: 170
                                height: 108
                                radius: 85
                                color: "transparent"
                                border.color: "#1A6B4A"
                                border.width: 2
                                Rectangle {
                                    anchors.centerIn: parent
                                    width: 80
                                    height: 50
                                    radius: 40
                                    color: "#D4EDE2"
                                    border.color: "#1A6B4A"
                                    border.width: 1
                                    Text {
                                        anchors.centerIn: parent
                                        text: "zona de\nimpresion"
                                        color: "#1A6B4A"
                                        font.pixelSize: 8
                                        horizontalAlignment: Text.AlignHCenter
                                    }
                                }
                                Text {
                                    anchors.bottom: parent.bottom
                                    anchors.bottomMargin: 8
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    text: "90 mm"
                                    color: "#1A6B4A"
                                    font.pixelSize: 9
                                }
                            }
                        }

                        Item {
                            anchors.centerIn: parent
                            width: 210
                            height: 130
                            visible: selectedSupport === "6"
                            Rectangle {
                                anchors.centerIn: parent
                                width: 200
                                height: 120
                                radius: 8
                                color: "white"
                                border.color: "#BBBBBB"
                                border.width: 1
                                Grid {
                                    anchors.centerIn: parent
                                    columns: 3
                                    rows: 2
                                    spacing: 10
                                    Repeater {
                                        model: 6
                                        Rectangle {
                                            width: 50
                                            height: 40
                                            radius: 25
                                            color: root.isWellSelected(index) ? "#D4EDE2" : "#F0F0F0"
                                            border.color: root.isWellSelected(index) ? "#1A6B4A" : "#BBBBBB"
                                            border.width: root.isWellSelected(index) ? 2 : 1
                                            Column {
                                                anchors.centerIn: parent
                                                spacing: 1
                                                Text {
                                                    anchors.horizontalCenter: parent.horizontalCenter
                                                    text: (index + 1)
                                                    color: root.isWellSelected(index) ? "#1A6B4A" : "#999"
                                                    font.pixelSize: 10
                                                    font.bold: root.isWellSelected(index)
                                                }
                                                Text {
                                                    anchors.horizontalCenter: parent.horizontalCenter
                                                    property string mname: manager.getWellModelName(index)
                                                    text: mname.length > 6 ? mname.substring(0, 6) + ".." : mname
                                                    color: "#1A6B4A"
                                                    font.pixelSize: 7
                                                    visible: mname !== ""
                                                }
                                            }
                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: root.toggleWell(index)
                                                onDoubleClicked: manager.assignSTLToWell(index, selectedSupport)
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        Item {
                            anchors.centerIn: parent
                            width: 210
                            height: 130
                            visible: selectedSupport === "24"
                            Rectangle {
                                anchors.centerIn: parent
                                width: 200
                                height: 120
                                radius: 8
                                color: "white"
                                border.color: "#BBBBBB"
                                border.width: 1
                                Grid {
                                    anchors.centerIn: parent
                                    columns: 6
                                    rows: 4
                                    spacing: 4
                                    Repeater {
                                        model: 24
                                        Rectangle {
                                            width: 24
                                            height: 22
                                            radius: 12
                                            color: root.isWellSelected(index) ? "#D4EDE2" : "#F0F0F0"
                                            border.color: root.isWellSelected(index) ? "#1A6B4A" : "#BBBBBB"
                                            border.width: 1
                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: root.toggleWell(index)
                                                onDoubleClicked: manager.assignSTLToWell(index, selectedSupport)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Text {
                        Layout.fillWidth: true
                        text: selectedSupport === "petri"
                              ? "La zona central de la placa sera la region de impresion."
                              : "Clic: seleccionar pocillo   |   Doble clic: asignar STL individual"
                        font.pixelSize: 10
                        color: "#888888"
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        visible: selectedSupport !== "petri"
                        Button {
                            text: "Asignar mismo STL a todos"
                            Layout.fillWidth: true
                            font.pixelSize: 11
                            onClicked: manager.assignSTLToAllWells(selectedSupport)
                        }
                        Button {
                            text: "Limpiar seleccion"
                            Layout.fillWidth: true
                            font.pixelSize: 11
                            onClicked: {
                                selectedWells = {}
                                var i = 0
                                while (i < 24) {
                                    manager.clearWellAssignment(i)
                                    i = i + 1
                                }
                            }
                        }
                    }
                }
            }

            GroupBox {
                Layout.fillWidth: true
                title: "Parametros sugeridos"
                GridLayout {
                    anchors.fill: parent
                    columns: 4
                    rowSpacing: 6
                    columnSpacing: 10
                    Text {
                        text: "Capa (mm):"
                        color: "#666"
                        font.pixelSize: 11
                    }
                    Text {
                        text: currentProfile.layer_height !== undefined ? currentProfile.layer_height.toFixed(2) : "--"
                        font.bold: true
                        font.pixelSize: 11
                        color: "#1A6B4A"
                    }
                    Text {
                        text: "Velocidad (mm/s):"
                        color: "#666"
                        font.pixelSize: 11
                    }
                    Text {
                        text: currentProfile.speed_print !== undefined ? currentProfile.speed_print : "--"
                        font.bold: true
                        font.pixelSize: 11
                        color: "#1A6B4A"
                    }
                    Text {
                        text: "Temperatura (C):"
                        color: "#666"
                        font.pixelSize: 11
                    }
                    Text {
                        text: currentProfile.material_print_temperature !== undefined ? currentProfile.material_print_temperature : "--"
                        font.bold: true
                        font.pixelSize: 11
                        color: "#1A6B4A"
                    }
                    Text {
                        text: "Retraccion:"
                        color: "#666"
                        font.pixelSize: 11
                    }
                    Text {
                        text: currentProfile.retraction_enable !== undefined
                              ? (currentProfile.retraction_enable ? "Habilitada" : "Deshabilitada")
                              : "--"
                        font.bold: true
                        font.pixelSize: 11
                        color: currentProfile.retraction_enable ? "#1A6B4A" : "#C0392B"
                    }
                }
            }

            Item {
                Layout.fillHeight: true
            }

            Text {
                id: statusLabel
                Layout.fillWidth: true
                text: manager.statusMessage
                color: "#1A6B4A"
                font.pixelSize: 11
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                visible: text !== ""
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

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
                        text: applyBtn.text
                        color: "white"
                        font.bold: true
                        font.pixelSize: 12
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
                    id: gcodeBtn
                    text: "Generar G-code"
                    Layout.fillWidth: true
                    visible: selectedSupport !== "petri"
                    enabled: selectedBioink !== "" && getSelectedWellIndices().length > 0
                    background: Rectangle {
                        color: gcodeBtn.pressed ? "#1A3A6B" : gcodeBtn.hovered ? "#1E4A8A" : "#1E3A6B"
                        radius: 4
                    }
                    contentItem: Text {
                        text: gcodeBtn.text
                        color: "white"
                        font.bold: true
                        font.pixelSize: 12
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: manager.generateGCode(
                        selectedBioink,
                        selectedSupport,
                        root.getSelectedWellIndices()
                    )
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
                text: "Parametros aplicados correctamente a Cura."
                color: "#1A6B4A"
                font.pixelSize: 11
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                Timer {
                    id: hideTimer
                    interval: 3000
                    onTriggered: confirmMsg.visible = false
                }
            }
        }
    }
}
