# **********************************************************
# * Archivo: entorno_juego.py                              *
# * Descripcion: Flujo rediseñado con asistente Coco       *
# *   - Coco sugiere UN solo paso en cualquier momento     *
# *   - Usa el algoritmo seleccionado para calcular        *
# **********************************************************

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AgenteIA.Entorno import Entorno
from tablero_hexagonal import TableroHexagonal, construir_nivel, DESCRIPCIONES_NIVEL
from agente_conexion import AgenteConexion
from voz import GestorVoz

ST = {
    "MENU":           "menu",
    "SELECCIONAR":    "seleccionar",
    "JUGADOR_TRAZA":  "jugador_traza",
    "RESUMEN_NIVEL":  "resumen_nivel",
    "DEMO_ALGORITMO": "demo_algoritmo",
    "ENTRE_DEMOS":    "entre_demos",
    "NIVEL_COMPLETO": "nivel_completo",
}


class EntornoJuego(Entorno):

    def __init__(self):
        Entorno.__init__(self)
        self.tablero  = None
        self.agente   = None
        self.voz      = GestorVoz()

        self.nivel_actual   = 1
        self.nivel_maximo   = 5
        self.tecnica_actual = "amplitud"
        self.estado         = ST["MENU"]
        self.puntuacion     = 0
        self.modo_tecnico   = False

        self.emociones_pendientes  = []
        self.emociones_completadas = []

        # Turno del jugador
        self.emocion_activa  = None
        self.celda_activa    = None
        self.camino_jugador  = []

        # Resultados
        self.resultados_jugador = {}

        # Demos al final
        self.demos_pendientes = []
        self.demo_actual      = None
        self.camino_algoritmo = []
        self.historial_algo   = []
        self.frame_animacion  = 0
        self.step_ms          = 55

        # --- COCO ---
        self.coco_celda_sugerida  = None   # Celda que Coco recomienda
        self.coco_mensaje         = ""     # Texto que Coco dice
        self.coco_visible         = False  # Si mostrar la sugerencia ahora
        self.coco_usos            = 0      # Cuantas veces pidio ayuda

    # -----------------------------------------------------------
    # CARGA DE NIVEL
    # -----------------------------------------------------------
    def cargar_nivel(self, n: int):
        self.nivel_actual          = n
        self.emociones_pendientes  = []
        self.emociones_completadas = []
        self.resultados_jugador    = {}
        self.demos_pendientes      = []
        self.demo_actual           = None
        self.puntuacion            = 0
        self.coco_usos             = 0
        self._reset_turno()
        self._reset_coco()

        self.tablero = construir_nivel(n)
        self.agente  = AgenteConexion(self.tablero)
        self.get_agentes().clear()
        self.insertar(self.agente)

        self.emociones_pendientes = list(self.tablero.personajes.keys())
        self.estado = ST["SELECCIONAR"]

        print(f"✅ {DESCRIPCIONES_NIVEL[n]}")
        if n == 1:
            self.voz.saludo_inicial()
        else:
            self.voz.hablar(
                f"Nivel {n}. {len(self.emociones_pendientes)} emociones. Adelante!")

    def _reset_turno(self):
        self.emocion_activa = None
        self.celda_activa   = None
        self.camino_jugador = []
        self._reset_coco()
        if self.tablero:
            self.tablero.limpiar_busqueda()
            self.tablero.limpiar_camino_jugador()

    def _reset_coco(self):
        """Limpia la sugerencia de Coco."""
        if self.tablero and self.coco_celda_sugerida:
            # Quita el marcado de la celda sugerida anterior
            self.coco_celda_sugerida.es_sugerencia = False
        self.coco_celda_sugerida = None
        self.coco_mensaje        = ""
        self.coco_visible        = False

    def siguiente_nivel(self):
        nxt = self.nivel_actual + 1
        if nxt <= self.nivel_maximo:
            self.cargar_nivel(nxt)
        else:
            self.estado = ST["NIVEL_COMPLETO"]
            self.voz.narrar_nivel_completo()

    # -----------------------------------------------------------
    # METODOS DEL DOCENTE
    # -----------------------------------------------------------
    def get_percepciones(self, agente):
        agente.set_percepciones({
            "tablero": self.tablero,
            "emocion": self.emocion_activa,
            "tecnica": self.tecnica_actual,
        })

    def ejecutar(self, agente):
        pass

    def finalizar(self):
        return self.estado == ST["NIVEL_COMPLETO"]

    # -----------------------------------------------------------
    # FASE 1: EL NIÑO TRAZA CAMINOS
    # -----------------------------------------------------------
    def seleccionar_emocion(self, emocion: str):
        if emocion not in self.emociones_pendientes:
            return
        self._reset_turno()
        self.emocion_activa = emocion
        pos = self.tablero.personajes[emocion]
        self.celda_activa   = self.tablero.get_celda(*pos)
        self.camino_jugador = [self.celda_activa]
        self.estado = ST["JUGADOR_TRAZA"]
        self.voz.narrar_turno_jugador(emocion)

    def intentar_mover_jugador(self, q: int, r: int):
        if self.estado != ST["JUGADOR_TRAZA"] or not self.celda_activa:
            return

        destino = self.tablero.get_celda(q, r)
        if not destino or not destino.es_transitable():
            return

        if not self.tablero.son_vecinos(
                self.celda_activa.q, self.celda_activa.r, q, r):
            self.voz.narrar_celda_invalida()
            return

        # Retroceder
        if len(self.camino_jugador) >= 2 and destino == self.camino_jugador[-2]:
            self.camino_jugador[-1].en_camino_jugador = False
            self.camino_jugador.pop()
            self.celda_activa = self.camino_jugador[-1]
            self._reset_coco()   # limpia sugerencia al retroceder
            return

        # Avanzar
        destino.en_camino_jugador = True
        self.camino_jugador.append(destino)
        self.celda_activa = destino
        self._reset_coco()       # limpia sugerencia al avanzar

        # Llego a la meta?
        meta_pos = self.tablero.metas.get(self.emocion_activa)
        if meta_pos and (destino.q, destino.r) == meta_pos:
            self._jugador_completo_emocion()

    def _jugador_completo_emocion(self):
        em    = self.emocion_activa
        pasos = len(self.camino_jugador)

        self.resultados_jugador[em] = {
            "pasos_jugador":  pasos,
            "camino_jugador": list(self.camino_jugador),
            "usos_coco":      self.coco_usos,
        }
        self.emociones_completadas.append(em)
        self.emociones_pendientes.remove(em)
        self.puntuacion += max(5, 20 - pasos)

        self.voz.hablar(
            f"Muy bien! Conectaste {em} en {pasos} pasos. "
            + ("Elige la siguiente emocion!"
               if self.emociones_pendientes
               else "Completaste todas las emociones!")
        )

        self._reset_turno()

        if self.emociones_pendientes:
            self.estado = ST["SELECCIONAR"]
        else:
            self.estado = ST["RESUMEN_NIVEL"]
            self.voz.hablar(
                "Excelente! Resolviste todo. "
                "Presiona ESPACIO para ver las soluciones del algoritmo!",
                prioridad=True
            )

    # -----------------------------------------------------------
    # COCO — SUGERENCIA DE UN PASO
    # -----------------------------------------------------------
    def pedir_ayuda_coco(self):
        """
        Calcula el siguiente paso óptimo desde la posición actual del jugador
        usando el algoritmo seleccionado, y lo marca como sugerencia.
        Disponible en SELECCIONAR y JUGADOR_TRAZA.
        """
        self._reset_coco()

        # En SELECCIONAR: sugiere qué emocion atacar primero
        if self.estado == ST["SELECCIONAR"]:
            if self.emociones_pendientes:
                sugerida = self.emociones_pendientes[0]
                self.coco_mensaje = (
                    f"Coco dice: Empieza con '{sugerida}'. "
                    f"Haz clic en ese personaje!"
                )
                self.voz.hablar(
                    f"Te sugiero empezar con {sugerida}. Busca ese personaje!",
                    prioridad=True
                )
                # Resalta la celda del personaje sugerido
                pos = self.tablero.personajes.get(sugerida)
                if pos:
                    celda = self.tablero.get_celda(*pos)
                    if celda:
                        celda.es_sugerencia = True
                        self.coco_celda_sugerida = celda
                self.coco_visible = True
                self.coco_usos   += 1
            return

        # En JUGADOR_TRAZA: calcula el camino óptimo y sugiere el siguiente paso
        if self.estado != ST["JUGADOR_TRAZA"] or not self.celda_activa:
            self.voz.hablar("Primero selecciona una emocion para que pueda ayudarte!")
            return

        meta_pos = self.tablero.metas.get(self.emocion_activa)
        if not meta_pos:
            return

        celda_meta = self.tablero.get_celda(*meta_pos)

        # Ejecuta el algoritmo desde la posición ACTUAL del jugador
        camino_optimo = self.agente.buscar(
            self.celda_activa,
            celda_meta,
            self.tecnica_actual
        )
        # Limpia los marcadores que deja la búsqueda (no queremos mostrarlos)
        self.tablero.limpiar_busqueda()

        if not camino_optimo or len(camino_optimo) < 2:
            self.coco_mensaje = "Coco dice: ¡Ya casi llegas! Un paso más."
            self.voz.hablar("Ya casi llegas! Un paso mas!", prioridad=True)
            self.coco_visible = True
            return

        # El siguiente paso es el segundo elemento del camino
        # (el primero es la celda actual)
        siguiente = camino_optimo[1]
        siguiente.es_sugerencia = True
        self.coco_celda_sugerida = siguiente

        nombres_tecnica = {
            "amplitud":      "BFS",
            "profundidad":   "DFS",
            "costouniforme": "Costo Uniforme",
        }
        nombre_tec = nombres_tecnica.get(self.tecnica_actual, self.tecnica_actual)

        pasos_restantes = len(camino_optimo) - 1
        self.coco_mensaje = (
            f"Coco ({nombre_tec}): Ve hacia ({siguiente.q}, {siguiente.r}). "
            f"Faltan ~{pasos_restantes} pasos."
        )
        self.voz.hablar(
            f"Coco sugiere: muevete hacia la celda resaltada. "
            f"Faltan aproximadamente {pasos_restantes} pasos usando {nombre_tec}.",
            prioridad=True
        )
        self.coco_visible = True
        self.coco_usos   += 1

    # -----------------------------------------------------------
    # FASE 2: DEMOS DEL ALGORITMO AL FINAL
    # -----------------------------------------------------------
    def iniciar_demos(self):
        self.demos_pendientes = list(self.emociones_completadas)
        self.tablero.limpiar_busqueda()
        self.tablero.limpiar_camino_jugador()
        self._lanzar_siguiente_demo()

    def _lanzar_siguiente_demo(self):
        if not self.demos_pendientes:
            self.estado = ST["NIVEL_COMPLETO"]
            self._comparar_resultados()
            return

        self.demo_actual = self.demos_pendientes.pop(0)
        self.tablero.limpiar_busqueda()

        pos_i = self.tablero.personajes[self.demo_actual]
        pos_m = self.tablero.metas[self.demo_actual]
        ci    = self.tablero.get_celda(*pos_i)
        cm    = self.tablero.get_celda(*pos_m)

        camino = self.agente.buscar(ci, cm, self.tecnica_actual)
        self.camino_algoritmo = camino
        self.historial_algo   = list(self.agente.historial_busqueda)
        self.frame_animacion  = 0
        self.estado = ST["DEMO_ALGORITMO"]

        pj = self.resultados_jugador.get(
            self.demo_actual, {}).get("pasos_jugador", "?")
        self.voz.hablar(
            f"Solucion para {self.demo_actual}. "
            f"Tu usaste {pj} pasos. El algoritmo usara {len(camino)}. Observa!"
        )

    def avanzar_animacion_algoritmo(self) -> bool:
        if self.frame_animacion < len(self.historial_algo):
            self.historial_algo[self.frame_animacion].visitada = True
            self.frame_animacion += 1
            return False
        else:
            self.tablero.marcar_camino(self.camino_algoritmo)
            pj = self.resultados_jugador.get(
                self.demo_actual, {}).get("pasos_jugador", 0)
            pa = len(self.camino_algoritmo)
            self.voz.narrar_exito_algoritmo(self.demo_actual, pj, pa)
            self.estado = ST["ENTRE_DEMOS"]
            return True

    def confirmar_siguiente_demo(self):
        self._lanzar_siguiente_demo()

    def _comparar_resultados(self):
        mejores = sum(
            1 for em, res in self.resultados_jugador.items()
            if res["pasos_jugador"] <= len(
                self.agente.buscar(
                    self.tablero.get_celda(*self.tablero.personajes[em]),
                    self.tablero.get_celda(*self.tablero.metas[em]),
                    self.tecnica_actual
                )
            )
        )
        total = len(self.resultados_jugador)
        if mejores == total:
            self.voz.hablar(
                "Increible! Encontraste el camino optimo en todas. Eres un genio! "
                "Presiona N para el siguiente nivel.", prioridad=True)
        else:
            self.voz.hablar(
                f"Muy bien! Superaste al algoritmo en {mejores} de {total}. "
                "Sigue practicando! Presiona N para el siguiente nivel.",
                prioridad=True)

    # -----------------------------------------------------------
    # CONTROLES
    # -----------------------------------------------------------
    def toggle_modo_tecnico(self):
        self.modo_tecnico = not self.modo_tecnico

    def cambiar_tecnica(self, tecnica: str):
        self.tecnica_actual = tecnica
        nombres = {
            "amplitud":      "BFS Amplitud",
            "profundidad":   "DFS Profundidad",
            "costouniforme": "Costo Uniforme",
        }
        self.voz.hablar(f"Algoritmo: {nombres.get(tecnica, tecnica)}")
        # Si Coco tenia una sugerencia activa, la recalcula con la nueva tecnica
        if self.coco_visible:
            self.pedir_ayuda_coco()

    # -----------------------------------------------------------
    # GETTERS
    # -----------------------------------------------------------
    def get_estado(self):  return self.estado
    def get_tablero(self): return self.tablero

    def cerrar(self):
        self.voz.cerrar()