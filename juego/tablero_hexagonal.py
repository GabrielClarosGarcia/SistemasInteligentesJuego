# **********************************************************
# * Archivo: tablero_hexagonal.py                          *
# * Descripcion: Tablero hexagonal (forma de panal)        *
# *              Coordenadas axiales q+r+s=0               *
# **********************************************************

TIPOS_CELDA = {
    "libre":     {"costo": 1,   "color": (210, 225, 210)},
    "bosque":    {"costo": 2,   "color": (34,  139, 34)},
    "montana":   {"costo": 3,   "color": (139, 90,  43)},
    "miedo":     {"costo": 4,   "color": (80,  0,   80)},
    "obstaculo": {"costo": 999, "color": (50,  50,  50)},
}

EMOCIONES = {
    "tristeza": {"color": (70,  130, 180), "estacion": "juego"},
    "miedo":    {"color": (147, 112, 219), "estacion": "calma"},
    "enojo":    {"color": (220, 50,  50),  "estacion": "abrazo"},
    "alegria":  {"color": (255, 215, 0),   "estacion": "amigos"},
    "ansiedad": {"color": (50,  180, 50),  "estacion": "respiracion"},
}

ESTACIONES = {
    "juego":       {"color": (100, 200, 255), "nombre": "Zona de Juego"},
    "calma":       {"color": (200, 150, 255), "nombre": "Zona de Calma"},
    "abrazo":      {"color": (255, 150, 150), "nombre": "Zona de Abrazo"},
    "amigos":      {"color": (255, 230, 100), "nombre": "Zona de Amigos"},
    "respiracion": {"color": (150, 255, 150), "nombre": "Zona de Respiracion"},
}

DIRECCIONES_HEX = [(+1,0),(-1,0),(0,+1),(0,-1),(+1,-1),(-1,+1)]


class Celda:
    def __init__(self, q, r, tipo="libre"):
        self.q = q
        self.r = r
        self.s = -q - r
        self.tipo      = tipo
        self.emocion   = None
        self.estacion  = None
        # Marcadores visuales
        self.visitada          = False   # explorada por el algoritmo
        self.en_camino         = False   # camino final del algoritmo
        self.en_camino_jugador = False   # camino trazado por el niño
        self.es_sugerencia     = False   # sugerencia de Coco

    def get_costo(self):
        return TIPOS_CELDA[self.tipo]["costo"]

    def es_transitable(self):
        return self.tipo != "obstaculo"

    def get_color(self):
        if self.estacion:
            return ESTACIONES[self.estacion]["color"]
        if self.emocion:
            return EMOCIONES[self.emocion]["color"]
        return TIPOS_CELDA[self.tipo]["color"]

    def __eq__(self, other):
        return isinstance(other, Celda) and self.q == other.q and self.r == other.r

    def __hash__(self):
        return hash((self.q, self.r))

    def __repr__(self):
        return f"Celda({self.q},{self.r},{self.tipo})"


class TableroHexagonal:
    def __init__(self, radio=4):
        self.radio      = radio
        self.celdas     = {}
        self.personajes = {}
        self.metas      = {}
        self._construir()

    def _construir(self):
        for q in range(-self.radio, self.radio + 1):
            for r in range(-self.radio, self.radio + 1):
                s = -q - r
                if abs(q) <= self.radio and abs(r) <= self.radio and abs(s) <= self.radio:
                    self.celdas[(q, r)] = Celda(q, r)

    def get_celda(self, q, r):
        return self.celdas.get((q, r))

    def set_tipo(self, q, r, tipo):
        c = self.get_celda(q, r)
        if c: c.tipo = tipo

    def colocar_emocion(self, emocion, q, r):
        c = self.get_celda(q, r)
        if c:
            c.emocion = emocion
            self.personajes[emocion] = (q, r)

    def colocar_estacion(self, nombre, q, r):
        c = self.get_celda(q, r)
        if c:
            c.estacion = nombre
            for em, datos in EMOCIONES.items():
                if datos["estacion"] == nombre:
                    self.metas[em] = (q, r)

    def get_vecinos(self, q, r):
        vecinos = []
        for dq, dr in DIRECCIONES_HEX:
            c = self.get_celda(q+dq, r+dr)
            if c and c.es_transitable():
                vecinos.append(c)
        return vecinos

    def distancia(self, q1, r1, q2, r2):
        return (abs(q1-q2) + abs(q1+r1-q2-r2) + abs(r1-r2)) // 2

    def limpiar_busqueda(self):
        for c in self.celdas.values():
            c.visitada  = False
            c.en_camino = False

    def limpiar_camino_jugador(self):
        for c in self.celdas.values():
            c.en_camino_jugador = False
            c.es_sugerencia     = False   # tambien limpia sugerencias

    def marcar_camino(self, camino):
        for c in camino:
            c.en_camino = True

    def son_vecinos(self, q1, r1, q2, r2):
        return (q2-q1, r2-r1) in DIRECCIONES_HEX


# -----------------------------------------------------------
# NIVELES
# -----------------------------------------------------------

