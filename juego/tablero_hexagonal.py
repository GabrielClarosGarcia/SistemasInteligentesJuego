# **********************************************************
# * Archivo: tablero_hexagonal.py                          *
# * Descripcion: Logica del tablero hexagonal              *
# *              Sistema de coordenadas axiales (q, r)     *
# **********************************************************

# ¿Qué son las coordenadas axiales (q, r)?
# En un tablero hexagonal cada celda tiene dos coordenadas:
#   q → columna (eje horizontal)
#   r → fila (eje vertical)
# Cada celda tiene exactamente 6 vecinos, siempre los mismos offsets

# -----------------------------------------------------------
# TIPOS DE CELDA
# Cada celda del tablero puede ser de un tipo diferente
# El tipo define el costo emocional de atravesarla
# -----------------------------------------------------------
TIPOS_CELDA = {
    "libre":      {"costo": 1, "color": (200, 220, 200), "nombre": "Camino libre"},
    "bosque":     {"costo": 2, "color": (34, 139, 34),   "nombre": "Bosque"},
    "montana":    {"costo": 3, "color": (139, 90, 43),   "nombre": "Montaña"},
    "miedo":      {"costo": 4, "color": (80, 0, 80),     "nombre": "Zona de Miedo"},
    "obstaculo":  {"costo": 999, "color": (50, 50, 50),  "nombre": "Obstáculo"},
}

# -----------------------------------------------------------
# EMOCIONES Y ESTACIONES
# Cada emocion tiene un color y debe conectarse a una estacion
# -----------------------------------------------------------
EMOCIONES = {
    "tristeza":  {"color": (70, 130, 180),  "estacion": "juego",       "emoji": "😢"},
    "miedo":     {"color": (147, 112, 219), "estacion": "calma",       "emoji": "😨"},
    "enojo":     {"color": (220, 50, 50),   "estacion": "abrazo",      "emoji": "😠"},
    "alegria":   {"color": (255, 215, 0),   "estacion": "amigos",      "emoji": "😊"},
    "ansiedad":  {"color": (50, 180, 50),   "estacion": "respiracion", "emoji": "😰"},
}

ESTACIONES = {
    "juego":       {"color": (100, 200, 255), "nombre": "Zona de Juego"},
    "calma":       {"color": (200, 150, 255), "nombre": "Zona de Calma"},
    "abrazo":      {"color": (255, 150, 150), "nombre": "Zona de Abrazo"},
    "amigos":      {"color": (255, 230, 100), "nombre": "Zona de Amigos"},
    "respiracion": {"color": (150, 255, 150), "nombre": "Zona de Respiración"},
}

# -----------------------------------------------------------
# CLASE CELDA
# Representa una celda individual del tablero
# -----------------------------------------------------------
class Celda:
    def __init__(self, q, r, tipo="libre"):
        self.q = q                  # coordenada columna
        self.r = r                  # coordenada fila
        self.tipo = tipo            # tipo de terreno
        self.emocion = None         # si hay un personaje aqui
        self.estacion = None        # si es una estacion de bienestar
        self.es_inicio = False      # marcador visual
        self.visitada = False       # para animacion de busqueda
        self.en_camino = False      # para mostrar el camino final

    def get_costo(self):
        # Si es obstáculo, costo muy alto (no se puede pasar)
        return TIPOS_CELDA[self.tipo]["costo"]

    def es_transitable(self):
        # Solo las celdas no obstáculo son transitables
        return self.tipo != "obstaculo"

    def get_color(self):
        # El color depende del tipo de celda
        # Si tiene estacion, usa el color de la estacion
        if self.estacion:
            return ESTACIONES[self.estacion]["color"]
        # Si tiene emocion (personaje), usa el color de la emocion
        if self.emocion:
            return EMOCIONES[self.emocion]["color"]
        return TIPOS_CELDA[self.tipo]["color"]

    def __eq__(self, other):
        # Dos celdas son iguales si tienen las mismas coordenadas
        if isinstance(other, Celda):
            return self.q == other.q and self.r == other.r
        return False

    def __hash__(self):
        # Necesario para usar celdas en conjuntos y diccionarios
        return hash((self.q, self.r))

    def __repr__(self):
        return f"Celda({self.q}, {self.r}, {self.tipo})"


