import os

from UM.Extension import Extension
from UM.Logger import Logger

# Cura 5.7 usa PyQt6
try:
    from PyQt6.QtWidgets import QMessageBox
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal
    PYQT = 6
except ImportError:
    from PyQt5.QtWidgets import QMessageBox
    from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal
    PYQT = 5


class BioprintingPlugin(QObject, Extension):
    """
    Plugin de bioimpresión para Ultimaker Cura 5.7+
    Tesis Ingeniería Biomédica — PUCP
    Autor: Mauricio Ramos Gallegos
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMenuName("Bioimpresion")
        self.addMenuItem("Configurar Biotinta", self.showBiotintaWindow)
        self.addMenuItem("Acerca del plugin",   self.showAboutWindow)

        self._biotinta_window = None
        self._about_window    = None

        # Perfiles de biotinta validados para extrusión por jeringa
        self._perfiles = {
            "Alginato de Sodio": {
                "layer_height":               0.2,
                "speed_print":                10,
                "material_print_temperature": 25,
                "retraction_enable":          False,
                "infill_sparse_density":      30,
                "description": "Hidrogel natural de algas. Alta biocompatibilidad. Crosslinking con CaCl2."
            },
            "Colageno": {
                "layer_height":               0.15,
                "speed_print":                8,
                "material_print_temperature": 20,
                "retraction_enable":          False,
                "infill_sparse_density":      40,
                "description": "Proteina estructural ECM. Excelente adhesion celular."
            },
            "Gelatina": {
                "layer_height":               0.2,
                "speed_print":                12,
                "material_print_temperature": 22,
                "retraction_enable":          False,
                "infill_sparse_density":      35,
                "description": "Derivado del colageno. Buena imprimibilidad."
            },
            "GelMA": {
                "layer_height":               0.15,
                "speed_print":                9,
                "material_print_temperature": 22,
                "retraction_enable":          False,
                "infill_sparse_density":      40,
                "description": "Gelatina modificada. Alta estabilidad post-UV."
            },
            "Pluronic F-127": {
                "layer_height":               0.3,
                "speed_print":                15,
                "material_print_temperature": 20,
                "retraction_enable":          False,
                "infill_sparse_density":      25,
                "description": "Polimero sintetico. Excelente imprimibilidad."
            },
        }

        Logger.log("i", f"[BioprintingPlugin] *** CARGADO *** PyQt{PYQT} | dir: {os.path.dirname(__file__)}")

    # ── Ventanas ───────────────────────────────────────────────────────────

    def showBiotintaWindow(self):
        if self._biotinta_window is None:
            self._biotinta_window = self._cargarQml("BioprintingDialog.qml")
        if self._biotinta_window:
            self._biotinta_window.show()
        else:
            Logger.log("e", "[BioprintingPlugin] No se pudo cargar BioprintingDialog.qml")

    def showAboutWindow(self):
        if self._about_window is None:
            self._about_window = self._cargarQml("AboutDialog.qml")
        if self._about_window:
            self._about_window.show()
        else:
            Logger.log("e", "[BioprintingPlugin] No se pudo cargar AboutDialog.qml")

    def _cargarQml(self, filename):
        from UM.Application import Application
        ruta = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "resources", "qml", filename
        )
        if not os.path.exists(ruta):
            Logger.log("e", f"[BioprintingPlugin] Archivo QML no encontrado: {ruta}")
            return None
        Logger.log("d", f"[BioprintingPlugin] Cargando QML: {ruta}")
        return Application.getInstance().createQmlComponent(ruta, {"manager": self})

    # ── Propiedades para QML ───────────────────────────────────────────────

    @pyqtProperty("QStringList", constant=True)
    def bioinkNames(self):
        return list(self._perfiles.keys())

    @pyqtSlot(str, result="QVariantMap")
    def getBioinkProfile(self, name: str):
        return self._perfiles.get(name, {})

    @pyqtSlot(str)
    def applyBioinkProfile(self, name: str):
        from UM.Application import Application
        perfil = self._perfiles.get(name)
        if not perfil:
            Logger.log("w", f"[BioprintingPlugin] Perfil no encontrado: {name}")
            return

        stack = Application.getInstance().getGlobalContainerStack()
        if not stack:
            Logger.log("e", "[BioprintingPlugin] Sin impresora activa en Cura.")
            return

        params = {
            "layer_height":               perfil["layer_height"],
            "speed_print":                perfil["speed_print"],
            "material_print_temperature": perfil["material_print_temperature"],
            "retraction_enable":          perfil["retraction_enable"],
            "infill_sparse_density":      perfil["infill_sparse_density"],
        }
        for key, value in params.items():
            try:
                stack.setProperty(key, "value", value)
                Logger.log("i", f"[BioprintingPlugin] {key} = {value} OK")
            except Exception as e:
                Logger.log("w", f"[BioprintingPlugin] Error aplicando {key}: {e}")

        Logger.log("i", f"[BioprintingPlugin] Perfil '{name}' aplicado.")
