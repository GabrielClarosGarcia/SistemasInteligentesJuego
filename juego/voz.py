# **********************************************************
# * Archivo: voz.py                                        *
# * Descripcion: Solo TTS (pyttsx3, offline).              *
# *              STT desactivado para evitar errores       *
# *              de PyAudio en Windows.                    *
# **********************************************************

import threading
import queue

try:
    import pyttsx3
    _TTS_OK = True
except ImportError:
    _TTS_OK = False
    print("⚠️  pyttsx3 no instalado: pip install pyttsx3")


class GestorVoz:

    def __init__(self):
        self.habilitada  = True
        self._cola       = queue.Queue()
        self._engine     = None
        self._activo     = False
        self.stt_escuchando = False   # siempre False, solo para compatibilidad UI

        if _TTS_OK:
            self._init_engine()

    def _init_engine(self):
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate",   130)   # lento para niños
            self._engine.setProperty("volume", 1.0)

            # Busca voz en español
            for v in self._engine.getProperty("voices"):
                if "spanish" in v.name.lower() or "es_" in v.id.lower():
                    self._engine.setProperty("voice", v.id)
                    break

            self._activo = True
            t = threading.Thread(target=self._loop, daemon=True)
            t.start()
            print("✅ TTS listo")
        except Exception as e:
            print(f"⚠️  TTS error: {e}")
            self._engine = None

    def _loop(self):
        while self._activo:
            try:
                texto = self._cola.get(timeout=0.5)
                if self.habilitada and self._engine:
                    self._engine.say(texto)
                    self._engine.runAndWait()
                self._cola.task_done()
            except queue.Empty:
                continue
            except Exception:
                pass

    # -----------------------------------------------------------
    # API PUBLICA
    # -----------------------------------------------------------
    def hablar(self, texto: str, prioridad: bool = False):
        """Encola un mensaje para ser leido en voz alta."""
        if not _TTS_OK or not self.habilitada:
            print(f"[VOZ] {texto}")
            return
        if prioridad:
            self._vaciar_cola()
        self._cola.put(texto)

    def _vaciar_cola(self):
        while not self._cola.empty():
            try:
                self._cola.get_nowait()
            except queue.Empty:
                break

    def toggle_voz(self):
        self.habilitada = not self.habilitada
        estado = "activada" if self.habilitada else "silenciada"
        print(f"🔊 Voz {estado}")
        if self.habilitada:
            self.hablar("Voz activada")

    def cerrar(self):
        self._activo = False
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass

    # -----------------------------------------------------------
    # MENSAJES DEL JUEGO
    # -----------------------------------------------------------
    def saludo_inicial(self):
        self.hablar(
            "Hola! Soy Coco, tu guia. "
            "Haz clic en el personaje y traza tu camino hasta la estacion. "
            "Luego el algoritmo te mostrara la mejor ruta!",
            prioridad=True
        )

    def narrar_tecnica(self, tecnica: str):
        msgs = {
            "amplitud":      "Modo demostracion: Busqueda en Amplitud. Exploro nivel por nivel.",
            "profundidad":   "Modo demostracion: Busqueda en Profundidad. Sigo un camino hasta el final.",
            "costouniforme": "Modo demostracion: Costo Uniforme. Busco el camino mas economico.",
        }
        self.hablar(msgs.get(tecnica, "Buscando..."))

    def narrar_turno_jugador(self, emocion: str):
        self.hablar(
            f"Tu turno! Ayuda a {emocion} a llegar a su estacion. "
            "Haz clic en los hexagonos vecinos para trazar el camino.",
            prioridad=True
        )

    def narrar_exito_jugador(self, emocion: str, pasos: int):
        self.hablar(
            f"Excelente! Conectaste {emocion} en {pasos} pasos. "
            "Ahora mira como lo hace el algoritmo!",
            prioridad=True
        )

    def narrar_exito_algoritmo(self, emocion: str, pasos_jugador: int, pasos_algo: int):
        if pasos_jugador == pasos_algo:
            self.hablar(
                f"Increible! Encontraste el camino optimo igual que el algoritmo. "
                f"{pasos_algo} pasos. Eres un genio!",
                prioridad=True
            )
        elif pasos_jugador < pasos_algo:
            self.hablar(
                f"Sorprendente! Tu camino de {pasos_jugador} pasos es mejor "
                f"que el algoritmo con {pasos_algo}. Eres muy inteligente!",
                prioridad=True
            )
        else:
            self.hablar(
                f"El algoritmo encontro un camino de {pasos_algo} pasos. "
                f"Tu usaste {pasos_jugador}. Intenta de nuevo para mejorar!",
                prioridad=True
            )

    def narrar_celda_invalida(self):
        self.hablar("Solo puedes moverte a celdas vecinas!")

    def narrar_nivel_completo(self):
        self.hablar(
            "Felicitaciones! Conectaste todas las emociones. "
            "Eres un experto en inteligencia emocional!",
            prioridad=True
        )

    def narrar_exito(self, emocion: str):
        msgs = {
            "tristeza":  "La tristeza llego al juego. Como te sientes ahora?",
            "miedo":     "El miedo encontro calma. Muy valiente!",
            "enojo":     "El enojo llego al abrazo. Un abrazo siempre ayuda.",
            "alegria":   "La alegria encontro amigos. A celebrar!",
            "ansiedad":  "La ansiedad llego a respiracion. Respira hondo!",
        }
        self.hablar(msgs.get(emocion, "Conexion completada!"), prioridad=True)