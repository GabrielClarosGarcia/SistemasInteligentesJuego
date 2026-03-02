# juego/visualizador.py
import math
import pygame

SQRT3 = math.sqrt(3)


class Visualizador:
    def __init__(self, entorno):
        self.entorno = entorno
        self.W, self.H = 1100, 750
        self.HEX_SIZE = 36
        self.ORIGIN = (110, 110)

        self.step_ms = 70   # velocidad animación (ms por paso)
        self.last_step = 0

    # -----------------------
    # Hex math (axial q,r)
    # -----------------------
    def axial_to_pixel(self, q, r):
        size = self.HEX_SIZE
        ox, oy = self.ORIGIN
        x = size * (SQRT3 * q + (SQRT3 / 2) * r)
        y = size * (1.5 * r)
        return ox + x, oy + y

    def hex_corners(self, cx, cy):
        pts = []
        for i in range(6):
            angle = math.radians(60 * i - 30)  # pointy-top
            pts.append((cx + self.HEX_SIZE * math.cos(angle),
                        cy + self.HEX_SIZE * math.sin(angle)))
        return pts

    def pixel_to_axial(self, x, y):
        size = self.HEX_SIZE
        ox, oy = self.ORIGIN
        px = (x - ox) / size
        py = (y - oy) / size

        q = (SQRT3 / 3) * px - (1 / 3) * py
        r = (2 / 3) * py
        return self.hex_round(q, r)

    def hex_round(self, q, r):
        x = q
        z = r
        y = -x - z

        rx, ry, rz = round(x), round(y), round(z)

        x_diff = abs(rx - x)
        y_diff = abs(ry - y)
        z_diff = abs(rz - z)

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry
        return int(rx), int(rz)

    # -----------------------
    # Draw
    # -----------------------
    def draw(self, screen, font, font_small):
        screen.fill((20, 20, 28))
        tablero = self.entorno.get_tablero()
        if tablero is None:
            return

        # celdas
        for (q, r), celda in tablero.celdas.items():
            cx, cy = self.axial_to_pixel(q, r)
            pts = self.hex_corners(cx, cy)

            color = celda.get_color()

            # overlays
            if celda.visitada:
                color = self.mix(color, (130, 130, 180), 0.55)
            if celda.en_camino:
                color = self.mix(color, (255, 255, 255), 0.65)

            pygame.draw.polygon(screen, color, pts)
            pygame.draw.polygon(screen, (55, 55, 75), pts, 2)

            # texto dentro (sin emoji para evitar fallas de fuente)
            if celda.emocion:
                label = celda.emocion[:2].upper()
                txt = font.render(label, True, (10, 10, 10))
                screen.blit(txt, (cx - 12, cy - 10))
            elif celda.estacion:
                label = celda.estacion[:2].upper()
                txt = font.render(label, True, (10, 10, 10))
                screen.blit(txt, (cx - 12, cy - 10))

            # modo técnico: coordenadas + costo
            if self.entorno.modo_tecnico:
                t = font_small.render(f"{q},{r}", True, (240, 240, 245))
                screen.blit(t, (cx - 18, cy + 10))
                c = font_small.render(f"c{celda.get_costo()}", True, (240, 240, 245))
                screen.blit(c, (cx - 18, cy + 26))

        # HUD
        hud = [
            f"Estado: {self.entorno.get_estado()} | Técnica: {self.entorno.tecnica_actual} | Puntos: {self.entorno.puntuacion}",
            "Click en una EMOCIÓN para buscar | 1=BFS 2=DFS 3=UCS | T=Modo técnico | R=Reset nivel",
            f"Pendientes: {', '.join(self.entorno.emociones_pendientes) if self.entorno.emociones_pendientes else 'ninguna'}",
        ]
        y = 10
        for line in hud:
            screen.blit(font.render(line, True, (235, 235, 245)), (10, y))
            y += 24

    def mix(self, a, b, t):
        return (
            int(a[0] * (1 - t) + b[0] * t),
            int(a[1] * (1 - t) + b[1] * t),
            int(a[2] * (1 - t) + b[2] * t),
        )

    # -----------------------
    # Main loop
    # -----------------------
    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Conexion Mental (Proto)")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("consolas", 18)
        font_small = pygame.font.SysFont("consolas", 14)

        self.entorno.cargar_nivel(1)

        while True:
            now = pygame.time.get_ticks()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return

                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_t:
                        self.entorno.toggle_modo_tecnico()
                    elif e.key == pygame.K_1:
                        self.entorno.cambiar_tecnica("amplitud")
                    elif e.key == pygame.K_2:
                        self.entorno.cambiar_tecnica("profundidad")
                    elif e.key == pygame.K_3:
                        self.entorno.cambiar_tecnica("costouniforme")
                    elif e.key == pygame.K_r:
                        self.entorno.cargar_nivel(1)

                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    q, r = self.pixel_to_axial(mx, my)
                    celda = self.entorno.tablero.get_celda(q, r) if self.entorno.tablero else None
                    if celda and celda.emocion:
                        # inicia búsqueda al hacer click en la emoción
                        self.entorno.iniciar_busqueda(celda.emocion, self.entorno.tecnica_actual)

            # lógica por estado
            if self.entorno.get_estado() == "buscando":
                # hace la búsqueda (rápido en 8x8)
                self.entorno.evolucionar()

            if self.entorno.get_estado() == "animando":
                if now - self.last_step >= self.step_ms:
                    self.last_step = now
                    self.entorno.avanzar_animacion()

            self.draw(screen, font, font_small)
            pygame.display.flip()
            clock.tick(60)