def construir_nivel_1() -> TableroHexagonal:
    t = TableroHexagonal(radio=4)
    for q, r in [(-1,-2),(0,-3),(1,-3),(-2,1),(2,-1)]:
        t.set_tipo(q, r, "obstaculo")
    for q, r in [(-1,1),(1,-2),(0,2)]:
        t.set_tipo(q, r, "bosque")
    t.colocar_emocion("tristeza", -3, 0)
    t.colocar_estacion("juego",    3, 0)
    return t

def construir_nivel_2() -> TableroHexagonal:
    t = TableroHexagonal(radio=4)
    for q, r in [(0,-2),(0,-1),(0,0),(0,1)]:
        t.set_tipo(q, r, "obstaculo")
    for q, r in [(-2,1),(2,-1),(-1,-2),(1,2)]:
        t.set_tipo(q, r, "bosque")
    for q, r in [(-1,2),(1,-2)]:
        t.set_tipo(q, r, "montana")
    t.colocar_emocion("tristeza", -3,  1)
    t.colocar_emocion("alegria",  -3, -1)
    t.colocar_estacion("juego",    3, -1)
    t.colocar_estacion("amigos",   3,  1)
    return t

def construir_nivel_3() -> TableroHexagonal:
    t = TableroHexagonal(radio=4)
    for q, r in [(-1,-3),(-1,-2),(-1,0),(-1,1),(-1,2)]:
        t.set_tipo(q, r, "obstaculo")
    for q, r in [(1,-2),(1,-1),(1,1),(1,2),(1,3)]:
        t.set_tipo(q, r, "obstaculo")
    for q, r in [(-2,1),(2,-1),(0,-2),(0,2)]:
        t.set_tipo(q, r, "miedo")
    for q, r in [(-2,-1),(2,1),(-1,3),(1,-3)]:
        t.set_tipo(q, r, "bosque")
    t.colocar_emocion("tristeza", -3,  2)
    t.colocar_emocion("miedo",    -3,  0)
    t.colocar_emocion("alegria",  -3, -2)
    t.colocar_estacion("juego",    3, -2)
    t.colocar_estacion("calma",    3,  0)
    t.colocar_estacion("amigos",   3,  2)
    return t

def construir_nivel_4() -> TableroHexagonal:
    t = TableroHexagonal(radio=4)
    for q, r in [(-2,-1),(-2,0),(-2,1),(0,-3),(0,-2),(0,2),(0,3),(2,-1),(2,0),(2,1)]:
        t.set_tipo(q, r, "obstaculo")
    for q, r in [(-1,-2),(1,2),(-1,2),(1,-2)]:
        t.set_tipo(q, r, "miedo")
    for q, r in [(0,-1),(0,0),(0,1),(-3,1),(3,-1)]:
        t.set_tipo(q, r, "bosque")
    t.colocar_emocion("tristeza", -3,  2)
    t.colocar_emocion("miedo",    -4,  1)
    t.colocar_emocion("enojo",    -4, -1)
    t.colocar_emocion("alegria",  -3, -2)
    t.colocar_estacion("juego",    3, -2)
    t.colocar_estacion("calma",    4, -1)
    t.colocar_estacion("abrazo",   4,  1)
    t.colocar_estacion("amigos",   3,  2)
    return t

def construir_nivel_5() -> TableroHexagonal:
    t = TableroHexagonal(radio=5)
    for q, r in [(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),
                 (0,-4),(0,-3),(0,3),(0,4),
                 (2,-2),(2,-1),(2,0),(2,1),(2,2)]:
        t.set_tipo(q, r, "obstaculo")
    for q, r in [(-3,1),(3,-1),(-1,-3),(1,3),(-1,3),(1,-3)]:
        t.set_tipo(q, r, "miedo")
    for q, r in [(0,-1),(0,0),(0,1),(-4,2),(4,-2)]:
        t.set_tipo(q, r, "bosque")
    for q, r in [(-1,-1),(1,1),(-1,2),(1,-2)]:
        t.set_tipo(q, r, "montana")
    t.colocar_emocion("tristeza", -4,  3)
    t.colocar_emocion("miedo",    -5,  2)
    t.colocar_emocion("enojo",    -5,  0)
    t.colocar_emocion("alegria",  -5, -2)
    t.colocar_emocion("ansiedad", -4, -3)
    t.colocar_estacion("juego",       4, -3)
    t.colocar_estacion("calma",       5, -2)
    t.colocar_estacion("abrazo",      5,  0)
    t.colocar_estacion("amigos",      5,  2)
    t.colocar_estacion("respiracion", 4,  3)
    return t


NIVELES = {1: construir_nivel_1, 2: construir_nivel_2, 3: construir_nivel_3,
           4: construir_nivel_4, 5: construir_nivel_5}

DESCRIPCIONES_NIVEL = {
    1: "Nivel 1 - Introduccion: 1 emocion",
    2: "Nivel 2 - Exploracion: 2 emociones",
    3: "Nivel 3 - Laberinto: 3 emociones",
    4: "Nivel 4 - Desafio: 4 emociones",
    5: "Nivel 5 - Final: 5 emociones, tablero grande",
}

def construir_nivel(numero: int) -> TableroHexagonal:
    fn = NIVELES.get(numero)
    if not fn: raise ValueError(f"Nivel {numero} no existe")
    return fn()