# -*- coding: utf-8 *-*
"""
    :Propósito: Constantes de PyOECF
    :Autor:     Tony Diana
    :Versión:   26.10.17
"""

# cSpell:ignore anni, annus, github, meipass, primus, rawpy, srgb, ultimus
# cSpell:ignore Valencià, windll

__all__ = ["COM", "K"]

# --- Bibliotecas estándar Python
import locale
import os
import sys
from pathlib import Path

# --- Bibliotecas internas
from bib import std


#
# --- Código de idioma del sistema, si es uno de los conocidos; si no, el
#     de por defecto. Linux y macOS lo dicen en variables de entorno
#     (es_ES.UTF-8, o es:en en LANGUAGE); Windows, en su idioma de la
#     interfaz. Solo cuentan las dos primeras letras
def _idioma_sistema(variables: tuple[str, ...], conocidos: dict,
                    defecto: str) -> str:
    code = next((os.environ[v] for v in variables if os.environ.get(v)),
                "")
    if (not code) and sys.platform.startswith("win"):
        import ctypes
        _x = ctypes.windll.kernel32.GetUserDefaultUILanguage()  # type: ignore
        interfaz = _x

        code = locale.windows_locale.get(interfaz, "")

    if not code:
        code = locale.getlocale()[0] or ""

    code = code[:2].lower()
    return code if (code in conocidos) else defecto


