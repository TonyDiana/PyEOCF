# -*- coding: utf-8 *-*
"""
    :Propósito: Píxeles defectuosos del sensor: los calientes (con las tomas
                tapadas, confirmados con la Z0) y los muertos (con las Z-V,
                confirmados con la ZX), contados por megapíxel
    :Autor:     Tony Diana
    :Versión:   26.10.28
"""

# cSpell:ignore kpx, rawpy

__all__ = ["KPX", "Pixeles", "contar_pixeles"]

# --- Bibliotecas estándar Python
from dataclasses import dataclass
from pathlib import Path

# --- Bibliotecas externas
import numpy as np
import rawpy

# --- Bibliotecas internas
from bib import std
from .teselas import KTE


#
class KPX(std.EnumMutable):
    """ Constantes del recuento de píxeles defectuosos. """

    SIGMAS_CALIENTE = 12
    """Un píxel es caliente si, en todas las tapadas, sube más de estas
    desviaciones típicas robustas (las de la tapada entera) sobre el negro."""

    MIN_TAPADAS = 2
    """Tapadas necesarias: un píxel caliente sale en todas ellas."""

    CONFIRMA = 10
    """Niveles sobre la mediana de sus vecinos con que la Z0 confirma un
    píxel caliente."""

    MUERTO = 0.5
    """Fracción de la mediana de sus vecinos por debajo de la cual un píxel
    está muerto."""

    MUERTO_PREVIO = 0.8
    """Corte más flojo, sobre la media de sus vecinos, para elegir a los
    candidatos a muerto antes de calcular su mediana."""

    NIVEL_MIN = 200
    """Nivel mínimo, sobre el negro, de los vecinos para buscar muertos: con
    menos luz un muerto no se distingue."""

    MAX_ZV = 3
    """Z-V que se miran para los muertos (un muerto sale en todas)."""

    VECINO = 2
    """Distancia, en píxeles, a los vecinos del mismo color (mosaico 2 × 2)."""

    MOSAICO = (2, 2)
    """Mosaico de color que sabe tratar (Bayer): cada color, a un píxel de
    distancia en su plano."""

    PX_MPX = 1_000_000
    """Píxeles de un megapíxel."""


#
@dataclass(frozen=True, slots=True, kw_only=True)
class Pixeles(object):
    """
    Píxeles defectuosos: calientes (con las tapadas; None sin ellas) y
    cuántos confirma la Z0 (None sin Z0), muertos (con las Z-V; None sin
    ellas) y los megapíxeles del sensor, para contarlos por megapíxel.
    """
    calientes: int | None
    confirmados: int | None
    muertos: int | None
    megapixeles: float

    #
    @property
    def calientesMpx(self) -> float | None:
        """ Saber los calientes por megapíxel (None si no se contaron). """
        return (None if (self.calientes is None)
                else self.calientes / self.megapixeles)

    #
    @property
    def muertosMpx(self) -> float | None:
        """ Saber los muertos por megapíxel (None si no se contaron). """
        return (None if (self.muertos is None)
                else self.muertos / self.megapixeles)


#
def contar_pixeles(tapadas: list[Path], z0: Path | None, zvs: list[Path],
                   zx: Path | None, buenas: np.ndarray,
                   negro: tuple[float, ...], alto: int,
                   ancho: int) -> Pixeles | None:
    """
    Píxeles defectuosos de un sensor, con las copias de la serie. Calientes:
    los que suben sobre el negro en todas las tapadas (si hay al menos
    KPX.MIN_TAPADAS), confirmados en la Z0. Muertos: los que, en las
    teselas buenas (buenas, filas × columnas de KTE.LADO), marcan mucho
    menos que sus vecinos en todas las Z-V (las KPX.MAX_ZV primeras) y en
    la ZX. negro: el de cada canal del RAW. None si el mosaico de color no
    es el de Bayer.
    """
    calientes = None
    confirmados = None
    if len(tapadas) >= KPX.MIN_TAPADAS:
        calientes = _calientes(tapadas, negro)
        if calientes is None:
            return None
        if z0 is not None:
            confirmados = _confirmados(z0, calientes)

    muertos = None
    if zvs:
        muertos = _muertos(zvs[:KPX.MAX_ZV], zx, buenas, negro)
        if muertos is None:
            return None
    return Pixeles(
        calientes=None if (calientes is None) else len(calientes),
        confirmados=confirmados,
        muertos=muertos,
        megapixeles=(alto * ancho) / KPX.PX_MPX)


#
# --- La imagen visible de un RAW sin revelar, el color de cada píxel y su
#     mosaico (None si no es el que KPX.MOSAICO sabe tratar)
def _leer(archivo: Path) -> tuple[np.ndarray, np.ndarray] | None:
    with rawpy.imread(str(archivo)) as raw:
        if tuple(np.asarray(raw.raw_pattern).shape) != KPX.MOSAICO:
            return None
        return (raw.raw_image_visible.astype(np.float32),
                raw.raw_colors_visible.copy())


