# **********************************************************
# * Archivo: sprites.py                                    *
# * Descripcion: Caras emocionales, estaciones y           *
# *              dibujos para obstaculos y terrenos        *
# **********************************************************

import pygame
import math


# -----------------------------------------------------------
# CARAS EMOCIONALES
# -----------------------------------------------------------
def dibujar_cara_tristeza(screen, cx, cy, r):
    pygame.draw.circle(screen, (70, 130, 180), (cx, cy), r)
    pygame.draw.circle(screen, (40, 90, 140), (cx, cy), r, 2)
    pygame.draw.circle(screen, (10,10,40), (cx-r//3, cy-r//5), r//6)
    pygame.draw.circle(screen, (10,10,40), (cx+r//3, cy-r//5), r//6)
    pygame.draw.line(screen, (10,10,40), (cx-r//2, cy-r//2), (cx-r//8, cy-r//3), 2)
    pygame.draw.line(screen, (10,10,40), (cx+r//8, cy-r//3), (cx+r//2, cy-r//2), 2)
    pts = [(cx - r//2 + int(r*t), cy + r//4 + int((r//4)*math.sin(t*math.pi)))
           for t in [i/10 for i in range(11)]]
    if len(pts) > 1:
        pygame.draw.lines(screen, (10,10,40), False, pts, 2)
    pygame.draw.circle(screen, (150, 210, 255), (cx+r//3, cy+r//6), r//8)


def dibujar_cara_miedo(screen, cx, cy, r):
    pygame.draw.circle(screen, (147, 112, 219), (cx, cy), r)
    pygame.draw.circle(screen, (90, 60, 160), (cx, cy), r, 2)
    pygame.draw.circle(screen, (255,255,255), (cx-r//3, cy-r//5), r//4)
    pygame.draw.circle(screen, (255,255,255), (cx+r//3, cy-r//5), r//4)
    pygame.draw.circle(screen, (10,10,40), (cx-r//3, cy-r//5), r//8)
    pygame.draw.circle(screen, (10,10,40), (cx+r//3, cy-r//5), r//8)
    pygame.draw.arc(screen, (10,10,40), pygame.Rect(cx-r//2, cy-r//2-4, r//3, r//4), 0, math.pi, 2)
    pygame.draw.arc(screen, (10,10,40), pygame.Rect(cx+r//8, cy-r//2-4, r//3, r//4), 0, math.pi, 2)
    pygame.draw.ellipse(screen, (10,10,40), pygame.Rect(cx-r//4, cy+r//6, r//2, r//3))


def dibujar_cara_enojo(screen, cx, cy, r):
    pygame.draw.circle(screen, (220, 50, 50), (cx, cy), r)
    pygame.draw.circle(screen, (160, 20, 20), (cx, cy), r, 2)
    pygame.draw.circle(screen, (10,10,10), (cx-r//3, cy-r//5), r//6)
    pygame.draw.circle(screen, (10,10,10), (cx+r//3, cy-r//5), r//6)
    pygame.draw.line(screen, (10,10,10), (cx-r//2, cy-r//2), (cx-r//8, cy-r//3), 3)
    pygame.draw.line(screen, (10,10,10), (cx+r//8, cy-r//3), (cx+r//2, cy-r//2), 3)
    pygame.draw.line(screen, (10,10,10), (cx-r//3, cy+r//4), (cx+r//3, cy+r//4), 3)
    pygame.draw.line(screen, (180,20,20), (cx-r+4, cy), (cx-r//2, cy+r//4), 2)
    pygame.draw.line(screen, (180,20,20), (cx+r//2, cy+r//4), (cx+r-4, cy), 2)


def dibujar_cara_alegria(screen, cx, cy, r):
    pygame.draw.circle(screen, (255, 215, 0), (cx, cy), r)
    pygame.draw.circle(screen, (200, 160, 0), (cx, cy), r, 2)
    pygame.draw.arc(screen, (10,10,10), pygame.Rect(cx-r//2, cy-r//3, r//3, r//4), math.pi, 2*math.pi, 2)
    pygame.draw.arc(screen, (10,10,10), pygame.Rect(cx+r//8, cy-r//3, r//3, r//4), math.pi, 2*math.pi, 2)
    pygame.draw.arc(screen, (10,10,10), pygame.Rect(cx-r//2, cy, r, r//2), math.pi, 2*math.pi, 3)
    pygame.draw.circle(screen, (255,180,180), (cx-r//2, cy+r//5), r//6)
    pygame.draw.circle(screen, (255,180,180), (cx+r//2, cy+r//5), r//6)


def dibujar_cara_ansiedad(screen, cx, cy, r):
    pygame.draw.circle(screen, (50, 180, 50), (cx, cy), r)
    pygame.draw.circle(screen, (20, 120, 20), (cx, cy), r, 2)
    pygame.draw.circle(screen, (255,255,255), (cx-r//3, cy-r//5), r//5)
    pygame.draw.circle(screen, (255,255,255), (cx+r//3, cy-r//5), r//4)
    pygame.draw.circle(screen, (10,10,10), (cx-r//3, cy-r//5), r//9)
    pygame.draw.circle(screen, (10,10,10), (cx+r//3, cy-r//5), r//9)
    pts = [(cx-r//3, cy+r//4),(cx-r//6, cy+r//6),(cx, cy+r//4),
           (cx+r//6, cy+r//6),(cx+r//3, cy+r//4)]
    pygame.draw.lines(screen, (10,10,10), False, pts, 2)
    pygame.draw.circle(screen, (150,230,150), (cx-r+6, cy-r//3), r//8)


CARAS = {
    "tristeza": dibujar_cara_tristeza,
    "miedo":    dibujar_cara_miedo,
    "enojo":    dibujar_cara_enojo,
    "alegria":  dibujar_cara_alegria,
    "ansiedad": dibujar_cara_ansiedad,
}


# -----------------------------------------------------------
# ESTACIONES
# -----------------------------------------------------------
def dibujar_estacion_juego(screen, cx, cy, r):
    pygame.draw.circle(screen, (100, 200, 255), (cx, cy), r)
    pygame.draw.circle(screen, (50, 140, 200), (cx, cy), r, 2)
    _estrella(screen, cx, cy-2, r//2, 5, (255,255,255))

def dibujar_estacion_calma(screen, cx, cy, r):
    pygame.draw.circle(screen, (200, 150, 255), (cx, cy), r)
    pygame.draw.circle(screen, (140, 90, 200), (cx, cy), r, 2)
    for i in range(3):
        pygame.draw.circle(screen, (255,255,255), (cx, cy), r//4 + i*(r//5), 2)

def dibujar_estacion_abrazo(screen, cx, cy, r):
    pygame.draw.circle(screen, (255, 150, 150), (cx, cy), r)
    pygame.draw.circle(screen, (200, 80, 80), (cx, cy), r, 2)
    _corazon(screen, cx, cy, r//2, (255,255,255))

def dibujar_estacion_amigos(screen, cx, cy, r):
    pygame.draw.circle(screen, (255, 230, 100), (cx, cy), r)
    pygame.draw.circle(screen, (200, 170, 30), (cx, cy), r, 2)
    s = r // 3
    for dx in [-s, s]:
        pygame.draw.circle(screen, (255,255,255), (cx+dx, cy-s//2), s//2)
        pygame.draw.line(screen, (255,255,255), (cx+dx, cy), (cx+dx, cy+s), 2)

def dibujar_estacion_respiracion(screen, cx, cy, r):
    pygame.draw.circle(screen, (150, 255, 150), (cx, cy), r)
    pygame.draw.circle(screen, (80, 190, 80), (cx, cy), r, 2)
    for i in range(6):
        a = i * math.pi / 3
        px = cx + int((r//2)*math.cos(a))
        py = cy + int((r//2)*math.sin(a))
        pygame.draw.circle(screen, (255,255,255), (px, py), r//5)
    pygame.draw.circle(screen, (255,255,200), (cx, cy), r//5)

ESTACIONES_DRAW = {
    "juego":       dibujar_estacion_juego,
    "calma":       dibujar_estacion_calma,
    "abrazo":      dibujar_estacion_abrazo,
    "amigos":      dibujar_estacion_amigos,
    "respiracion": dibujar_estacion_respiracion,
}


# -----------------------------------------------------------
# OBSTACULOS Y TERRENOS ESPECIALES
# -----------------------------------------------------------

def dibujar_obstaculo(screen, cx, cy, r):
    """
    Muro de piedra: fondo gris oscuro con bloques de piedra dibujados.
    Claramente indica que no se puede pasar.
    """
    # Fondo oscuro
    pygame.draw.circle(screen, (45, 45, 50), (cx, cy), r)

    # Bloques de piedra (patron de ladrillo)
    col_piedra  = (90, 90, 95)
    col_grieta  = (30, 30, 35)
    s = r // 3

    # Fila superior: 2 bloques
    for dx in [-s//2, s]:
        pygame.draw.rect(screen, col_piedra,
            (cx + dx - s//2, cy - s - s//4, s, s//2), border_radius=2)
        pygame.draw.rect(screen, col_grieta,
            (cx + dx - s//2, cy - s - s//4, s, s//2), 1, border_radius=2)

    # Fila central: 1 bloque ancho
    pygame.draw.rect(screen, col_piedra,
        (cx - s, cy - s//4, s*2, s//2), border_radius=2)
    pygame.draw.rect(screen, col_grieta,
        (cx - s, cy - s//4, s*2, s//2), 1, border_radius=2)

    # Fila inferior: 2 bloques
    for dx in [-s, s//2]:
        pygame.draw.rect(screen, col_piedra,
            (cx + dx, cy + s//4, s, s//2), border_radius=2)
        pygame.draw.rect(screen, col_grieta,
            (cx + dx, cy + s//4, s, s//2), 1, border_radius=2)

    # X roja encima para reforzar "no pasar"
    grosor = max(2, r//8)
    pygame.draw.line(screen, (200, 50, 50),
        (cx - r//2 + 4, cy - r//2 + 4), (cx + r//2 - 4, cy + r//2 - 4), grosor)
    pygame.draw.line(screen, (200, 50, 50),
        (cx + r//2 - 4, cy - r//2 + 4), (cx - r//2 + 4, cy + r//2 - 4), grosor)


def dibujar_bosque(screen, cx, cy, r):
    """Arboles verdes: 2-3 triangulos apilados."""
    pygame.draw.circle(screen, (34, 100, 34), (cx, cy), r)
    col_arbol = (20, 160, 20)
    col_tronco = (100, 60, 20)
    s = r // 2

    for i, (dx, escala) in enumerate([(-s//2, 0.9), (s//2, 0.8), (0, 1.0)]):
        bx = cx + dx
        # Copa (triangulo)
        pts = [
            (bx,          cy - int(s*escala)),
            (bx - int(s*escala*0.7), cy + int(s*escala*0.3)),
            (bx + int(s*escala*0.7), cy + int(s*escala*0.3)),
        ]
        pygame.draw.polygon(screen, col_arbol, pts)
        # Tronco
        pygame.draw.rect(screen, col_tronco,
            (bx - 2, cy + int(s*escala*0.3), 4, int(s*0.4)))


def dibujar_montana(screen, cx, cy, r):
    """Pico de montaña con nieve."""
    pygame.draw.circle(screen, (100, 75, 50), (cx, cy), r)
    s = r
    # Montaña principal
    pts_m = [(cx, cy - s), (cx - s, cy + s//2), (cx + s, cy + s//2)]
    pygame.draw.polygon(screen, (120, 90, 60), pts_m)
    # Nieve en la cima
    pts_n = [(cx, cy - s), (cx - s//3, cy - s//3), (cx + s//3, cy - s//3)]
    pygame.draw.polygon(screen, (240, 240, 255), pts_n)
    # Sombra lateral
    pygame.draw.line(screen, (80, 60, 40),
        (cx, cy - s), (cx - s, cy + s//2), 2)


def dibujar_zona_miedo(screen, cx, cy, r):
    """Zona oscura con calavera/fantasma para representar el miedo."""
    pygame.draw.circle(screen, (50, 0, 60), (cx, cy), r)
    pygame.draw.circle(screen, (100, 0, 120), (cx, cy), r, 2)

    # Fantasma simple
    s  = r // 2
    gc = (180, 150, 220)   # color fantasma

    # Cabeza redonda
    pygame.draw.circle(screen, gc, (cx, cy - s//3), s//2)
    # Cuerpo rectangular redondeado
    pygame.draw.rect(screen, gc,
        pygame.Rect(cx - s//2, cy - s//3, s, s), border_radius=4)
    # Ondas en la base del fantasma
    base_y = cy - s//3 + s
    for i in range(3):
        bx = cx - s//2 + i*(s//3)
        pygame.draw.arc(screen, gc,
            pygame.Rect(bx, base_y - s//6, s//3, s//4),
            math.pi, 2*math.pi, 3)
    # Ojos del fantasma
    pygame.draw.circle(screen, (50, 0, 60), (cx - s//5, cy - s//3), s//6)
    pygame.draw.circle(screen, (50, 0, 60), (cx + s//5, cy - s//3), s//6)

    # Pequeñas estrellas de fondo
    for dx, dy in [(-s+4, -s+4), (s-4, -s+4), (0, s-4)]:
        pygame.draw.circle(screen, (200, 180, 255), (cx+dx, cy+dy), 2)


# -----------------------------------------------------------
# HELPERS
# -----------------------------------------------------------
def _estrella(screen, cx, cy, r, puntas, color):
    ri = r // 2
    pts = []
    for i in range(puntas*2):
        a = math.radians(i*180/puntas - 90)
        radio = r if i%2==0 else ri
        pts.append((cx + int(radio*math.cos(a)), cy + int(radio*math.sin(a))))
    if len(pts) >= 3:
        pygame.draw.polygon(screen, color, pts)

def _corazon(screen, cx, cy, r, color):
    pts = []
    for i in range(360):
        t = math.radians(i)
        x = cx + int(r*16*math.sin(t)**3/16)
        y = cy - int(r*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))/16)
        pts.append((x, y))
    if len(pts) >= 3:
        pygame.draw.polygon(screen, color, pts)


# -----------------------------------------------------------
# API PUBLICA
# -----------------------------------------------------------
def dibujar_personaje(screen, emocion, cx, cy, radio):
    fn = CARAS.get(emocion)
    if fn:
        fn(screen, int(cx), int(cy), radio)
    else:
        pygame.draw.circle(screen, (180,180,180), (int(cx), int(cy)), radio)

def dibujar_estacion(screen, nombre, cx, cy, radio):
    fn = ESTACIONES_DRAW.get(nombre)
    if fn:
        fn(screen, int(cx), int(cy), radio)
    else:
        pygame.draw.circle(screen, (200,200,100), (int(cx), int(cy)), radio)

def dibujar_tipo_celda(screen, tipo, cx, cy, radio):
    """Dibuja el visual del tipo de terreno dentro del hexagono."""
    if tipo == "obstaculo":
        dibujar_obstaculo(screen, cx, cy, radio)
    elif tipo == "bosque":
        dibujar_bosque(screen, cx, cy, radio)
    elif tipo == "montana":
        dibujar_montana(screen, cx, cy, radio)
    elif tipo == "miedo":
        dibujar_zona_miedo(screen, cx, cy, radio)
    # "libre" no necesita dibujo especial


# -----------------------------------------------------------
# TEST VISUAL
# -----------------------------------------------------------
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 500))
    pygame.display.set_caption("Test Sprites")
    fuente = pygame.font.SysFont("consolas", 13)

    emociones  = ["tristeza","miedo","enojo","alegria","ansiedad"]
    estaciones = ["juego","calma","abrazo","amigos","respiracion"]
    terrenos   = ["obstaculo","bosque","montana","miedo"]

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

        screen.fill((20,20,28))

        # Fila 1: caras
        for i, em in enumerate(emociones):
            cx = 90 + i*190
            dibujar_personaje(screen, em, cx, 90, 55)
            lbl = fuente.render(em, True, (235,235,245))
            screen.blit(lbl, (cx - lbl.get_width()//2, 155))

        # Fila 2: estaciones
        for i, est in enumerate(estaciones):
            cx = 90 + i*190
            dibujar_estacion(screen, est, cx, 270, 55)
            lbl = fuente.render(est, True, (235,235,245))
            screen.blit(lbl, (cx - lbl.get_width()//2, 335))

        # Fila 3: terrenos
        for i, ter in enumerate(terrenos):
            cx = 90 + i*190
            dibujar_tipo_celda(screen, ter, cx, 430, 45)
            lbl = fuente.render(ter, True, (235,235,245))
            screen.blit(lbl, (cx - lbl.get_width()//2, 485))

        pygame.display.flip()

    pygame.quit()