# **********************************************************
# * Archivo: niveles.py                                    *
# * Descripcion: Definicion de los 5 niveles del juego     *
# *              Cada nivel tiene diferente complejidad     *
# **********************************************************

from tablero_hexagonal import TableroHexagonal


def construir_nivel_1() -> TableroHexagonal:
    """
    Nivel 1 - Introduccion
    Dos emociones simples, pocos obstaculos, caminos amplios.
    Ideal para aprender BFS.
    """
    t = TableroHexagonal(8, 8)

    # Obstaculos simples
    for q, r in [(2, 2), (2, 3), (5, 3), (5, 4)]:
        t.set_tipo(q, r, "obstaculo")

    # Bosques (costo 2)
    for q, r in [(1, 3), (4, 4), (3, 3)]:
        t.set_tipo(q, r, "bosque")

    # Montanas (costo 3)
    for q, r in [(4, 2), (3, 4)]:
        t.set_tipo(q, r, "montana")

    # Personajes
    t.colocar_emocion("tristeza", 0, 0)
    t.colocar_emocion("alegria",  0, 5)

    # Estaciones
    t.colocar_estacion("juego",   7, 1)
    t.colocar_estacion("amigos",  7, 6)

    return t


def construir_nivel_2() -> TableroHexagonal:
    """
    Nivel 2 - Tres emociones
    Mas obstaculos, zonas de miedo para motivar Costo Uniforme.
    """
    t = TableroHexagonal(8, 8)

    # Obstaculos formando un laberinto simple
    for q, r in [(2, 1), (2, 2), (2, 3), (4, 4), (4, 5), (6, 2), (6, 3)]:
        t.set_tipo(q, r, "obstaculo")

    # Zonas de miedo (costo 4) — hay que rodearlas
    for q, r in [(3, 2), (5, 3), (1, 4)]:
        t.set_tipo(q, r, "miedo")

    # Bosques
    for q, r in [(1, 2), (3, 5), (5, 1), (4, 3)]:
        t.set_tipo(q, r, "bosque")

    # Montanas
    for q, r in [(3, 1), (6, 5)]:
        t.set_tipo(q, r, "montana")

    # Personajes (3 emociones)
    t.colocar_emocion("tristeza", 0, 0)
    t.colocar_emocion("miedo",    0, 3)
    t.colocar_emocion("alegria",  0, 6)

    # Estaciones
    t.colocar_estacion("juego",   7, 0)
    t.colocar_estacion("calma",   7, 3)
    t.colocar_estacion("amigos",  7, 6)

    return t


def construir_nivel_3() -> TableroHexagonal:
    """
    Nivel 3 - Cuatro emociones, laberinto medio
    Introduce zonas de miedo en rutas principales.
    Motiva comparar DFS vs BFS vs Uniforme.
    """
    t = TableroHexagonal(8, 8)

    # Laberinto con pasillos
    obstaculos = [
        (2, 0), (2, 1), (2, 2),         # pared izquierda
        (2, 4), (2, 5), (2, 6),
        (5, 1), (5, 2),                  # pared derecha
        (5, 5), (5, 6),
        (3, 3),                          # centro bloqueado
    ]
    for q, r in obstaculos:
        t.set_tipo(q, r, "obstaculo")

    # Zonas de miedo en los pasillos clave
    for q, r in [(3, 1), (3, 5), (4, 3), (1, 3)]:
        t.set_tipo(q, r, "miedo")

    # Bosques
    for q, r in [(1, 1), (4, 2), (6, 3), (3, 6), (4, 5)]:
        t.set_tipo(q, r, "bosque")

    # Montanas
    for q, r in [(4, 1), (1, 5), (6, 5)]:
        t.set_tipo(q, r, "montana")

    # Personajes (4 emociones)
    t.colocar_emocion("tristeza", 0, 0)
    t.colocar_emocion("miedo",    0, 2)
    t.colocar_emocion("enojo",    0, 5)
    t.colocar_emocion("alegria",  0, 7)

    # Estaciones
    t.colocar_estacion("juego",   7, 0)
    t.colocar_estacion("calma",   7, 2)
    t.colocar_estacion("abrazo",  7, 5)
    t.colocar_estacion("amigos",  7, 7)

    return t


