# **********************************************************
# * Archivo: visualizador.py (actualizado)                 *
# * Descripcion: Renderizado Pygame con panel lateral,     *
# *              navegacion de niveles y boton de microfono*
# **********************************************************

import math
import pygame

SQRT3 = math.sqrt(3)

# Colores UI
C_BG        = (20,  20,  28)
C_PANEL     = (30,  30,  42)
C_BORDE     = (55,  55,  75)
C_TEXTO     = (235, 235, 245)
C_TEXTO_DIM = (140, 140, 160)
C_ACENTO    = (100, 180, 255)
C_EXITO     = (80,  200, 120)
C_PELIGRO   = (220, 80,  80)
C_BOTON     = (50,  50,  70)
C_BOTON_ACT = (80,  120, 200)
C_MIC       = (60,  180, 100)
C_MIC_ACT   = (220, 80,  80)


class Visualizador:
    def __init__(self, entorno):
        self.entorno = entorno
        self.W, self.H   = 1200, 750
        self.PANEL_X     = 850          # inicio del panel lateral
        self.HEX_SIZE    = 36
        self.ORIGIN      = (80, 100)

        self.step_ms   = 60
        self.last_step = 0

    # -----------------------------------------------------------
    # HEX MATH
    # -----------------------------------------------------------
    def axial_to_pixel(self, q, r):
        size = self.HEX_SIZE
        ox, oy = self.ORIGIN
        x = size * (SQRT3 * q + (SQRT3 / 2) * r)
        y = size * (1.5 * r)
        return ox + x, oy + y

    def hex_corners(self, cx, cy):
        pts = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            pts.append((cx + self.HEX_SIZE * math.cos(angle),
                        cy + self.HEX_SIZE * math.sin(angle)))
        return pts

    def pixel_to_axial(self, x, y):
        size = self.HEX_SIZE
        ox, oy = self.ORIGIN
        px = (x - ox) / size
        py = (y - oy) / size
        q  = (SQRT3 / 3) * px - (1 / 3) * py
        r  = (2 / 3) * py
        return self._hex_round(q, r)

    def _hex_round(self, q, r):
        x, z = q, r
        y    = -x - z
        rx, ry, rz = round(x), round(y), round(z)
        xd, yd, zd = abs(rx-x), abs(ry-y), abs(rz-z)
        if xd > yd and xd > zd:
            rx = -ry - rz
        elif yd > zd:
            ry = -rx - rz
        else:
            rz = -rx - ry
        return int(rx), int(rz)

    def mix(self, a, b, t):
        return (
            int(a[0]*(1-t) + b[0]*t),
            int(a[1]*(1-t) + b[1]*t),
            int(a[2]*(1-t) + b[2]*t),
        )

    # -----------------------------------------------------------
    # DIBUJO DEL TABLERO
    # -----------------------------------------------------------
    def _draw_tablero(self, screen, font, font_small):
        tablero = self.entorno.get_tablero()
        if not tablero:
            return

        for (q, r), celda in tablero.celdas.items():
            cx, cy = self.axial_to_pixel(q, r)

            # Solo dibuja si esta dentro del area del tablero
            if cx > self.PANEL_X - 20:
                continue

            pts   = self.hex_corners(cx, cy)
            color = celda.get_color()

            if celda.visitada:
                color = self.mix(color, (130, 130, 200), 0.50)
            if celda.en_camino:
                color = self.mix(color, (255, 255, 255), 0.65)

            pygame.draw.polygon(screen, color, pts)
            pygame.draw.polygon(screen, C_BORDE, pts, 2)

            # Etiqueta dentro del hexagono
            if celda.emocion:
                label = celda.emocion[:2].upper()
                txt = font.render(label, True, (10, 10, 10))
                screen.blit(txt, (cx - 12, cy - 10))
            elif celda.estacion:
                label = celda.estacion[:2].upper()
                txt = font.render(label, True, (10, 10, 10))
                screen.blit(txt, (cx - 12, cy - 10))

            # Modo tecnico: coordenadas y costo
            if self.entorno.modo_tecnico:
                t1 = font_small.render(f"{q},{r}", True, (240, 240, 245))
                t2 = font_small.render(f"c{celda.get_costo()}", True, (240, 240, 245))
                screen.blit(t1, (cx - 18, cy + 8))
                screen.blit(t2, (cx - 18, cy + 22))

    # -----------------------------------------------------------
    # PANEL LATERAL
    # -----------------------------------------------------------
    def _draw_panel(self, screen, font, font_small):
        px = self.PANEL_X
        pygame.draw.rect(screen, C_PANEL, (px, 0, self.W - px, self.H))
        pygame.draw.line(screen, C_BORDE, (px, 0), (px, self.H), 2)

        e = self.entorno
        y = 15

        def txt(texto, color=C_TEXTO, f=None):
            nonlocal y
            surf = (f or font).render(texto, True, color)
            screen.blit(surf, (px + 12, y))
            y += surf.get_height() + 4

        def sep():
            nonlocal y
            pygame.draw.line(screen, C_BORDE, (px+8, y+2), (self.W-8, y+2), 1)
            y += 10

        # Titulo
        txt("CONEXION MENTAL", C_ACENTO)
        txt(f"Nivel {e.nivel_actual} / {e.nivel_maximo}", C_TEXTO_DIM, font_small)
        txt(f"Puntos: {e.puntuacion}", C_EXITO)
        sep()

        # Tecnica activa
        txt("TECNICA DE BUSQUEDA:", C_TEXTO_DIM, font_small)
        tecnicas = [
            ("1", "amplitud",      "BFS - Amplitud"),
            ("2", "profundidad",   "DFS - Profundidad"),
            ("3", "costouniforme", "Costo Uniforme"),
        ]
        for key, tec, nombre in tecnicas:
            activa = e.tecnica_actual == tec
            color  = C_ACENTO if activa else C_TEXTO
            prefijo = ">" if activa else " "
            txt(f"[{key}] {prefijo} {nombre}", color, font_small)
        sep()

        # Estado
        txt("ESTADO:", C_TEXTO_DIM, font_small)
        colores_estado = {
            "jugando":   C_EXITO,
            "buscando":  C_ACENTO,
            "animando":  (255, 200, 50),
            "completado": C_EXITO,
            "menu":      C_TEXTO_DIM,
        }
        color_estado = colores_estado.get(e.get_estado(), C_TEXTO)
        txt(e.get_estado().upper(), color_estado)
        sep()

        # Emociones pendientes
        txt("EMOCIONES:", C_TEXTO_DIM, font_small)
        from juego.tablero_hexagonal import EMOCIONES
        for emocion in e.emociones_pendientes:
            datos = EMOCIONES.get(emocion, {})
            color_em = datos.get("color", C_TEXTO)
            txt(f"  {emocion.upper()}", color_em, font_small)

        if e.emociones_completadas:
            txt("COMPLETADAS:", C_TEXTO_DIM, font_small)
            for emocion in e.emociones_completadas:
                txt(f"  ✓ {emocion}", C_EXITO, font_small)
        sep()

        # Resultado ultima busqueda
        if e.emocion_activa and e.emocion_activa in e.resultados_busqueda:
            res = e.resultados_busqueda[e.emocion_activa]
            txt("ULTIMA BUSQUEDA:", C_TEXTO_DIM, font_small)
            txt(f"  Pasos: {res.get('pasos',0)}", C_TEXTO, font_small)
            txt(f"  Costo: {res.get('costo',0)}", C_TEXTO, font_small)
            sep()

        # Botones de control
        y = self.H - 220
        txt("CONTROLES:", C_TEXTO_DIM, font_small)
        controles = [
            "[T]  Modo tecnico",
            "[R]  Reset nivel",
            "[N]  Siguiente nivel",
            "[M]  Silenciar/Voz",
            "[V]  Microfono (STT)",
            "[ESC] Salir",
        ]
        for ctrl in controles:
            txt(ctrl, C_TEXTO_DIM, font_small)

        # Boton microfono visual
        mic_y    = self.H - 55
        mic_x    = px + 20
        mic_col  = C_MIC_ACT if e.voz.stt_escuchando else C_MIC
        mic_txt  = "● REC" if e.voz.stt_escuchando else "🎤 HABLAR [V]"
        pygame.draw.rect(screen, mic_col, (mic_x, mic_y, 150, 34), border_radius=8)
        lbl = font.render(mic_txt, True, (255, 255, 255))
        screen.blit(lbl, (mic_x + 10, mic_y + 7))

        # Indicador voz ON/OFF
        voz_col = C_EXITO if e.voz.voz_habilitada else C_PELIGRO
        voz_txt = "VOZ ON" if e.voz.voz_habilitada else "VOZ OFF"
        pygame.draw.rect(screen, voz_col, (mic_x + 160, mic_y, 80, 34), border_radius=8)
        lv = font_small.render(voz_txt, True, (255, 255, 255))
        screen.blit(lv, (mic_x + 168, mic_y + 9))

    # -----------------------------------------------------------
    # HUD SUPERIOR
    # -----------------------------------------------------------
    def _draw_hud(self, screen, font_small):
        hud = (
            f"Click en EMOCION para buscar  |  "
            f"Nivel {self.entorno.nivel_actual}  |  "
            f"Tecnica: {self.entorno.tecnica_actual}  |  "
            f"{'[TECNICO]' if self.entorno.modo_tecnico else '[NIÑO]'}"
        )
        surf = font_small.render(hud, True, C_TEXTO_DIM)
        screen.blit(surf, (8, 8))

    # -----------------------------------------------------------
    # PANTALLA NIVEL COMPLETADO
    # -----------------------------------------------------------
    def _draw_completado(self, screen, font):
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        msg1 = font.render("¡NIVEL COMPLETADO!", True, C_EXITO)
        msg2 = font.render(f"Puntuacion: {self.entorno.puntuacion}", True, C_ACENTO)
        msg3 = font.render("Presiona [N] para el siguiente nivel", True, C_TEXTO)

        cx = self.PANEL_X // 2
        screen.blit(msg1, (cx - msg1.get_width()//2, self.H//2 - 60))
        screen.blit(msg2, (cx - msg2.get_width()//2, self.H//2))
        screen.blit(msg3, (cx - msg3.get_width()//2, self.H//2 + 50))

    # -----------------------------------------------------------
    # DRAW PRINCIPAL
    # -----------------------------------------------------------
    def draw(self, screen, font, font_small):
        screen.fill(C_BG)
        self._draw_tablero(screen, font, font_small)
        self._draw_panel(screen, font, font_small)
        self._draw_hud(screen, font_small)

        if self.entorno.get_estado() == "completado":
            self._draw_completado(screen, font)

    # -----------------------------------------------------------
    # MAIN LOOP
    # -----------------------------------------------------------
    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Conexion Mental - Busqueda No Informada")
        clock      = pygame.time.Clock()
        font       = pygame.font.SysFont("consolas", 17)
        font_small = pygame.font.SysFont("consolas", 13)

        self.entorno.cargar_nivel(1)

        while True:
            now = pygame.time.get_ticks()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.entorno.cerrar()
                    pygame.quit()
                    return

                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.entorno.cerrar()
                        pygame.quit()
                        return
                    elif e.key == pygame.K_t:
                        self.entorno.toggle_modo_tecnico()
                    elif e.key == pygame.K_1:
                        self.entorno.cambiar_tecnica("amplitud")
                    elif e.key == pygame.K_2:
                        self.entorno.cambiar_tecnica("profundidad")
                    elif e.key == pygame.K_3:
                        self.entorno.cambiar_tecnica("costouniforme")
                    elif e.key == pygame.K_r:
                        self.entorno.cargar_nivel(self.entorno.nivel_actual)
                    elif e.key == pygame.K_n:
                        self.entorno.siguiente_nivel()
                    elif e.key == pygame.K_m:
                        self.entorno.voz.toggle_voz()
                    elif e.key == pygame.K_v:
                        self.entorno.activar_escucha()

                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    # Click en boton microfono
                    px = self.PANEL_X
                    if px + 20 <= mx <= px + 170 and self.H - 55 <= my <= self.H - 21:
                        self.entorno.activar_escucha()
                        continue

                    # Click en el tablero
                    if mx < self.PANEL_X and self.entorno.tablero:
                        q, r   = self.pixel_to_axial(mx, my)
                        celda  = self.entorno.tablero.get_celda(q, r)
                        estado = self.entorno.get_estado()
                        if celda and celda.emocion and estado == "jugando":
                            self.entorno.iniciar_busqueda(
                                celda.emocion,
                                self.entorno.tecnica_actual
                            )

            # Logica por estado
            if self.entorno.get_estado() == "buscando":
                self.entorno.evolucionar()

            if self.entorno.get_estado() == "animando":
                if now - self.last_step >= self.step_ms:
                    self.last_step = now
                    self.entorno.avanzar_animacion()

            self.draw(screen, font, font_small)
            pygame.display.flip()
            clock.tick(60)