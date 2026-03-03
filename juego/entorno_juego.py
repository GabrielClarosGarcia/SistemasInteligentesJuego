# **********************************************************
# * Archivo: entorno_juego.py                              *
# * Descripcion: Entorno del juego. Extiende Entorno del   *
# *              docente. Conecta tablero + agente +        *
# *              logica del juego                          *
# **********************************************************

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AgenteIA.Entorno import Entorno
from juego.tablero_hexagonal import TableroHexagonal, construir_nivel_1, EMOCIONES
from juego.agente_conexion import AgenteConexion


# -----------------------------------------------------------
# ESTADOS DEL JUEGO
# El juego pasa por diferentes fases durante su ejecucion
# -----------------------------------------------------------
ESTADO_JUEGO = {
    "MENU":        "menu",
    "JUGANDO":     "jugando",
    "BUSCANDO":    "buscando",    # algoritmo corriendo
    "ANIMANDO":    "animando",    # mostrando animacion
    "COMPLETADO":  "completado",  # nivel terminado
    "GAME_OVER":   "game_over",
}


class EntornoJuego(Entorno):
    """
    Entorno principal del juego Conexion Mental.
    Extiende Entorno del docente e implementa:
      - get_percepciones(): que ve el agente
      - ejecutar(): que hace el agente con lo que percibe
    
    Tambien gestiona:
      - El nivel actual y su tablero
      - La tecnica de busqueda seleccionada
      - El estado del juego (menu, jugando, etc.)
      - Los resultados de las busquedas
    """

    def __init__(self):
        Entorno.__init__(self)
        self.tablero = None
        self.agente = None
        self.nivel_actual = 1
        self.tecnica_actual = "amplitud"       # BFS por defecto
        self.estado = ESTADO_JUEGO["MENU"]
        self.emociones_pendientes = []         # emociones que faltan conectar
        self.emociones_completadas = []        # emociones ya conectadas
        self.resultados_busqueda = {}          # caminos encontrados
        self.emocion_activa = None             # emocion que se esta buscando ahora
        self.frame_animacion = 0               # frame actual de la animacion
        self.velocidad_animacion = 10          # frames entre cada paso
        self.modo_tecnico = False              # toggle: vista nino vs vista tecnica
        self.puntuacion = 0
        self.mensaje_voz = ""                  # texto que dira el TTS

    # -----------------------------------------------------------
    # INICIALIZACION DEL NIVEL
    # -----------------------------------------------------------
    def cargar_nivel(self, numero_nivel: int):
        """Carga el tablero y configura el agente para el nivel dado."""
        self.nivel_actual = numero_nivel
        self.emociones_completadas = []
        self.resultados_busqueda = {}
        self.frame_animacion = 0

        # Por ahora solo tenemos nivel 1
        # Luego importaremos mas niveles desde niveles.py
        if numero_nivel == 1:
            self.tablero = construir_nivel_1()

        # Crea el agente con el tablero del nivel
        self.agente = AgenteConexion(self.tablero)

        # Registra el agente en el entorno (metodo del docente)
        # Limpia agentes anteriores primero
        self.get_agentes().clear()
        self.insertar(self.agente)

        # Las emociones pendientes son todas las que estan en el tablero
        self.emociones_pendientes = list(self.tablero.personajes.keys())

        self.estado = ESTADO_JUEGO["JUGANDO"]
        print(f" Nivel {numero_nivel} cargado")
        print(f"   Emociones a conectar: {self.emociones_pendientes}")

    # -----------------------------------------------------------
    # IMPLEMENTACION DE METODOS ABSTRACTOS DEL DOCENTE
    # -----------------------------------------------------------
    def get_percepciones(self, agente):
        """
        Implementa metodo abstracto del docente.
        Le da al agente la informacion que necesita:
          - Tablero actual
          - Emocion que debe conectar ahora
          - Tecnica de busqueda seleccionada
        """
        percepciones = {
            "tablero":        self.tablero,
            "emocion_activa": self.emocion_activa,
            "tecnica":        self.tecnica_actual,
            "estado_juego":   self.estado,
        }
        agente.set_percepciones(percepciones)

    def ejecutar(self, agente):
        """
        Implementa metodo abstracto del docente.
        Ejecuta la accion del agente segun el estado del juego.
        """
        if self.estado == ESTADO_JUEGO["BUSCANDO"]:
            self._ejecutar_busqueda()

    def finalizar(self):
        """
        Sobreescribe finalizar del docente.
        El juego termina cuando todas las emociones estan conectadas
        o cuando el agente es deshabilitado.
        """
        if self.estado == ESTADO_JUEGO["COMPLETADO"]:
            return True
        return any(not a.esta_habilitado() for a in self.get_agentes())

    # -----------------------------------------------------------
    # LOGICA DE BUSQUEDA
    # -----------------------------------------------------------
    def iniciar_busqueda(self, emocion: str, tecnica: str):
        """
        Inicia la busqueda para una emocion especifica.
        Llamado cuando el jugador selecciona una emocion y tecnica.
        """
        if emocion not in self.emociones_pendientes:
            print(f"  Emocion '{emocion}' ya completada o no existe")
            return

        self.emocion_activa = emocion
        self.tecnica_actual = tecnica
        self.estado = ESTADO_JUEGO["BUSCANDO"]
        self.tablero.limpiar_busqueda()
        self.frame_animacion = 0

        # Genera el mensaje de voz segun la tecnica
        self.mensaje_voz = self._generar_mensaje_tecnica(tecnica)
        print(f" Iniciando busqueda: {emocion} con {tecnica}")

    def _ejecutar_busqueda(self):
        """Ejecuta la busqueda y guarda el resultado para animacion."""
        if not self.emocion_activa:
            return

        pos_inicio = self.tablero.personajes.get(self.emocion_activa)
        pos_meta   = self.tablero.metas.get(self.emocion_activa)

        if not pos_inicio or not pos_meta:
            print(f" No hay inicio o meta para {self.emocion_activa}")
            self.estado = ESTADO_JUEGO["JUGANDO"]
            return

        celda_inicio = self.tablero.get_celda(*pos_inicio)
        celda_meta   = self.tablero.get_celda(*pos_meta)

        # Ejecuta el algoritmo (BFS, DFS, etc.)
        camino = self.agente.buscar(celda_inicio, celda_meta, self.tecnica_actual)

        # Guarda resultado
        self.resultados_busqueda[self.emocion_activa] = {
            "camino":   camino,
            "costo":    self.agente.get_costo(camino) if camino else 0,
            "pasos":    len(camino),
            "historial": list(self.agente.historial_busqueda),
        }

        # Cambia a estado de animacion
        self.estado = ESTADO_JUEGO["ANIMANDO"]
        self.frame_animacion = 0

    def avanzar_animacion(self) -> bool:
        """
        Avanza un frame en la animacion de busqueda.
        Retorna True si la animacion termino, False si sigue.
        Llamado por el visualizador cada frame de Pygame.
        """
        if self.emocion_activa not in self.resultados_busqueda:
            return True

        historial = self.resultados_busqueda[self.emocion_activa]["historial"]
        total_frames = len(historial)

        if self.frame_animacion < total_frames:
            # Marca la celda actual como visitada visualmente
            celda = historial[self.frame_animacion]
            celda.visitada = True
            self.frame_animacion += 1
            return False
        else:
            # Animacion terminada, marca el camino final
            camino = self.resultados_busqueda[self.emocion_activa]["camino"]
            self.tablero.marcar_camino(camino)
            self._completar_conexion()
            return True

    def _completar_conexion(self):
        """Marca una emocion como conectada y verifica si el nivel termino."""
        if self.emocion_activa:
            self.emociones_completadas.append(self.emocion_activa)
            self.emociones_pendientes.remove(self.emocion_activa)
            self.puntuacion += 10

            resultado = self.resultados_busqueda.get(self.emocion_activa, {})
            print(f" Conexion completada: {self.emocion_activa}")
            print(f"   Pasos: {resultado.get('pasos', 0)}")
            print(f"   Costo: {resultado.get('costo', 0)}")

            self.mensaje_voz = self._generar_mensaje_exito(self.emocion_activa)
            self.emocion_activa = None

        # Verifica si todas las emociones fueron conectadas
        if not self.emociones_pendientes:
            self.estado = ESTADO_JUEGO["COMPLETADO"]
            print(f" Nivel {self.nivel_actual} completado!")
        else:
            self.estado = ESTADO_JUEGO["JUGANDO"]

    # -----------------------------------------------------------
    # MENSAJES DE VOZ
    # Textos que el TTS leerá en cada momento del juego
    # -----------------------------------------------------------
    def _generar_mensaje_tecnica(self, tecnica: str) -> str:
        mensajes = {
            "amplitud": (
                "Voy a explorar todos los caminos cercanos primero, "
                "como cuando miras a tu alrededor antes de decidir."
            ),
            "profundidad": (
                "Voy a seguir un camino hasta el final. "
                "Si no funciona, regresamos e intentamos otro."
            ),
            "costouniforme": (
                "Buscaremos el camino que requiera menos esfuerzo emocional. "
                "No todos los caminos son iguales."
            ),
        }
        return mensajes.get(tecnica, "Iniciando búsqueda...")

    def _generar_mensaje_exito(self, emocion: str) -> str:
        mensajes = {
            "tristeza":  "¡Lo logramos! Conectamos la tristeza con el juego. ¿Cómo te sientes ahora?",
            "miedo":     "¡Muy bien! El miedo encontró su zona de calma. ¡Eres muy valiente!",
            "enojo":     "¡Excelente! El enojo llegó a la zona de abrazo. Un abrazo siempre ayuda.",
            "alegria":   "¡Fantástico! La alegría encontró a sus amigos. ¡A celebrar!",
            "ansiedad":  "¡Lo lograste! La ansiedad llegó a respiración. Respira hondo con nosotros.",
        }
        return mensajes.get(emocion, "¡Conexión completada!")

    # -----------------------------------------------------------
    # GETTERS UTILES PARA EL VISUALIZADOR
    # -----------------------------------------------------------
    def get_estado(self) -> str:
        return self.estado

    def get_tablero(self) -> TableroHexagonal:
        return self.tablero

    def get_resultado(self, emocion: str) -> dict:
        return self.resultados_busqueda.get(emocion, {})

    def toggle_modo_tecnico(self):
        self.modo_tecnico = not self.modo_tecnico
        modo = "TÉCNICO" if self.modo_tecnico else "NIÑO"
        print(f" Modo cambiado a: {modo}")

    def cambiar_tecnica(self, tecnica: str):
        self.tecnica_actual = tecnica
        print(f"  Técnica cambiada a: {tecnica}")


