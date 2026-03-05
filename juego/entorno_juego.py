# **********************************************************
# * Archivo: entorno_juego.py (actualizado)                *
# * Descripcion: Entorno principal. Ahora integra voz      *
# *              y carga niveles desde niveles.py           *
# **********************************************************

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AgenteIA.Entorno import Entorno
from juego.tablero_hexagonal import TableroHexagonal, EMOCIONES
from juego.agente_conexion import AgenteConexion
from juego.niveles import construir_nivel, DESCRIPCIONES_NIVEL
from juego.voz import GestorVoz

ESTADO_JUEGO = {
    "MENU":       "menu",
    "JUGANDO":    "jugando",
    "BUSCANDO":   "buscando",
    "ANIMANDO":   "animando",
    "COMPLETADO": "completado",
    "GAME_OVER":  "game_over",
}


class EntornoJuego(Entorno):

    def __init__(self):
        Entorno.__init__(self)
        self.tablero = None
        self.agente = None
        self.nivel_actual = 1
        self.nivel_maximo = 5
        self.tecnica_actual = "amplitud"
        self.estado = ESTADO_JUEGO["MENU"]
        self.emociones_pendientes = []
        self.emociones_completadas = []
        self.resultados_busqueda = {}
        self.emocion_activa = None
        self.frame_animacion = 0
        self.modo_tecnico = False
        self.puntuacion = 0
        self.mensaje_voz = ""

        # Gestor de voz (TTS + STT)
        self.voz = GestorVoz()

    # -----------------------------------------------------------
    # CARGA DE NIVEL
    # -----------------------------------------------------------
    def cargar_nivel(self, numero_nivel: int):
        self.nivel_actual = numero_nivel
        self.emociones_completadas = []
        self.resultados_busqueda = {}
        self.frame_animacion = 0
        self.emocion_activa = None

        self.tablero = construir_nivel(numero_nivel)
        self.agente = AgenteConexion(self.tablero)

        self.get_agentes().clear()
        self.insertar(self.agente)

        self.emociones_pendientes = list(self.tablero.personajes.keys())
        self.estado = ESTADO_JUEGO["JUGANDO"]

        print(f"✅ {DESCRIPCIONES_NIVEL[numero_nivel]}")
        print(f"   Emociones: {self.emociones_pendientes}")

        # Saludo de voz al cargar nivel
        if numero_nivel == 1:
            self.voz.saludo_inicial()
        else:
            self.voz.hablar(
                f"Nivel {numero_nivel}. "
                f"{len(self.emociones_pendientes)} emociones para conectar. Adelante!"
            )

    def siguiente_nivel(self):
        """Avanza al siguiente nivel si existe."""
        siguiente = self.nivel_actual + 1
        if siguiente <= self.nivel_maximo:
            self.cargar_nivel(siguiente)
        else:
            self.estado = ESTADO_JUEGO["COMPLETADO"]
            self.voz.hablar(
                "Felicitaciones! Completaste todos los niveles. "
                "Eres un maestro de las emociones!"
            )

    # -----------------------------------------------------------
    # METODOS ABSTRACTOS DEL DOCENTE
    # -----------------------------------------------------------
    def get_percepciones(self, agente):
        percepciones = {
            "tablero":        self.tablero,
            "emocion_activa": self.emocion_activa,
            "tecnica":        self.tecnica_actual,
            "estado_juego":   self.estado,
        }
        agente.set_percepciones(percepciones)

    def ejecutar(self, agente):
        if self.estado == ESTADO_JUEGO["BUSCANDO"]:
            self._ejecutar_busqueda()

    def finalizar(self):
        if self.estado == ESTADO_JUEGO["COMPLETADO"]:
            return True
        return any(not a.esta_habilitado() for a in self.get_agentes())

    # -----------------------------------------------------------
    # BUSQUEDA
    # -----------------------------------------------------------
    def iniciar_busqueda(self, emocion: str, tecnica: str):
        if emocion not in self.emociones_pendientes:
            return

        self.emocion_activa = emocion
        self.tecnica_actual = tecnica
        self.estado = ESTADO_JUEGO["BUSCANDO"]
        self.tablero.limpiar_busqueda()
        self.frame_animacion = 0

        # Narra la tecnica por voz
        self.voz.narrar_tecnica(tecnica)

    def _ejecutar_busqueda(self):
        if not self.emocion_activa:
            return

        pos_inicio = self.tablero.personajes.get(self.emocion_activa)
        pos_meta   = self.tablero.metas.get(self.emocion_activa)

        if not pos_inicio or not pos_meta:
            self.estado = ESTADO_JUEGO["JUGANDO"]
            return

        celda_inicio = self.tablero.get_celda(*pos_inicio)
        celda_meta   = self.tablero.get_celda(*pos_meta)

        camino = self.agente.buscar(celda_inicio, celda_meta, self.tecnica_actual)

        self.resultados_busqueda[self.emocion_activa] = {
            "camino":    camino,
            "costo":     self.agente.get_costo(camino) if camino else 0,
            "pasos":     len(camino),
            "historial": list(self.agente.historial_busqueda),
        }

        if not camino:
            self.voz.narrar_sin_camino(self.emocion_activa)
            self.emocion_activa = None
            self.estado = ESTADO_JUEGO["JUGANDO"]
            return

        self.estado = ESTADO_JUEGO["ANIMANDO"]
        self.frame_animacion = 0

    def avanzar_animacion(self) -> bool:
        if self.emocion_activa not in self.resultados_busqueda:
            return True

        historial = self.resultados_busqueda[self.emocion_activa]["historial"]

        if self.frame_animacion < len(historial):
            historial[self.frame_animacion].visitada = True
            self.frame_animacion += 1
            return False
        else:
            camino = self.resultados_busqueda[self.emocion_activa]["camino"]
            self.tablero.marcar_camino(camino)
            self._completar_conexion()
            return True

    def _completar_conexion(self):
        if self.emocion_activa:
            self.emociones_completadas.append(self.emocion_activa)
            self.emociones_pendientes.remove(self.emocion_activa)
            resultado = self.resultados_busqueda.get(self.emocion_activa, {})
            self.puntuacion += max(10, 50 - resultado.get("costo", 0))

            self.voz.narrar_exito(self.emocion_activa)
            self.emocion_activa = None

        if not self.emociones_pendientes:
            self.estado = ESTADO_JUEGO["COMPLETADO"]
            self.voz.narrar_nivel_completo()
        else:
            self.estado = ESTADO_JUEGO["JUGANDO"]

    # -----------------------------------------------------------
    # ESCUCHAR VOZ (STT)
    # -----------------------------------------------------------
    def activar_escucha(self):
        """Activa el microfono para que el niño diga como se siente."""
        def al_detectar(emocion, texto):
            if emocion and emocion in self.emociones_pendientes:
                self.iniciar_busqueda(emocion, self.tecnica_actual)
            elif emocion and emocion not in self.emociones_pendientes:
                self.voz.hablar(
                    f"La emocion {emocion} ya fue conectada. "
                    "Elige otra emocion del tablero."
                )

        self.voz.escuchar(callback=al_detectar)

    # -----------------------------------------------------------
    # CONTROLES
    # -----------------------------------------------------------
    def toggle_modo_tecnico(self):
        self.modo_tecnico = not self.modo_tecnico

    def cambiar_tecnica(self, tecnica: str):
        self.tecnica_actual = tecnica
        nombres = {
            "amplitud":      "Busqueda en Amplitud BFS",
            "profundidad":   "Busqueda en Profundidad DFS",
            "costouniforme": "Busqueda de Costo Uniforme",
        }
        self.voz.hablar(f"Tecnica cambiada a {nombres.get(tecnica, tecnica)}")

    # -----------------------------------------------------------
    # GETTERS
    # -----------------------------------------------------------
    def get_estado(self) -> str:
        return self.estado

    def get_tablero(self) -> TableroHexagonal:
        return self.tablero

    def get_resultado(self, emocion: str) -> dict:
        return self.resultados_busqueda.get(emocion, {})

    def cerrar(self):
        """Cierra recursos al salir del juego."""
        self.voz.cerrar()