def construir_nivel_4() -> TableroHexagonal:
    """
    Nivel 4 - Cinco emociones, laberinto complejo
    Muchas zonas de miedo. Costo Uniforme brilla aqui.
    Hay rutas cortas pero caras y rutas largas pero baratas.
    """
    t = TableroHexagonal(8, 8)

    # Laberinto denso
    obstaculos = [
        (1, 2), (1, 3),
        (3, 0), (3, 1), (3, 2),
        (3, 5), (3, 6), (3, 7),
        (5, 1), (5, 2), (5, 3),
        (5, 5), (5, 6),
        (6, 4),
    ]
    for q, r in obstaculos:
        t.set_tipo(q, r, "obstaculo")

    # Zonas de miedo estrategicas (bloquean rutas directas)
    for q, r in [(2, 1), (2, 4), (4, 2), (4, 5), (6, 2), (6, 6)]:
        t.set_tipo(q, r, "miedo")

    # Bosques
    for q, r in [(1, 1), (2, 3), (4, 4), (5, 0), (6, 7), (1, 6)]:
        t.set_tipo(q, r, "bosque")

    # Montanas (rutas alternativas costosas)
    for q, r in [(2, 6), (4, 1), (6, 3)]:
        t.set_tipo(q, r, "montana")

    # Cinco emociones
    t.colocar_emocion("tristeza", 0, 0)
    t.colocar_emocion("miedo",    0, 2)
    t.colocar_emocion("enojo",    0, 4)
    t.colocar_emocion("alegria",  0, 6)
    t.colocar_emocion("ansiedad", 0, 7)

    # Cinco estaciones
    t.colocar_estacion("juego",       7, 0)
    t.colocar_estacion("calma",       7, 2)
    t.colocar_estacion("abrazo",      7, 4)
    t.colocar_estacion("amigos",      7, 6)
    t.colocar_estacion("respiracion", 7, 7)

    return t


def construir_nivel_5() -> TableroHexagonal:
    """
    Nivel 5 - Desafio final
    Tablero 10x10, todas las emociones, laberinto complejo.
    Demuestra diferencias claras entre los 3 algoritmos.
    """
    t = TableroHexagonal(10, 10)

    # Laberinto con multiples zonas
    obstaculos = [
        # Pared vertical izquierda con hueco
        (2, 0), (2, 1), (2, 2), (2, 3),
        (2, 5), (2, 6), (2, 7), (2, 8),
        # Pared vertical derecha con hueco
        (6, 1), (6, 2), (6, 3),
        (6, 5), (6, 6), (6, 7), (6, 8),
        # Centro
        (4, 4), (4, 5),
        (5, 3), (5, 4),
    ]
    for q, r in obstaculos:
        t.set_tipo(q, r, "obstaculo")

    # Muchas zonas de miedo
    miedos = [(3, 2), (3, 6), (5, 1), (5, 7), (7, 3), (7, 6), (1, 4), (4, 2), (4, 7)]
    for q, r in miedos:
        t.set_tipo(q, r, "miedo")

    # Bosques
    bosques = [(1, 1), (3, 4), (5, 5), (7, 1), (8, 5), (1, 7), (3, 8), (7, 8)]
    for q, r in bosques:
        t.set_tipo(q, r, "bosque")

    # Montanas
    montanas = [(4, 1), (5, 6), (8, 3), (1, 8), (6, 4)]
    for q, r in montanas:
        t.set_tipo(q, r, "montana")

    # Cinco emociones distribuidas verticalmente
    t.colocar_emocion("tristeza", 0, 0)
    t.colocar_emocion("miedo",    0, 2)
    t.colocar_emocion("enojo",    0, 5)
    t.colocar_emocion("alegria",  0, 7)
    t.colocar_emocion("ansiedad", 0, 9)

    # Cinco estaciones al otro lado
    t.colocar_estacion("juego",       9, 0)
    t.colocar_estacion("calma",       9, 2)
    t.colocar_estacion("abrazo",      9, 5)
    t.colocar_estacion("amigos",      9, 7)
    t.colocar_estacion("respiracion", 9, 9)

    return t


# -----------------------------------------------------------
# Mapa de niveles — usado por entorno_juego.py
# -----------------------------------------------------------
NIVELES = {
    1: construir_nivel_1,
    2: construir_nivel_2,
    3: construir_nivel_3,
    4: construir_nivel_4,
    5: construir_nivel_5,
}

DESCRIPCIONES_NIVEL = {
    1: "Nivel 1 - Introduccion: 2 emociones, caminos simples",
    2: "Nivel 2 - Exploracion: 3 emociones, zonas de miedo",
    3: "Nivel 3 - Laberinto: 4 emociones, pasillos estrechos",
    4: "Nivel 4 - Desafio: 5 emociones, rutas costosas",
    5: "Nivel 5 - Final: tablero grande, todas las emociones",
}


def construir_nivel(numero: int) -> TableroHexagonal:
    """Fabrica que retorna el tablero del nivel indicado."""
    constructor = NIVELES.get(numero)
    if constructor is None:
        raise ValueError(f"Nivel {numero} no existe. Niveles disponibles: 1-5")
    return constructor()


# -----------------------------------------------------------
# TEST
# -----------------------------------------------------------
if __name__ == "__main__":
    print("=== TEST: Niveles ===\n")

    for n in range(1, 6):
        t = construir_nivel(n)
        print(f"{DESCRIPCIONES_NIVEL[n]}")
        print(f"  Celdas: {len(t.celdas)}")
        print(f"  Personajes: {list(t.personajes.keys())}")
        print(f"  Estaciones: {list(t.metas.keys())}")

        obstaculos = sum(1 for c in t.celdas.values() if c.tipo == "obstaculo")
        miedos     = sum(1 for c in t.celdas.values() if c.tipo == "miedo")
        print(f"  Obstaculos: {obstaculos} | Zonas miedo: {miedos}\n")

    print("✅ Todos los niveles construidos correctamente")