# -----------------------------------------------------------
# CLASE TABLERO HEXAGONAL
# Contiene todas las celdas y la lógica de navegación
# -----------------------------------------------------------
class TableroHexagonal:

    # Los 6 vecinos posibles en coordenadas axiales
    # Estos offsets son SIEMPRE los mismos para cualquier celda
    DIRECCIONES = [
        (+1,  0),   # derecha
        (-1,  0),   # izquierda
        ( 0, +1),   # abajo-derecha
        ( 0, -1),   # arriba-izquierda
        (+1, -1),   # arriba-derecha
        (-1, +1),   # abajo-izquierda
    ]

    def __init__(self, filas=8, columnas=8):
        self.filas = filas
        self.columnas = columnas
        self.celdas = {}        # diccionario (q,r) -> Celda
        self.personajes = {}    # emocion -> (q,r) posicion del personaje
        self.metas = {}         # emocion -> (q,r) posicion de la estacion meta
        self._construir_tablero()

    def _construir_tablero(self):
        # Crea todas las celdas del tablero
        for r in range(self.filas):
            for q in range(self.columnas):
                self.celdas[(q, r)] = Celda(q, r, "libre")

    def get_celda(self, q, r):
        # Retorna la celda en (q,r) o None si no existe
        return self.celdas.get((q, r), None)

    def set_tipo(self, q, r, tipo):
        # Cambia el tipo de una celda
        celda = self.get_celda(q, r)
        if celda:
            celda.tipo = tipo

    def colocar_emocion(self, emocion, q, r):
        # Coloca un personaje emocional en una celda
        celda = self.get_celda(q, r)
        if celda:
            celda.emocion = emocion
            self.personajes[emocion] = (q, r)

    def colocar_estacion(self, nombre_estacion, q, r):
        # Coloca una estacion de bienestar en una celda
        celda = self.get_celda(q, r)
        if celda:
            celda.estacion = nombre_estacion
            # Registra qué emocion debe ir a esta estacion
            for emocion, datos in EMOCIONES.items():
                if datos["estacion"] == nombre_estacion:
                    self.metas[emocion] = (q, r)

    def get_vecinos(self, q, r):
        # Retorna todas las celdas vecinas transitables
        vecinos = []
        for dq, dr in self.DIRECCIONES:
            nq, nr = q + dq, r + dr
            celda = self.get_celda(nq, nr)
            if celda and celda.es_transitable():
                vecinos.append(celda)
        return vecinos

    def distancia_hexagonal(self, q1, r1, q2, r2):
        # Distancia entre dos celdas en tablero hexagonal
        # Formula estandar para coordenadas axiales
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

    def limpiar_busqueda(self):
        # Resetea marcadores visuales de busqueda anterior
        for celda in self.celdas.values():
            celda.visitada = False
            celda.en_camino = False

    def marcar_camino(self, camino):
        # Marca las celdas del camino encontrado
        for celda in camino:
            celda.en_camino = True

    def __repr__(self):
        return f"TableroHexagonal({self.columnas}x{self.filas})"


# -----------------------------------------------------------
# FUNCION: construir nivel
# Crea un tablero con un layout predefinido para un nivel
# -----------------------------------------------------------
def construir_nivel_1():
    tablero = TableroHexagonal(8, 8)

    # Colocar obstáculos
    obstaculos = [(2,2), (2,3), (3,5), (5,2), (5,3), (6,5)]
    for q, r in obstaculos:
        tablero.set_tipo(q, r, "obstaculo")

    # Colocar terrenos con costo variable
    bosques = [(1,3), (4,4), (3,3)]
    for q, r in bosques:
        tablero.set_tipo(q, r, "bosque")

    montanas = [(4,2), (3,4)]
    for q, r in montanas:
        tablero.set_tipo(q, r, "montana")

    miedos = [(1,5), (6,3)]
    for q, r in miedos:
        tablero.set_tipo(q, r, "miedo")

    # Colocar personajes (emociones)
    tablero.colocar_emocion("tristeza", 0, 0)
    tablero.colocar_emocion("alegria",  0, 4)

    # Colocar estaciones de bienestar
    tablero.colocar_estacion("juego",   7, 1)
    tablero.colocar_estacion("amigos",  7, 6)

    return tablero


# -----------------------------------------------------------
# TEST: verificar que todo funciona (ejecutar este archivo)
# -----------------------------------------------------------
if __name__ == "__main__":
    print("=== TEST: Tablero Hexagonal ===\n")

    tablero = construir_nivel_1()
    print(f"Tablero creado: {tablero}")
    print(f"Total de celdas: {len(tablero.celdas)}")

    # Test: obtener celda
    celda = tablero.get_celda(0, 0)
    print(f"\nCelda (0,0): {celda}")
    print(f"  Tipo: {celda.tipo}")
    print(f"  Emocion: {celda.emocion}")
    print(f"  Costo: {celda.get_costo()}")

    # Test: vecinos de (0,0)
    vecinos = tablero.get_vecinos(0, 0)
    print(f"\nVecinos de (0,0): {vecinos}")

    # Test: distancia hexagonal
    d = tablero.distancia_hexagonal(0, 0, 7, 1)
    print(f"\nDistancia de (0,0) a (7,1): {d}")

    # Test: personajes y metas registrados
    print(f"\nPersonajes: {tablero.personajes}")
    print(f"Metas: {tablero.metas}")

    # Test: vecinos de celda con obstáculos cerca
    vecinos2 = tablero.get_vecinos(2, 1)
    print(f"\nVecinos de (2,1) evitando obstáculos: {vecinos2}")

    print("\n✅ Tablero hexagonal funcionando correctamente")