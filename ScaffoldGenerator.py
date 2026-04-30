"""
ScaffoldGenerator.py
Generador de G-code para scaffolds en placas multipocillo y Petri.

Tesis Ingeniería Biomédica — PUCP
Autor: Mauricio Ramos Gallegos
"""

import os
import struct
import math


# ── Coordenadas estándar de soportes de laboratorio ─────────────────────────

SUPPORTS = {
    "petri": {
        "name":        "Placa Petri",
        "width":       90.0,
        "height":      90.0,
        "wells":       [{"id": 0, "cx": 45.0, "cy": 45.0, "r": 42.0}],
    },
    "6": {
        "name":        "Multipocillos 6",
        "width":       127.0,
        "height":      85.0,
        "wells": [
            {"id": 0, "cx": 24.5,  "cy": 21.5, "r": 17.4},
            {"id": 1, "cx": 63.5,  "cy": 21.5, "r": 17.4},
            {"id": 2, "cx": 102.5, "cy": 21.5, "r": 17.4},
            {"id": 3, "cx": 24.5,  "cy": 60.5, "r": 17.4},
            {"id": 4, "cx": 63.5,  "cy": 60.5, "r": 17.4},
            {"id": 5, "cx": 102.5, "cy": 60.5, "r": 17.4},
        ],
    },
    "24": {
        "name":        "Multipocillos 24",
        "width":       127.0,
        "height":      85.0,
        "wells": [
            {"id": i,
             "cx": 14.38 + (i % 6) * 19.3,
             "cy": 10.5  + (i // 6) * 19.3,
             "r":  7.8}
            for i in range(24)
        ],
    },
}


# ── Lector de STL binario ────────────────────────────────────────────────────

def read_stl_binary(path: str):
    """
    Lee un archivo STL binario y retorna lista de triángulos.
    Cada triángulo es una lista de 3 vértices (x, y, z).
    """
    triangles = []
    with open(path, "rb") as f:
        f.read(80)                          # header
        count = struct.unpack("<I", f.read(4))[0]
        for _ in range(count):
            f.read(12)                      # normal vector (ignoramos)
            verts = []
            for _ in range(3):
                x, y, z = struct.unpack("<fff", f.read(12))
                verts.append((x, y, z))
            f.read(2)                       # attribute byte count
            triangles.append(verts)
    return triangles


def get_stl_bounds(triangles):
    """Calcula las dimensiones del modelo STL."""
    xs = [v[0] for tri in triangles for v in tri]
    ys = [v[1] for tri in triangles for v in tri]
    zs = [v[2] for tri in triangles for v in tri]
    return {
        "min_x": min(xs), "max_x": max(xs),
        "min_y": min(ys), "max_y": max(ys),
        "min_z": min(zs), "max_z": max(zs),
        "width":  max(xs) - min(xs),
        "depth":  max(ys) - min(ys),
        "height": max(zs) - min(zs),
    }


# ── Generador de G-code ──────────────────────────────────────────────────────

class GCodeGenerator:
    """
    Genera G-code para scaffolds posicionados en
    soportes de laboratorio (Petri, multipocillos 6 y 24).
    """

    def __init__(self, bioink_profile: dict, support_type: str):
        self.profile      = bioink_profile
        self.support_type = support_type
        self.support_info = SUPPORTS.get(support_type, SUPPORTS["petri"])
        self.lines        = []

    def _emit(self, line: str):
        self.lines.append(line)

    def _header(self):
        """Encabezado del G-code con metadatos del plugin."""
        self._emit("; ============================================================")
        self._emit("; G-code generado por Bioprinting Plugin — PUCP")
        self._emit(f"; Biotinta:  {self.profile.get('name', 'N/A')}")
        self._emit(f"; Soporte:   {self.support_info['name']}")
        self._emit(f"; Temp. extrusión: {self.profile.get('material_print_temperature', 25)} °C")
        self._emit(f"; Velocidad: {self.profile.get('speed_print', 10)} mm/s")
        self._emit(f"; Altura capa: {self.profile.get('layer_height', 0.2)} mm")
        self._emit("; ============================================================")
        self._emit("")
        self._emit("G21 ; unidades en mm")
        self._emit("G90 ; posicionamiento absoluto")
        self._emit("G92 E0 ; reset extrusor")
        self._emit(f"M104 S{self.profile.get('material_print_temperature', 25)} ; temperatura extrusión")
        self._emit(f"M109 S{self.profile.get('material_print_temperature', 25)} ; esperar temperatura")
        self._emit("G28 ; home all axes")
        self._emit("G1 Z5 F3000 ; levantar boquilla")
        self._emit("")

    def _footer(self):
        """Comandos finales del G-code."""
        self._emit("")
        self._emit("; === FIN DE IMPRESIÓN ===")
        self._emit("G1 Z10 F3000 ; levantar boquilla final")
        self._emit("G28 X0 Y0   ; home X e Y")
        self._emit("M104 S0     ; apagar extrusor")
        self._emit("M84         ; apagar motores")

    def _scaffold_at(self, cx: float, cy: float,
                     stl_triangles, bounds: dict,
                     layer_height: float, speed_mm_s: float,
                     well_index: int, model_name: str):
        """
        Genera trayectorias de un scaffold centrado en (cx, cy).
        Usa las trayectorias del STL proyectadas capa por capa.
        """
        speed_mm_min = int(speed_mm_s * 60)
        travel_speed = 6000
        n_layers     = max(1, round(bounds["height"] / layer_height))

        # Offset para centrar el modelo en el pocillo
        ox = cx - (bounds["min_x"] + bounds["width"]  / 2)
        oy = cy - (bounds["min_y"] + bounds["depth"]   / 2)

        self._emit(f"")
        self._emit(f"; --- Pocillo {well_index + 1} | Modelo: {model_name} ---")
        self._emit(f"; Centro: ({cx:.1f}, {cy:.1f}) mm")
        self._emit(f"; Capas: {n_layers}")

        e_total = 0.0
        filament_d   = 1.75
        nozzle_d     = 0.4
        e_per_mm     = (nozzle_d * layer_height) / (math.pi * (filament_d / 2) ** 2)

        for layer in range(n_layers):
            z       = (layer + 1) * layer_height
            z_min   = bounds["min_z"] + layer       * layer_height
            z_max   = bounds["min_z"] + (layer + 1) * layer_height

            # Filtrar triángulos en esta capa
            layer_tris = [
                tri for tri in stl_triangles
                if any(z_min <= v[2] <= z_max for v in tri)
            ]

            if not layer_tris:
                continue

            self._emit(f"")
            self._emit(f"; Capa {layer + 1} / Z={z:.2f}mm")
            self._emit(f"G0 F{travel_speed} Z{z + 0.5:.2f} ; levantar para viaje")

            first_move = True
            for tri in layer_tris:
                # Proyectar vértices al plano Z de la capa
                pts = [(v[0] + ox, v[1] + oy) for v in tri]

                if first_move:
                    self._emit(
                        f"G0 F{travel_speed} "
                        f"X{pts[0][0]:.3f} Y{pts[0][1]:.3f} Z{z:.2f}"
                    )
                    first_move = False

                for px, py in pts[1:]:
                    dx       = px - pts[0][0]
                    dy       = py - pts[0][1]
                    dist     = math.sqrt(dx**2 + dy**2)
                    e_total += dist * e_per_mm
                    self._emit(
                        f"G1 F{speed_mm_min} "
                        f"X{px:.3f} Y{py:.3f} "
                        f"E{e_total:.5f}"
                    )

        # Levantar al terminar el pocillo
        self._emit(f"G0 F{travel_speed} Z{n_layers * layer_height + 2:.2f}")
        self._emit(f"G92 E0 ; reset extrusor tras pocillo {well_index + 1}")

    def generate(self, well_assignments: dict, output_path: str) -> str:
        """
        Genera el G-code completo.

        well_assignments: dict { well_index: {"stl_path": str, "name": str} }
        output_path:      ruta donde guardar el .gcode

        Retorna el path del archivo generado.
        """
        layer_height = self.profile.get("layer_height", 0.2)
        speed        = self.profile.get("speed_print", 10)
        wells        = self.support_info["wells"]

        self._header()

        for well_index, assignment in well_assignments.items():
            well = next((w for w in wells if w["id"] == well_index), None)
            if well is None:
                continue

            stl_path   = assignment.get("stl_path", "")
            model_name = assignment.get("name", f"Modelo {well_index + 1}")

            if not stl_path or not os.path.exists(stl_path):
                self._emit(f"; ⚠ Pocillo {well_index + 1}: STL no encontrado ({stl_path})")
                continue

            try:
                triangles = read_stl_binary(stl_path)
                bounds    = get_stl_bounds(triangles)
                self._scaffold_at(
                    cx=well["cx"], cy=well["cy"],
                    stl_triangles=triangles, bounds=bounds,
                    layer_height=layer_height, speed_mm_s=speed,
                    well_index=well_index, model_name=model_name
                )
            except Exception as e:
                self._emit(f"; ⚠ Error procesando pocillo {well_index + 1}: {e}")

        self._footer()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines))

        return output_path