# -----------------------------------------------------------
# TEST
# -----------------------------------------------------------
if __name__ == "__main__":
    print("=== TEST: Entorno Juego ===\n")

    entorno = EntornoJuego()
    entorno.cargar_nivel(1)

    print(f"\nEstado inicial: {entorno.get_estado()}")
    print(f"Emociones pendientes: {entorno.emociones_pendientes}")

    # Simula busqueda con BFS
    print("\n--- Simulando BFS para tristeza ---")
    entorno.iniciar_busqueda("tristeza", "amplitud")
    entorno.evolucionar()  # llama get_percepciones + ejecutar del docente

    resultado = entorno.get_resultado("tristeza")
    if resultado:
        print(f"Pasos: {resultado['pasos']}")
        print(f"Costo: {resultado['costo']}")
        print(f"Mensaje voz: {entorno.mensaje_voz}")

    # Simula animacion completa
    print("\n--- Simulando animacion ---")
    while entorno.get_estado() == ESTADO_JUEGO["ANIMANDO"]:
        termino = entorno.avanzar_animacion()
        if termino:
            break

    print(f"\nEstado final: {entorno.get_estado()}")
    print(f"Emociones completadas: {entorno.emociones_completadas}")
    print(f"Puntuacion: {entorno.puntuacion}")

    # Simula busqueda con Costo Uniforme para alegria
    print("\n--- Simulando Costo Uniforme para alegria ---")
    entorno.iniciar_busqueda("alegria", "costouniforme")
    entorno.evolucionar()
    while entorno.get_estado() == ESTADO_JUEGO["ANIMANDO"]:
        if entorno.avanzar_animacion():
            break

    print(f"Estado final: {entorno.get_estado()}")
    print(f"Puntuacion final: {entorno.puntuacion}")

    print("\n Entorno funcionando correctamente")