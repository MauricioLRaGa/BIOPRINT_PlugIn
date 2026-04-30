import os

from UM.Extension import Extension
from UM.Logger import Logger

try:
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QUrl
    from PyQt6.QtWidgets import QFileDialog
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QUrl
    from PyQt5.QtWidgets import QFileDialog

# Coordenadas reales de pocillos en mm
WELL_COORDS = {
    "petri": [{"id": 0, "cx": 45.0, "cy": 45.0}],
    "6": [
        {"id": 0, "cx": 24.5,  "cy": 21.5},
        {"id": 1, "cx": 63.5,  "cy": 21.5},
        {"id": 2, "cx": 102.5, "cy": 21.5},
        {"id": 3, "cx": 24.5,  "cy": 60.5},
        {"id": 4, "cx": 63.5,  "cy": 60.5},
        {"id": 5, "cx": 102.5, "cy": 60.5},
    ],
    "24": [
        {"id": i, "cx": 14.38 + (i % 6) * 19.3, "cy": 10.5 + (i // 6) * 19.3}
        for i in range(24)
    ],
}


class BioprintingPlugin(QObject, Extension):
    """
    Plugin de bioimpresion para Ultimaker Cura 5.7+
    Gestion de biotintas + visualizacion 3D en escena de Cura.

    Tesis Ingenieria Biomedica — PUCP
    Autor: Mauricio Ramos Gallegos
    """

    wellAssignChanged    = pyqtSignal()
    statusMessageChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMenuName("Bioimpresion")
        self.addMenuItem("Configurar Biotinta", self.showMainDialog)
        self.addMenuItem("Limpiar escena",      self.clearScene)
        self.addMenuItem("Acerca del plugin",   self.showAboutDialog)

        self._main_dialog  = None
        self._about_dialog = None
        self._well_assignments = {}  # { well_index: {"stl_path": str, "name": str} }
        self._status_message   = ""

        self._perfiles = {
            "Alginato de Sodio": {
                "name": "Alginato de Sodio",
                "layer_height": 0.2,
                "speed_print": 10,
                "material_print_temperature": 25,
                "retraction_enable": False,
                "infill_sparse_density": 30,
                "description": "Hidrogel natural de algas. Alta biocompatibilidad. Crosslinking con CaCl2."
            },
            "Colageno": {
                "name": "Colageno",
                "layer_height": 0.15,
                "speed_print": 8,
                "material_print_temperature": 20,
                "retraction_enable": False,
                "infill_sparse_density": 40,
                "description": "Proteina estructural ECM. Excelente adhesion celular."
            },
            "Gelatina": {
                "name": "Gelatina",
                "layer_height": 0.2,
                "speed_print": 12,
                "material_print_temperature": 22,
                "retraction_enable": False,
                "infill_sparse_density": 35,
                "description": "Derivado del colageno. Buena imprimibilidad."
            },
            "GelMA": {
                "name": "GelMA",
                "layer_height": 0.15,
                "speed_print": 9,
                "material_print_temperature": 22,
                "retraction_enable": False,
                "infill_sparse_density": 40,
                "description": "Gelatina modificada. Alta estabilidad post-UV."
            },
            "Pluronic F-127": {
                "name": "Pluronic F-127",
                "layer_height": 0.3,
                "speed_print": 15,
                "material_print_temperature": 20,
                "retraction_enable": False,
                "infill_sparse_density": 25,
                "description": "Polimero sintetico. Excelente imprimibilidad."
            },
        }

        Logger.log("i", "[BioprintingPlugin] Plugin cargado.")

    # ── Ventanas ───────────────────────────────────────────────────────

    def showMainDialog(self):
        if self._main_dialog is None:
            self._main_dialog = self._loadQml("BioprintingDialog.qml")
        if self._main_dialog:
            self._main_dialog.show()

    def showAboutDialog(self):
        if self._about_dialog is None:
            self._about_dialog = self._loadQml("AboutDialog.qml")
        if self._about_dialog:
            self._about_dialog.show()

    def _loadQml(self, filename):
        from UM.Application import Application
        ruta = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "resources", "qml", filename
        )
        if not os.path.exists(ruta):
            Logger.log("e", f"[BioprintingPlugin] No existe: {ruta}")
            return None
        return Application.getInstance().createQmlComponent(ruta, {"manager": self})

    # ── Propiedades QML ────────────────────────────────────────────────

    @pyqtProperty("QStringList", constant=True)
    def bioinkNames(self):
        return list(self._perfiles.keys())

    @pyqtSlot(str, result="QVariantMap")
    def getBioinkProfile(self, name):
        return self._perfiles.get(name, {})

    @pyqtProperty(str, notify=statusMessageChanged)
    def statusMessage(self):
        return self._status_message

    def _setStatus(self, msg):
        self._status_message = msg
        self.statusMessageChanged.emit()
        Logger.log("i", f"[BioprintingPlugin] {msg}")

    # ── Aplicar perfil a Cura ──────────────────────────────────────────

    @pyqtSlot(str)
    def applyBioinkProfile(self, name):
        from UM.Application import Application
        perfil = self._perfiles.get(name)
        if not perfil:
            return
        stack = Application.getInstance().getGlobalContainerStack()
        if not stack:
            return
        for key in ["layer_height", "speed_print", "material_print_temperature",
                    "retraction_enable", "infill_sparse_density"]:
            try:
                stack.setProperty(key, "value", perfil[key])
            except Exception as e:
                Logger.log("w", f"[BioprintingPlugin] {key}: {e}")
        Logger.log("i", f"[BioprintingPlugin] Perfil '{name}' aplicado.")

    # ── Gestión de pocillos ────────────────────────────────────────────

    @pyqtSlot(int, result=str)
    def getWellModelName(self, well_index):
        a = self._well_assignments.get(well_index)
        return a.get("name", "") if a else ""

    @pyqtSlot(int, str)
    def assignSTLToWell(self, well_index, support_type):
        """
        Abre explorador, asigna STL al pocillo y lo carga
        en la escena 3D de Cura posicionado en las coordenadas reales.
        """
        dialog = QFileDialog()
        dialog.setWindowTitle(f"Seleccionar STL para pocillo {well_index + 1}")
        dialog.setNameFilter("Archivos STL (*.stl)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        if not dialog.exec():
            return

        files = dialog.selectedFiles()
        if not files:
            return

        stl_path = files[0]
        name     = os.path.splitext(os.path.basename(stl_path))[0]

        self._well_assignments[well_index] = {
            "stl_path": stl_path,
            "name":     name
        }
        self.wellAssignChanged.emit()

        # Cargar en la escena 3D de Cura
        self._loadSTLInScene(stl_path, well_index, support_type)
        self._setStatus(f"Pocillo {well_index + 1}: {name} cargado en escena.")

    def _loadSTLInScene(self, stl_path, well_index, support_type):
        """
        Carga el STL en la escena de Cura y lo posiciona
        en las coordenadas reales del pocillo seleccionado.
        """
        from UM.Application import Application
        from UM.Math.Vector import Vector

        try:
            app = Application.getInstance()

            # Obtener coordenadas del pocillo
            wells  = WELL_COORDS.get(support_type, WELL_COORDS["6"])
            well   = next((w for w in wells if w["id"] == well_index), None)
            if not well:
                Logger.log("w", f"[BioprintingPlugin] Pocillo {well_index} no encontrado.")
                return

            cx = well["cx"]
            cy = well["cy"]

            # Cargar el STL en la escena de Cura
            app.readLocalFile(QUrl.fromLocalFile(stl_path))
            Logger.log("i", f"[BioprintingPlugin] STL cargado: {stl_path}")

            # Esperar un momento y luego posicionar el nodo
            # Usamos un timer para dar tiempo a que Cura procese el archivo
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, lambda: self._positionNode(cx, cy, stl_path))

        except Exception as e:
            Logger.log("e", f"[BioprintingPlugin] Error cargando STL: {e}")
            self._setStatus(f"Error cargando STL: {e}")

    def _loadAndPosition(self, stl_path, cx, cy):
        """Carga un STL en Cura y lo posiciona en (cx, cy)."""
        try:
            from UM.Application import Application
            app = Application.getInstance()
            app.readLocalFile(QUrl.fromLocalFile(stl_path))
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, lambda: self._positionNode(cx, cy, stl_path))
        except Exception as e:
            Logger.log("e", f"[BioprintingPlugin] Error en _loadAndPosition: {e}")

    def _positionNode(self, cx, cy, stl_path):
        """
        Posiciona el nodo en las coordenadas reales del pocillo.

        Cura usa el centro de la cama como origen (0,0).
        Los pocillos usan la esquina inferior izquierda como origen.
        Offset: restar la mitad de las dimensiones de la cama.
        
        Cama custom por defecto: 220mm x 220mm
        Offset X = cx - 110
        Offset Y = cy - 110
        """
        try:
            from UM.Application import Application
            from UM.Math.Vector import Vector
            from UM.Operations.TranslateOperation import TranslateOperation

            app   = Application.getInstance()
            scene = app.getController().getScene()
            root  = scene.getRoot()

            # Obtener dimensiones reales de la cama desde Cura
            stack = app.getGlobalContainerStack()
            if stack:
                bed_width = stack.getProperty("machine_width", "value") or 220
                bed_depth = stack.getProperty("machine_depth", "value") or 220
            else:
                bed_width = 220
                bed_depth = 220

            # Convertir coordenadas de pocillo a coordenadas de Cura
            # Sistema de coordenadas Cura:
            #   X: -bed_width/2 (izquierda) a +bed_width/2 (derecha)
            #   Z: -bed_depth/2 (frente)    a +bed_depth/2 (fondo)
            # Sistema placa laboratorio:
            #   X: 0 (izquierda) a plate_width (derecha)
            #   Y: 0 (frente)    a plate_depth (fondo)
            # Escalar pocillo a cama: la placa 127x85mm debe caber en 220x220mm
            # Centrar la placa en la cama
            plate_width = 127.0
            plate_depth = 85.0
            plate_offset_x = (bed_width  - plate_width)  / 2
            plate_offset_y = (bed_depth - plate_depth) / 2
            cura_x = (cx + plate_offset_x) - (bed_width  / 2)
            cura_z = (cy + plate_offset_y) - (bed_depth / 2)

            Logger.log("i", f"[BioprintingPlugin] Cama: {bed_width}x{bed_depth} | Pocillo: ({cx},{cy}) -> Cura: ({cura_x:.1f},{cura_z:.1f})")

            # Encontrar el nodo recién cargado
            filename    = os.path.splitext(os.path.basename(stl_path))[0]
            target_node = None

            for node in root.getChildren():
                if hasattr(node, 'getName') and filename in (node.getName() or ""):
                    target_node = node
                    break

            if target_node is None:
                children = [n for n in root.getChildren()
                            if hasattr(n, 'getMeshData') and n.getMeshData() is not None]
                if children:
                    target_node = children[-1]

            if target_node:
                current_pos = target_node.getWorldPosition()
                offset      = Vector(
                    cura_x - current_pos.x,
                    0,
                    cura_z - current_pos.z
                )
                op = TranslateOperation(target_node, offset)
                op.push()

                Logger.log("i", f"[BioprintingPlugin] Nodo posicionado en Cura ({cura_x:.1f}, {cura_z:.1f})")
                self._setStatus(f"Modelo posicionado en pocillo ({cx:.1f}, {cy:.1f}) mm")
            else:
                Logger.log("w", "[BioprintingPlugin] No se encontro el nodo.")

        except Exception as e:
            Logger.log("e", f"[BioprintingPlugin] Error posicionando nodo: {e}")

    @pyqtSlot(str)
    def assignSTLToAllWells(self, support_type):
        """Asigna el mismo STL a todos los pocillos y los carga en escena."""
        from .ScaffoldGenerator import SUPPORTS
        dialog = QFileDialog()
        dialog.setWindowTitle("Seleccionar STL para todos los pocillos")
        dialog.setNameFilter("Archivos STL (*.stl)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        if not dialog.exec():
            return

        files = dialog.selectedFiles()
        if not files:
            return

        stl_path = files[0]
        name     = os.path.splitext(os.path.basename(stl_path))[0]
        wells    = SUPPORTS.get(support_type, {}).get("wells", [])

        for well in wells:
            self._well_assignments[well["id"]] = {
                "stl_path": stl_path,
                "name":     name
            }

        self.wellAssignChanged.emit()

        # Cargar un modelo por cada pocillo en la escena de Cura
        from PyQt6.QtCore import QTimer
        delay = 0
        for well in wells:
            cx = well["cx"]
            cy = well["cy"]
            # Escalonar la carga para dar tiempo a Cura de procesar cada STL
            QTimer.singleShot(delay, lambda c=(cx, cy): self._loadAndPosition(stl_path, c[0], c[1]))
            delay += 600

        self._setStatus(f"Cargando {len(wells)} modelos en escena...")

    @pyqtSlot(int)
    def clearWellAssignment(self, well_index):
        if well_index in self._well_assignments:
            del self._well_assignments[well_index]
            self.wellAssignChanged.emit()

    @pyqtSlot()
    def clearScene(self):
        """Elimina solo los modelos STL de la escena, sin tocar la cama."""
        try:
            from UM.Application import Application
            from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation
            from UM.Operations.GroupedOperation import GroupedOperation
            from cura.Scene.CuraSceneNode import CuraSceneNode

            app   = Application.getInstance()
            scene = app.getController().getScene()
            root  = scene.getRoot()

            # Filtrar solo nodos STL importados por el usuario
            # CuraSceneNode con mesh data y que NO sean la cama (BuildPlate)
            nodes = []
            for node in root.getChildren():
                # Saltar nodos del sistema (cama, origen, etc)
                node_type = type(node).__name__
                if node_type in ["BuildPlateDecorator", "BuildVolume", "Platform"]:
                    continue
                if "build" in node_type.lower() or "platform" in node_type.lower():
                    continue
                # Solo tomar CuraSceneNodes con mesh data
                if isinstance(node, CuraSceneNode) and node.getMeshData() is not None:
                    nodes.append(node)

            if not nodes:
                self._setStatus("La escena ya esta vacia.")
                return

            op = GroupedOperation()
            for node in nodes:
                op.addOperation(RemoveSceneNodeOperation(node))
            op.push()

            self._well_assignments = {}
            self.wellAssignChanged.emit()
            self._setStatus(f"{len(nodes)} modelo(s) eliminado(s) de la escena.")

        except Exception as e:
            Logger.log("e", f"[BioprintingPlugin] Error limpiando escena: {e}")

    # ── Generar G-code ─────────────────────────────────────────────────

    @pyqtSlot(str, str, "QVariantList")
    def generateGCode(self, bioink_name, support_type, selected_wells):
        from .ScaffoldGenerator import GCodeGenerator

        perfil = self._perfiles.get(bioink_name)
        if not perfil:
            self._setStatus("Error: biotinta no encontrada.")
            return
        if not selected_wells:
            self._setStatus("Selecciona al menos un pocillo.")
            return

        assignments = {}
        for well_index in selected_wells:
            idx = int(well_index)
            if idx in self._well_assignments:
                assignments[idx] = self._well_assignments[idx]
            else:
                self._setStatus(f"Pocillo {idx + 1} sin STL asignado.")
                return

        save_dialog = QFileDialog()
        save_dialog.setWindowTitle("Guardar G-code")
        save_dialog.setNameFilter("Archivos G-code (*.gcode)")
        save_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        save_dialog.setDefaultSuffix("gcode")

        if not save_dialog.exec():
            return

        output_path = save_dialog.selectedFiles()[0]

        try:
            gen    = GCodeGenerator(bioink_profile=perfil, support_type=support_type)
            result = gen.generate(well_assignments=assignments, output_path=output_path)
            self._setStatus(f"G-code guardado: {os.path.basename(result)}")
        except Exception as e:
            self._setStatus(f"Error: {e}")
            Logger.log("e", f"[BioprintingPlugin] {e}")
