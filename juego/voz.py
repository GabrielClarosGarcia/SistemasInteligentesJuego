# **********************************************************
# * Archivo: voz.py                                        *
# * Descripcion: Modulo de voz para Conexion Mental        *
# *              TTS (Texto a Voz) con pyttsx3 - offline   *
# *              STT (Voz a Texto) con SpeechRecognition   *
# **********************************************************

import threading
import queue
import time

# --- TTS ---
try:
    import pyttsx3
    TTS_DISPONIBLE = True
except ImportError:
    TTS_DISPONIBLE = False
    print("⚠️  pyttsx3 no instalado. TTS desactivado.")

# --- STT ---
try:
    import speech_recognition as sr
    STT_DISPONIBLE = True
except ImportError:
    STT_DISPONIBLE = False
    print("⚠️  SpeechRecognition no instalado. STT desactivado.")


# -----------------------------------------------------------
# CLASE GESTОР DE VOZ
# Maneja TTS y STT de forma no bloqueante usando hilos
# -----------------------------------------------------------
class GestorVoz:
    """
    Gestiona toda la funcionalidad de voz del juego.

    TTS (Texto a Voz):
      - Usa pyttsx3 (offline, sin internet)
      - Voz pausada y clara para niños
      - No bloquea el hilo principal de Pygame

    STT (Voz a Texto):
      - Usa SpeechRecognition con Google (online)
      - Fallback: muestra teclado si no hay internet
      - Detecta palabras clave emocionales
    """

    # Palabras clave que el STT reconoce y mapea a emociones
    PALABRAS_EMOCIONES = {
        "triste":    "tristeza",
        "tristeza":  "tristeza",
        "llorando":  "tristeza",
        "miedo":     "miedo",
        "asustado":  "miedo",
        "asustada":  "miedo",
        "enojado":   "enojo",
        "enojada":   "enojo",
        "enojo":     "enojo",
        "bravo":     "enojo",
        "feliz":     "alegria",
        "alegre":    "alegria",
        "alegria":   "alegria",
        "contento":  "alegria",
        "ansioso":   "ansiedad",
        "ansiosa":   "ansiedad",
        "ansiedad":  "ansiedad",
        "nervioso":  "ansiedad",
        "nerviosa":  "ansiedad",
    }

    def __init__(self):
        self.tts_engine = None
        self.tts_cola = queue.Queue()       # cola de mensajes a leer
        self.tts_hilo = None
        self.tts_activo = False
        self.voz_habilitada = True          # toggle para silenciar

        self.stt_escuchando = False
        self.ultimo_texto_reconocido = ""
        self.ultima_emocion_detectada = None
        self.callback_stt = None            # funcion a llamar cuando detecta emocion

        if TTS_DISPONIBLE:
            self._inicializar_tts()

    # -----------------------------------------------------------
    # TTS - TEXTO A VOZ
    # -----------------------------------------------------------
    def _inicializar_tts(self):
        """Inicializa el motor TTS con configuracion para niños."""
        try:
            self.tts_engine = pyttsx3.init()

            # Velocidad: 130 palabras/min (lento y claro para niños)
            self.tts_engine.setProperty("rate", 130)

            # Volumen al maximo
            self.tts_engine.setProperty("volume", 1.0)

            # Intenta usar voz en español si existe
            voces = self.tts_engine.getProperty("voices")
            for voz in voces:
                if "spanish" in voz.name.lower() or "es" in voz.id.lower():
                    self.tts_engine.setProperty("voice", voz.id)
                    break

            # Inicia hilo dedicado para TTS (no bloquea Pygame)
            self.tts_activo = True
            self.tts_hilo = threading.Thread(
                target=self._hilo_tts,
                daemon=True
            )
            self.tts_hilo.start()
            print("✅ TTS inicializado correctamente")

        except Exception as e:
            print(f"❌ Error inicializando TTS: {e}")
            self.tts_engine = None

    def _hilo_tts(self):
        """
        Hilo dedicado al TTS.
        Espera mensajes en la cola y los lee uno por uno.
        Corre en segundo plano para no bloquear Pygame.
        """
        while self.tts_activo:
            try:
                # Espera un mensaje con timeout para poder cerrar el hilo
                mensaje = self.tts_cola.get(timeout=0.5)
                if self.voz_habilitada and self.tts_engine:
                    self.tts_engine.say(mensaje)
                    self.tts_engine.runAndWait()
                self.tts_cola.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️  Error TTS: {e}")

    def hablar(self, texto: str, prioridad: bool = False):
        """
        Agrega un texto a la cola de TTS para ser leido.

        Parametros:
          texto     → el texto a leer en voz alta
          prioridad → si True, limpia la cola y lee este primero
        """
        if not TTS_DISPONIBLE or not self.voz_habilitada:
            print(f"[VOZ] {texto}")  # fallback: imprime en consola
            return

        if prioridad:
            # Limpia mensajes pendientes
            while not self.tts_cola.empty():
                try:
                    self.tts_cola.get_nowait()
                except queue.Empty:
                    break

        self.tts_cola.put(texto)

    def silenciar(self):
        """Detiene la voz y limpia la cola."""
        self.voz_habilitada = False
        while not self.tts_cola.empty():
            try:
                self.tts_cola.get_nowait()
            except queue.Empty:
                break
        print("🔇 Voz silenciada")

    def activar_voz(self):
        """Reactiva la voz."""
        self.voz_habilitada = True
        print("🔊 Voz activada")

    def toggle_voz(self):
        """Alterna entre voz activada y silenciada."""
        if self.voz_habilitada:
            self.silenciar()
        else:
            self.activar_voz()

    # -----------------------------------------------------------
    # STT - VOZ A TEXTO
    # -----------------------------------------------------------
    def escuchar(self, callback=None):
        """
        Inicia el reconocimiento de voz en un hilo separado.

        Parametros:
          callback → funcion(emocion, texto) llamada cuando detecta algo
        """
        if not STT_DISPONIBLE:
            print("⚠️  STT no disponible")
            return

        if self.stt_escuchando:
            print("⚠️  Ya estoy escuchando...")
            return

        self.callback_stt = callback
        hilo = threading.Thread(target=self._hilo_stt, daemon=True)
        hilo.start()
        self.hablar("Habla! Cuentame como te sientes")

    def _hilo_stt(self):
        """Hilo de reconocimiento de voz."""
        self.stt_escuchando = True
        reconocedor = sr.Recognizer()

        # Ajuste de sensibilidad para voces infantiles
        reconocedor.energy_threshold = 300
        reconocedor.pause_threshold = 1.0   # niños hacen pausas mas largas

        try:
            with sr.Microphone() as fuente:
                print("🎤 Escuchando...")
                # Ajusta al ruido ambiente
                reconocedor.adjust_for_ambient_noise(fuente, duration=0.5)

                # Escucha con timeout de 5 segundos
                audio = reconocedor.listen(fuente, timeout=5, phrase_time_limit=8)

            # Intenta reconocer con Google (online)
            try:
                texto = reconocedor.recognize_google(audio, language="es-ES")
                print(f"🎤 Reconocido: '{texto}'")
                self.ultimo_texto_reconocido = texto
                self._procesar_texto(texto)

            except sr.UnknownValueError:
                print("🎤 No entendí bien")
                self.hablar("No entendi bien, puedes repetirlo mas despacio?")
                if self.callback_stt:
                    self.callback_stt(None, "")

            except sr.RequestError:
                # Sin internet - fallback offline
                print("🎤 Sin internet, modo offline")
                self.hablar("No tengo conexion, usa los botones para elegir")
                if self.callback_stt:
                    self.callback_stt(None, "sin_conexion")

        except sr.WaitTimeoutError:
            print("🎤 Tiempo de espera agotado")
            self.hablar("Presiona el boton cuando quieras hablar")
            if self.callback_stt:
                self.callback_stt(None, "timeout")

        except Exception as e:
            print(f"❌ Error STT: {e}")
            if self.callback_stt:
                self.callback_stt(None, "error")

        finally:
            self.stt_escuchando = False

    def _procesar_texto(self, texto: str):
        """
        Busca palabras clave emocionales en el texto reconocido.
        Llama al callback con la emocion detectada.
        """
        texto_lower = texto.lower()
        emocion_detectada = None

        for palabra, emocion in self.PALABRAS_EMOCIONES.items():
            if palabra in texto_lower:
                emocion_detectada = emocion
                break

        self.ultima_emocion_detectada = emocion_detectada

        if emocion_detectada:
            print(f"💡 Emocion detectada: {emocion_detectada}")
            self.hablar(f"Escuche que te sientes con {emocion_detectada}. Busquemos tu camino!")
        else:
            self.hablar("Entendi lo que dijiste, pero no identifique una emocion clara.")

        if self.callback_stt:
            self.callback_stt(emocion_detectada, texto)

    # -----------------------------------------------------------
    # MENSAJES PREDEFINIDOS DEL JUEGO
    # Llamados desde entorno_juego.py o visualizador.py
    # -----------------------------------------------------------
    def saludo_inicial(self):
        self.hablar(
            "Hola! Soy Coco, tu guia en esta aventura. "
            "Ayudemos a nuestros amigos a encontrar su camino emocional.",
            prioridad=True
        )

    def narrar_tecnica(self, tecnica: str):
        """Explica la tecnica de busqueda en lenguaje para niños."""
        mensajes = {
            "amplitud": (
                "Usare la busqueda en amplitud. "
                "Exploraremos todos los caminos cercanos primero, "
                "como cuando miras a tu alrededor antes de dar un paso."
            ),
            "profundidad": (
                "Usare la busqueda en profundidad. "
                "Seguire un camino hasta el final. "
                "Si no funciona, regresamos e intentamos otro. Asi se aprende!"
            ),
            "costouniforme": (
                "Usare la busqueda de costo uniforme. "
                "Buscaremos el camino que requiera menos esfuerzo emocional. "
                "No todos los caminos son iguales."
            ),
        }
        texto = mensajes.get(tecnica, "Iniciando busqueda...")
        self.hablar(texto)

    def narrar_exito(self, emocion: str):
        """Felicita al niño cuando se completa una conexion."""
        mensajes = {
            "tristeza":  "Lo logramos! La tristeza encontro el juego. Como te sientes ahora?",
            "miedo":     "Muy bien! El miedo encontro su zona de calma. Eres muy valiente!",
            "enojo":     "Excelente! El enojo llego a la zona de abrazo. Un abrazo siempre ayuda.",
            "alegria":   "Fantastico! La alegria encontro a sus amigos. A celebrar!",
            "ansiedad":  "Lo lograste! La ansiedad llego a respiracion. Respira hondo con nosotros.",
        }
        self.hablar(mensajes.get(emocion, "Conexion completada! Muy bien!"), prioridad=True)

    def narrar_nivel_completo(self):
        self.hablar(
            "Increible! Conectaste todas las emociones con sus lugares especiales. "
            "Eres un experto en inteligencia emocional!",
            prioridad=True
        )

    def narrar_sin_camino(self, emocion: str):
        self.hablar(
            f"Hmm, no encontre un camino para {emocion} ahora. "
            "Hay demasiados obstaculos. Intentemos otra tecnica.",
            prioridad=True
        )

    def cerrar(self):
        """Cierra el motor TTS limpiamente al salir del juego."""
        self.tts_activo = False
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception:
                pass


# -----------------------------------------------------------
# TEST
# -----------------------------------------------------------
if __name__ == "__main__":
    print("=== TEST: Gestor de Voz ===\n")

    gestor = GestorVoz()

    print("--- Test TTS ---")
    gestor.saludo_inicial()
    time.sleep(4)

    gestor.narrar_tecnica("amplitud")
    time.sleep(5)

    gestor.narrar_exito("tristeza")
    time.sleep(4)

    print("\n--- Test deteccion de palabras ---")
    # Simula texto reconocido
    gestor._procesar_texto("estoy muy triste porque mi amigo no quiso jugar")
    time.sleep(3)

    gestor._procesar_texto("tengo miedo de la oscuridad")
    time.sleep(3)

    print(f"\nUltima emocion detectada: {gestor.ultima_emocion_detectada}")

    print("\n--- Test toggle voz ---")
    gestor.toggle_voz()   # silencia
    gestor.hablar("esto no deberia escucharse")
    time.sleep(1)
    gestor.toggle_voz()   # reactiva
    gestor.hablar("y esto si deberia escucharse")
    time.sleep(3)

    gestor.cerrar()
    print("\n✅ Gestor de voz funcionando")