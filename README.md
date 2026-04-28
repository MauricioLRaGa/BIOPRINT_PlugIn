# 🧬 Bioprinting Plugin para Ultimaker Cura

> Plugin de laminado con gestión de biotintas para bioimpresoras de extrusión por jeringa.  
> Desarrollado como tesis de grado en Ingeniería Biomédica — PUCP, Lima, Perú.

![Cura 5.7+](https://img.shields.io/badge/Cura-5.7%2B-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)
![SDK](https://img.shields.io/badge/SDK-8.7.0-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## ¿Qué hace este plugin?

Agrega un menú nativo **Extensions → Bioimpresión** dentro de Ultimaker Cura que permite:

- **Seleccionar una biotinta predefinida** con parámetros validados para extrusión por jeringa
- **Visualizar el soporte de impresión** (Placa Petri, Multipocillos 6 o 24) con pocillos seleccionables
- **Aplicar automáticamente los parámetros** al stack de configuración activo de Cura con un solo clic
- **Consultar la descripción** de cada biotinta con sus propiedades reológicas clave

---

## Capturas de pantalla

### Ventana principal — Gestión de Biotintas
*Selector de biotinta con descripción, visualización de soporte multipocillos 6 y parámetros sugeridos*

### Ventana Acerca de
*Información del plugin, versión y datos de autoría*

> 📸 *Las capturas se encuentran en la carpeta `/docs/screenshots/` del repositorio.*

---

## Biotintas soportadas

| Biotinta | Vel. impresión (mm/s) | Temperatura (°C) | Altura de capa (mm) | Densidad relleno (%) | Retracción |
|---|---|---|---|---|---|
| Alginato de Sodio | 10 | 25 | 0.20 | 30 | ❌ |
| Colágeno | 8 | 20 | 0.15 | 40 | ❌ |
| Gelatina | 12 | 22 | 0.20 | 35 | ❌ |
| GelMA | 9 | 22 | 0.15 | 40 | ❌ |
| Pluronic F-127 | 15 | 20 | 0.30 | 25 | ❌ |

> La retracción está deshabilitada en todos los perfiles porque los hidrogeles y biotintas blandas no requieren retracción — a diferencia de los termoplásticos convencionales.

---

## Soportes de impresión

| Soporte | Dimensiones | Pocillos | Selección individual |
|---|---|---|---|
| Placa Petri | Ø 90mm × 15mm | — | Zona central de impresión |
| Multipocillos 6 | 127mm × 85mm | 6 | ✅ Clic por pocillo |
| Multipocillos 24 | 127mm × 85mm | 24 | ✅ Clic por pocillo |

---

## Instalación

### Requisitos
- Ultimaker Cura **5.7 o superior**
- Windows, macOS o Linux

### Pasos

**1 — Clona o descarga el repositorio:**
```bash
git clone https://github.com/TuUsuario/BioprintingPlugin.git
```

**2 — Copia la carpeta interna `BioprintingPlugin` al directorio de plugins de Cura:**

| Sistema | Ruta |
|---|---|
| Windows | `%APPDATA%\cura\5.7\plugins\BioprintingPlugin\` |
| macOS | `~/Library/Application Support/cura/5.7/plugins/BioprintingPlugin/` |
| Linux | `~/.local/share/cura/5.7/plugins/BioprintingPlugin/` |

> ⚠️ **Importante:** La estructura final debe ser `plugins/BioprintingPlugin/BioprintingPlugin/` (carpeta duplicada). Cura requiere este formato para plugins externos.

**3 — Reinicia Ultimaker Cura**

**4 — Abre el plugin:**
```
Extensions → Bioimpresión → Configurar Biotinta
```

### Instalación rápida en Windows con Git Bash

```bash
# Clonar y copiar en un solo paso
git clone https://github.com/TuUsuario/BioprintingPlugin.git
cp -r BioprintingPlugin/BioprintingPlugin "$APPDATA/cura/5.7/plugins/BioprintingPlugin"
```

---

## Estructura del proyecto

```
BioprintingPlugin/
├── __init__.py                  # Registro del plugin en Cura (entry point)
├── plugin.json                  # Metadatos: nombre, versión, SDK 8.7.0
├── BioprintingPlugin.py         # Lógica principal, perfiles de biotinta,
│                                # propiedades expuestas a QML (pyqtSlot/pyqtProperty)
└── resources/
    └── qml/
        ├── BioprintingDialog.qml    # Ventana principal: biotinta + soporte + parámetros
        └── AboutDialog.qml          # Ventana "Acerca de"
```

---

## Arquitectura técnica

El plugin sigue la arquitectura de extensiones nativas de Ultimaker Cura:

```
Cura (PyQt6 + QML)
    └── Extension API
            └── BioprintingPlugin (Python)
                    ├── setMenuName()        → registra menú en Extensions
                    ├── addMenuItem()        → agrega ítems al menú
                    ├── pyqtProperty         → expone datos a QML
                    ├── pyqtSlot             → recibe eventos desde QML
                    └── createQmlComponent() → instancia ventanas QML
                            ├── BioprintingDialog.qml
                            └── AboutDialog.qml
```

**Flujo de datos:**
```
Usuario selecciona biotinta en QML
    → manager.getBioinkProfile(name) [Python]
    → retorna perfil como QVariantMap
    → QML actualiza parámetros en pantalla
    → Usuario presiona "Aplicar a Cura"
    → manager.applyBioinkProfile(name) [Python]
    → stack.setProperty() aplica al motor de Cura
```

---

## Compatibilidad

| Componente | Versión |
|---|---|
| Ultimaker Cura | 5.7+ |
| SDK API | 8.7.0 |
| Python | 3.x (incluido en Cura) |
| PyQt | 6.6.0 (incluido en Cura) |
| QML | QtQuick 2.15 / UM 1.6 |

---

## Estado del desarrollo

- [x] Estructura base del plugin (Extension API)
- [x] Registro en menú Extensions de Cura
- [x] Perfiles de 5 biotintas con parámetros validados
- [x] Interfaz QML con selector de biotinta y descripción
- [x] Visualización de Placa Petri con zona de impresión
- [x] Visualización de Multipocillos 6 con pocillos clickeables
- [x] Visualización de Multipocillos 24 con pocillos clickeables
- [x] Aplicación de parámetros al stack activo de Cura
- [x] Ventana "Acerca de" con datos de autoría
- [ ] Validación física con alginato de sodio en CELLINK BioX
- [ ] Generación de G-code adaptado por soporte seleccionado
- [ ] Perfiles de biotinta personalizables por el usuario
- [ ] Migración a Cura Marketplace

---

## Contexto académico

Este plugin fue desarrollado como parte de la tesis:

> **"Diseño e Implementación de un Complemento de Laminado con Gestión de Biotintas para Bioimpresoras de Extrusión"**
>
> Tesis para obtener el título profesional de **Ingeniero Biomédico**  
> Pontificia Universidad Católica del Perú (PUCP) — Lima, Perú, 2025

**Problema que resuelve:** Los laminadores convencionales (Cura, Simplify3D) están diseñados para materiales termoplásticos y no contemplan los parámetros críticos de las biotintas: viscosidad, temperatura fisiológica de extrusión, ausencia de retracción, y adaptación a soportes de cultivo celular. Este plugin cubre esa brecha mediante perfiles automatizados integrados directamente en Cura.

---

## Autor

**Mauricio Leonardo Ramos Gallegos**  
Ingeniería Biomédica — PUCP, Lima, Perú  
Asesora: Ana Cristina Midori Sanchez Sifuentes  
Laboratorio FABCORE — PUCP

---

## Licencia

MIT License — libre para uso académico y de investigación.