#
# --- Dónde están los píxeles calientes: los que suben más de
#     KPX.SIGMAS_CALIENTE desviaciones típicas robustas sobre el negro en
#     todas las tapadas, como (fila, columna). None si no se puede leer el
#     mosaico
def _calientes(tapadas: list[Path],
               negro: tuple[float, ...]) -> np.ndarray | None:
    comunes = None
    for archivo in tapadas:
        leida = _leer(archivo)
        if leida is None:
            return None
        imagen, colores = leida
        imagen -= np.asarray(negro, dtype=np.float32)[colores]
        escala = KTE.ESCALA_DAM * np.median(np.abs(imagen
                                                   - np.median(imagen)))
        suben = imagen > (KPX.SIGMAS_CALIENTE * escala)
        comunes = suben if (comunes is None) else (comunes & suben)
    return np.argwhere(comunes)


#
# --- Mediana de los ocho vecinos del mismo color de unos píxeles (a
#     KPX.VECINO píxeles, en el mosaico 2 × 2)
def _vecinos(imagen: np.ndarray, filas: np.ndarray,
             columnas: np.ndarray) -> np.ndarray:
    d = KPX.VECINO
    return np.median(np.stack([imagen[filas + df, columnas + dc]
                               for df in (-d, 0, d) for dc in (-d, 0, d)
                               if (df, dc) != (0, 0)]), axis=0)


#
# --- Cuántos de los píxeles calientes confirma la Z0: los que superan a sus
#     vecinos en más de KPX.CONFIRMA niveles (los de los bordes, no)
def _confirmados(z0: Path, calientes: np.ndarray) -> int | None:
    leida = _leer(z0)
    if leida is None:
        return None
    imagen = leida[0]
    d = KPX.VECINO
    filas, columnas = calientes[:, 0], calientes[:, 1]
    dentro = ((filas >= d) & (filas < imagen.shape[0] - d)
              & (columnas >= d) & (columnas < imagen.shape[1] - d))
    filas, columnas = filas[dentro], columnas[dentro]
    exceso = imagen[filas, columnas] - _vecinos(imagen, filas, columnas)
    return int((exceso > KPX.CONFIRMA).sum())


#
# --- Los píxeles muertos de una toma, como {(fila, columna)}: los de las
#     teselas buenas que marcan menos de KPX.MUERTO veces la mediana de sus
#     vecinos del mismo color, que tienen luz (KPX.NIVEL_MIN). Cada color en
#     su plano (2 × 2); antes de la mediana, un corte flojo sobre la media
#     de sus vecinos deja pocos candidatos. None si no se puede leer
def _muertos_de(archivo: Path, mascara: np.ndarray,
                negro: tuple[float, ...]) -> set[tuple[int, int]] | None:
    leida = _leer(archivo)
    if leida is None:
        return None
    imagen, colores = leida
    imagen -= np.asarray(negro, dtype=np.float32)[colores]
    muertos: set[tuple[int, int]] = set()
    for p in range(KPX.MOSAICO[0]):
        for q in range(KPX.MOSAICO[1]):
            plano = imagen[p::KPX.MOSAICO[0], q::KPX.MOSAICO[1]]
            tesela = mascara[p::KPX.MOSAICO[0], q::KPX.MOSAICO[1]]
            alto, ancho = plano.shape
            suma = np.zeros((alto - 2, ancho - 2), dtype=np.float32)
            for df in range(3):
                for dc in range(3):
                    if (df, dc) != (1, 1):
                        suma += plano[df:(alto - 2 + df), dc:(ancho - 2 + dc)]
            media = suma / 8
            previo = (tesela[1:-1, 1:-1] & (media > KPX.NIVEL_MIN)
                      & (plano[1:-1, 1:-1] < (KPX.MUERTO_PREVIO * media)))
            filas, columnas = np.nonzero(previo)
            filas, columnas = filas + 1, columnas + 1
            if not len(filas):
                continue
            mediana = np.median(np.stack([
                plano[filas + df, columnas + dc]
                for df in (-1, 0, 1) for dc in (-1, 0, 1)
                if (df, dc) != (0, 0)]), axis=0)
            malos = ((mediana > KPX.NIVEL_MIN)
                     & (plano[filas, columnas] < (KPX.MUERTO * mediana)))
            for f, c in zip(filas[malos], columnas[malos]):
                muertos.add(((f * KPX.MOSAICO[0]) + p,
                             (c * KPX.MOSAICO[1]) + q))
    return muertos


#
# --- Cuántos píxeles muertos hay: los que salen en todas las Z-V (zvs) y,
#     si hay ZX, también en ella (marca mucho menos que sus vecinos). None
#     si no se puede leer el mosaico
def _muertos(zvs: list[Path], zx: Path | None, buenas: np.ndarray,
             negro: tuple[float, ...]) -> int | None:
    primera = _leer(zvs[0])
    if primera is None:
        return None
    forma = primera[0].shape
    del primera

    # --- Las teselas buenas, píxel a píxel (lo que sobra de la rejilla,
    #     fuera)
    lado = KTE.LADO
    grande = np.kron(buenas, np.ones((lado, lado), dtype=bool))
    mascara = np.zeros(forma, dtype=bool)
    alto, ancho = min(forma[0], grande.shape[0]), min(forma[1],
                                                       grande.shape[1])
    mascara[:alto, :ancho] = grande[:alto, :ancho]

    comunes = None
    for archivo in zvs:
        de_toma = _muertos_de(archivo, mascara, negro)
        if de_toma is None:
            return None
        comunes = de_toma if (comunes is None) else (comunes & de_toma)
    if (zx is not None) and comunes:
        en_zx = _muertos_de(zx, mascara, negro)
        if en_zx is None:
            return None
        comunes &= en_zx
    return len(comunes) if comunes is not None else 0