#
# --- Constantes PyOECF
class K(std.EnumMutable):
    """ Constantes de PyOECF. """

    # --- Identidad del proyecto: nombre, usuario de GitHub, su
    #     repositorio y la web de ayuda (GitHub Pages). OJO: el
    #     repositorio también está en rec/scripts/remoto.conf (bash)
    NOMBRE = "PyOECF"
    """ Nombre del programa (ventana, archivos de resultados). """
    USUARIO_GITHUB = "TonyDiana"
    REPO_GITHUB = f"{USUARIO_GITHUB}/{NOMBRE}"
    """ Repositorio en GitHub: usuario/nombre. """
    URL_HELP = f"https://{USUARIO_GITHUB.lower()}.github.io/{NOMBRE}/"
    """ Web de ayuda (GitHub Pages). """

    # --- Autor y años del copyright: el primero y el de la última
    #     publicación. Al publicar en un año nuevo, cambiar annus_ultimus
    #     (no se toma del reloj: el año del copyright es el de publicación)
    AUTOR = "Tony Diana"
    ANNUS_PRIMUS = 2026
    ANNUS_ULTIMUS = 2026

    #
    @std.classproperty
    def derechos(cls) -> str:
        """
        «© 2026 Tony Diana», o «© 2026–2027 Tony Diana» si hay varios años.
        """
        anni = str(cls.ANNUS_PRIMUS)
        if cls.ANNUS_ULTIMUS != cls.ANNUS_PRIMUS:
            anni += f"–{cls.ANNUS_ULTIMUS}"
        return f"© {anni} {cls.AUTOR}"

    # --- Idiomas: código y nombre en su propio idioma. Cada texto
    #     traducible es un dict {código: texto}
    ES = "es"
    """ Código del español. """
    EN = "en"
    """ Código del inglés. """
    CA = "ca"
    """ Código del valenciano (ca_ES@valencia). """
    IDIOMAS = {ES: "Español", EN: "English", CA: "Valencià"}
    """ Idiomas de la app: {código: nombre en su propio idioma}. """

    # --- Idioma activo: al arrancar, el del sistema (inglés si PyOECF no
    #     lo conoce); cambia en marcha al elegir otro. Variables de
    #     entorno que lo indican, por orden de prioridad
    IDIOMA_DEFECTO = EN
    VARIABLES_IDIOMA = ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG")
    idioma = _idioma_sistema(VARIABLES_IDIOMA, IDIOMAS, IDIOMA_DEFECTO)
    """ Código del idioma activo (cambia al elegir otro en la lista). """

    #
    @classmethod
    def tr(cls, texto: dict) -> str:
        """ Devuelve el texto en el idioma activo. """
        return texto[cls.idioma]

    #
    # --- Textos con número: cada idioma lleva (singular, plural). En los
    #     tres idiomas, singular solo con 1
    @classmethod
    def tr_n(cls, texto: dict, n: int) -> str:
        """ Devuelve el texto en el idioma activo, en singular o plural. """
        singular, plural = texto[cls.idioma]
        return singular if (n == 1) else plural

    #
    # --- Versión: archivo en la raíz del proyecto (PyOECF.spec lo mete en
    #     el ejecutable leyendo este mismo nombre)
    ARCHIVO_VERSION = "VERSION"
    """ Archivo con la versión, en la raíz del proyecto. """

    #
    # --- Icono de la ventana, en la carpeta de recursos: uno para cada
    #     tema (PyOECF.spec lo mete en el ejecutable leyendo estos nombres).
    #     NO en el rec/ de la raíz: Remoto.sh lo quita de la rama de
    #     despliegue (solo ese; src/_rec se despliega)
    CARPETA_RECURSOS = "src/_rec"
    """ Carpeta de los recursos de la app, desde la raíz del proyecto. """
    CARPETA_IMG = f"{CARPETA_RECURSOS}/img"
    """ Carpeta de los iconos, dentro de la de recursos. """
    ICONO_TEMA_CLARO = "logo_n.png"
    """ Icono de la ventana con tema claro: negro. """
    ICONO_TEMA_OSCURO = "logo_b.png"
    """ Icono de la ventana con tema oscuro: blanco. """
    ICONOS = (ICONO_TEMA_CLARO, ICONO_TEMA_OSCURO)

    # --- Icono del programa: el del .exe de Windows y el del .app de
    #     macOS (barra de tareas, Dock). Diana negra sobre gris 18 %, el
    #     de la carta de gris. El .ico va también en la ventana de Windows
    ICONO_ICO = "PyOECF.ico"
    """ Icono de Windows (.exe y ventana). """
    ICONO_ICNS = "PyOECF.icns"

    # --- El mismo icono en PNG, a su tamaño, para la cabecera de la ventana
    ICONO_PNG = "PyOECF.png"
    """ Icono de la cabecera de la ventana. """

    #
    # --- Archivos de datos que viajan en la carpeta de recursos (el .spec
    #     los mete en el ejecutable leyendo estos nombres)
    PLANTILLA_PSD = "Soportes.psd"
    """ Plantilla de las láminas (PSD, RGB a 16 bits, 3300 × 2400 px). """
    PROMPT_IA = "prompt_ia.md"
    """
    Instrucciones para revisar el libro con una IA (su hoja IA), solo en
    español: en los recursos, para poder editarlas sin tocar el código.
    """

    #
    @std.classproperty
    def version(cls) -> str:
        """ Versión del programa: la del archivo VERSION de la raíz. """
        ruta = cls.path / cls.ARCHIVO_VERSION
        return ruta.read_text(encoding="utf-8").strip()

    #
    # --- Atributo de sys donde PyInstaller deja la carpeta de sus datos.
    #     ÚNICO sitio que lo conoce: quien necesite una carpeta del
    #     programa, la pide a K.path
    ATRIBUTO_PYINSTALLER = "_MEIPASS"

    #
    @std.classproperty
    def path(cls) -> Path:
        """ Carpeta del proyecto. """

        # --- Empaquetado: PyInstaller copia los datos a su propia carpeta
        empaquetado = getattr(sys, cls.ATRIBUTO_PYINSTALLER, None)
        if empaquetado:
            return Path(empaquetado)

        # --- Desde el código: este archivo vive en <raíz>/src/kernel/
        return Path(__file__).resolve().parents[2]

    #
    @std.classproperty
    def ruta_plantilla(cls) -> Path:
        """ Ruta de la plantilla de las láminas. """
        return cls.path / cls.CARPETA_RECURSOS / cls.PLANTILLA_PSD

    #
    @std.classproperty
    def ruta_prompt_ia(cls) -> Path:
        """ Ruta de las instrucciones de la hoja IA. """
        return cls.path / cls.CARPETA_RECURSOS / cls.PROMPT_IA


