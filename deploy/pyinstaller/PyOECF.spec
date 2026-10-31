# -*- mode: python ; coding: utf-8 -*-
# =============================================================================
# Receta de PyInstaller para PyOECF: ÚNICO sitio con las opciones de
# empaquetado. La usan igual la prueba local y el workflow
# .github/workflows/publicar_ejecutables.yml:
#
#   pyinstaller deploy/pyinstaller/PyOECF.spec
#
# Windows y Linux → un único archivo ejecutable (portable).
# macOS           → una aplicación PyOECF.app (PyInstaller desaconseja un
#                   único archivo con ventana en macOS).
# =============================================================================

# cSpell:ignore customtkinter, SPECPATH

# --- Bibliotecas estándar Python
import re
import sys
from pathlib import Path

# --- PyInstaller
from PyInstaller.utils.hooks import collect_data_files

# --- Constantes de la aplicación: el .spec las LEE, no las repite.
#     src/ al path para poder importar kernel (como hace src/main.py)
CARPETA_SPEC = Path(SPECPATH)       # --- Carpeta de este archivo
RAIZ = CARPETA_SPEC.parent.parent   # --- Raíz: deploy/pyinstaller/ → raíz
SRC = RAIZ / "src"                  # --- Código fuente
sys.path.insert(0, str(SRC))
from kernel import K                # noqa: E402

# --- Literales mágicos
NOMBRE = K.NOMBRE
PUNTO_ENTRADA = SRC / "main.py"
ES_MAC = sys.platform == "darwin"
ES_WIN = sys.platform == "win32"
DESCRIPCION = "Estudio de la respuesta tonal de una cámara digital"
PARTES_VERSION = 4              # --- Los números de la versión de Windows

# --- Datos que no son código y deben ir dentro:
#     - el archivo de versión (K.ARCHIVO_VERSION)
#     - los iconos de la ventana (K.ICONOS), en su carpeta de imágenes
#       (K.CARPETA_IMG), el .ico, que la ventana usa en Windows, y el PNG
#       de la cabecera
#     - la plantilla PSD de las láminas (K.PLANTILLA_PSD), 48 MB, y las
#       instrucciones de la hoja IA del libro (K.PROMPT_IA), en la carpeta
#       de recursos (K.CARPETA_RECURSOS): el código las busca con K.path,
#       también en el ejecutable
#     - temas de customtkinter: sin ellos la ventana falla al abrir
DATOS = [(str(RAIZ / K.ARCHIVO_VERSION), ".")]
IMG = RAIZ / K.CARPETA_IMG
DATOS += [(str(IMG / icono), K.CARPETA_IMG)
          for icono in (*K.ICONOS, K.ICONO_ICO, K.ICONO_PNG)]
REC = RAIZ / K.CARPETA_RECURSOS
DATOS += [(str(REC / archivo), K.CARPETA_RECURSOS)
          for archivo in (K.PLANTILLA_PSD, K.PROMPT_IA)]
DATOS += collect_data_files("customtkinter")

a = Analysis([str(PUNTO_ENTRADA)], datas=DATOS)
pyz = PYZ(a.pure)

# --- Metadatos de versión del .exe de Windows (nombre, versión, autor):
#     un binario sin ellos puntúa peor en Defender. Todo sale de K
info_version = None
if ES_WIN:
    from PyInstaller.utils.win32.versioninfo import (
        FixedFileInfo, StringFileInfo, StringStruct, StringTable,
        VarFileInfo, VarStruct, VSVersionInfo)
    numeros = [int(n) for n in re.findall(r"\d+", K.version)]
    numeros = (numeros + [0] * PARTES_VERSION)[:PARTES_VERSION]
    tupla = tuple(numeros)
    info_version = VSVersionInfo(
        ffi=FixedFileInfo(filevers=tupla, prodvers=tupla),
        kids=[
            StringFileInfo([StringTable("040904B0", [
                StringStruct("CompanyName", K.AUTOR),
                StringStruct("FileDescription", DESCRIPCION),
                StringStruct("FileVersion", K.version),
                StringStruct("InternalName", NOMBRE),
                StringStruct("LegalCopyright", K.AUTOR),
                StringStruct("OriginalFilename", f"{NOMBRE}.exe"),
                StringStruct("ProductName", NOMBRE),
                StringStruct("ProductVersion", K.version)])]),
            VarFileInfo([VarStruct("Translation", [0x0409, 1200])])])

if ES_MAC:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True,
              name=NOMBRE, console=False, upx=False)
    coll = COLLECT(exe, a.binaries, a.datas, name=NOMBRE, upx=False)
    app = BUNDLE(coll, name=f"{NOMBRE}.app",
                 icon=str(CARPETA_SPEC / K.ICONO_ICNS))

else:
    # --- Windows y Linux: un único archivo (portable). Sin UPX; en
    #     Windows, con icono y metadatos de versión
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [],
              name=NOMBRE, console=False, upx=False,
              icon=str(IMG / K.ICONO_ICO) if ES_WIN else None,
              version=info_version)