#
# --- Constantes comunes del cálculo
class COM(std.EnumMutable):
    """ Constantes comunes del cálculo: método, CIELab y TIFF. """

    # --- Archivos
    EXTENSIONES = (".arw", ".cr2", ".cr3", ".nef", ".raf")
    """Extensiones RAW (en minúsculas). Comprobadas con archivos reales:
    ARW, CR2, CR3, NEF y RAF."""

    EXTENSIONES_TIFF = (".tif", ".tiff")
    """Extensiones de las exportaciones del revelador (en minúsculas), para
    la segunda parte del análisis."""

    # --- Números
    CIEN = 100
    """Para pasar fracciones o divisores a porcentaje."""

    MARGEN_TV = 0.01
    """Margen al comparar tiempos: rawpy los da con poca precisión."""

    CANALES_RGB = 3
    """Canales de color: rojo, verde y azul (matriz de color de la cámara,
    imagen compuesta de la lámina y columnas por canal del libro)."""

    MAX_16 = 65535
    """Máximo de un valor de 16 bits (imagen compuesta de la lámina y
    tablas de las curvas ICC)."""

    # --- Criterios del método, que comparten la medida y el libro (el
    #     libro las escribe en su hoja Constantes)
    UMBRAL_RECORTE = 0.995
    """Recortado: un valor llega a esta fracción del máximo de su canal
    en la serie (en el libro, la constante KXL.C_UMBRAL_RECORTE)."""

    TOLERANCIA_LINEAL = 0.1
    """Tolerancia de linealidad, en zonas: un punto es lineal si se aparta
    menos de lo esperado; una Z-V de control que se aparta más de la ZV
    dice que la luz cambió (en el libro, KXL.C_TOLERANCIA_LINEAL)."""

    # --- CIELab (ISO/CIE 11664-4): L* de una luminancia relativa Y es
    #     (LAB_ESCALA · Y^(1/3)) − LAB_DESPLAZA, o LAB_PENDIENTE · Y por
    #     debajo de LAB_UMBRAL. Las usan el libro y la medida del revelador
    LAB_ESCALA = 116
    """CIELab: factor de la raíz cúbica de Y."""

    LAB_DESPLAZA = 16
    """CIELab: lo que se resta tras la raíz cúbica."""

    LAB_UMBRAL = 0.008856
    """CIELab: por debajo de esta Y, el tramo recto."""

    LAB_PENDIENTE = 903.3
    """CIELab: pendiente del tramo recto, por debajo de LAB_UMBRAL."""

    # --- sRGB (IEC 61966-2-1): curva entre el valor codificado y la luz.
    #     Los tramos rectos tienen dos umbrales, uno por sentido. Las usan
    #     el libro (hoja Constantes) y el reconocimiento del espacio de las
    #     exportaciones del revelador
    SRGB_GAMMA = 2.4
    """sRGB: exponente de la curva."""

    SRGB_PENDIENTE = 12.92
    """sRGB: pendiente del tramo recto."""

    SRGB_ESCALA = 1.055
    """sRGB: factor de la potencia."""

    SRGB_DESPLAZA = 0.055
    """sRGB: desplazamiento de la potencia."""

    SRGB_UMBRAL_CODIFICADO = 0.04045
    """sRGB: por debajo de este valor codificado (de 0 a 1), el tramo
    recto."""

    SRGB_UMBRAL_LUZ = 0.0031308
    """sRGB: por debajo de esta luz lineal (de 0 a 1), el tramo recto."""

    # --- TIFF (casi todos los RAW lo son o lo llevan dentro)
    BYTES_CABECERA = 262144
    """Bytes del principio del archivo (256 KiB) que se leen para buscar
    los datos de la cámara (marca, modelo, balance…)."""

    FIRMAS_TIFF = ((b"II*\x00", "<"), (b"MM\x00*", ">"))
    """Firmas de la cabecera TIFF, con su orden de bytes para struct."""

    BYTES_ORDEN = 2
    """Bytes de la marca de orden con que empieza la firma TIFF («II» o
    «MM»)."""

    TIPO_ASCII = 2
    """Tipo TIFF de una entrada de texto ASCII."""

    MAX_ENTRADAS = 200
    """Máximo de entradas creíble en un directorio TIFF: con más, no es un
    directorio de verdad."""

    BYTES_ENTRADA = 12
    """Tamaño de cada entrada de un directorio TIFF."""

    BYTES_EN_ENTRADA = 4
    """Tamaño del valor de una entrada: un dato que cabe aquí va en ella;
    si no, la entrada dice dónde está."""

    ETIQUETA_EXIF = 0x8769
    """Etiqueta TIFF del directorio EXIF."""

    ETIQUETA_NOTAS = 0x927C
    """Etiqueta EXIF de las notas del fabricante."""

    # --- TIFF: formatos de struct (sin el orden de bytes, que va delante)
    FORMATO_ENTERO = "I"
    """Entero de 4 bytes (desplazamientos y valores)."""

    FORMATO_CORTO = "H"
    """Entero de 2 bytes (como el número de entradas de un directorio)."""

    FORMATO_ENTRADA = "HHI4s"
    """Entrada de un directorio: etiqueta, tipo, cuenta y valor."""

    FORMATO_LISTA = "{cuenta}h"
    """Lista de cuenta enteros de 2 bytes con signo."""

    BYTES_CORTO = 2
    """Bytes de un entero de 2 (FORMATO_CORTO)."""

    POS_PRIMER_DIRECTORIO = 4
    """Posición, en la cabecera TIFF, del desplazamiento del primer
    directorio."""
