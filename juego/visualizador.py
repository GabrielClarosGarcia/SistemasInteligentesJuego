# **********************************************************
# * Archivo: visualizador.py                               *
# * Descripcion: Con botón de Coco para pedir ayuda        *
# *              en cualquier momento del juego            *
# **********************************************************

import math
import pygame
from sprites import dibujar_personaje, dibujar_estacion, dibujar_tipo_celda
from entorno_juego import ST

SQRT3 = math.sqrt(3)

C_BG      = (18,  20,  30)
C_PANEL   = (28,  30,  45)
C_BORDE   = (55,  58,  80)
C_TEXTO   = (230, 232, 248)
C_DIM     = (130, 132, 155)
C_ACENTO  = (90,  170, 255)
C_EXITO   = (70,  200, 110)
C_PELIGRO = (220, 75,  75)
C_JUGADOR = (255, 200, 50)
C_ALGO    = (255, 255, 255)
C_COCO    = (255, 160, 30)    # naranja para Coco
C_SUGER   = (255, 160, 30)    # mismo naranja para la celda sugerida


class Visualizador:

    def __init__(self, entorno):
        self.e         = entorno
        self.W, self.H = 1200, 750
        self.PANEL_X   = 840
        self.HEX_SIZE  = 52
        self.ORIGIN    = (430, 375)
        self.step_ms   = 55
        self.last_step = 0
        self._coco_pulse = 0   # animacion de pulso para la celda sugerida

    # -----------------------------------------------------------
    # HEX MATH
    # -----------------------------------------------------------
    def axial_to_pixel(self, q, r):
        s = self.HEX_SIZE; ox, oy = self.ORIGIN
        return (ox + s*(SQRT3*q + (SQRT3/2)*r), oy + s*1.5*r)

    def hex_corners(self, cx, cy):
        return [(cx + self.HEX_SIZE*math.cos(math.radians(60*i-30)),
                 cy + self.HEX_SIZE*math.sin(math.radians(60*i-30)))
                for i in range(6)]

    def pixel_to_axial(self, x, y):
        s = self.HEX_SIZE; ox, oy = self.ORIGIN
        px = (x-ox)/s; py = (y-oy)/s
        return self._round((SQRT3/3)*px-(1/3)*py, (2/3)*py)

    def _round(self, q, r):
        x, z = q, r; y = -x-z
        rx,ry,rz = round(x),round(y),round(z)
        xd,yd,zd = abs(rx-x),abs(ry-y),abs(rz-z)
        if   xd>yd and xd>zd: rx = -ry-rz
        elif yd>zd:            ry = -rx-rz
        else:                  rz = -rx-ry
        return int(rx), int(rz)

    def mix(self, a, b, t):
        return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))

    # -----------------------------------------------------------
    # TABLERO
    # -----------------------------------------------------------
    def _draw_tablero(self, screen, font_s):
        tablero = self.e.get_tablero()
        if not tablero: return

        # Pulso para la celda de Coco (0.0 → 1.0 → 0.0)
        pulso = abs(math.sin(self._coco_pulse * 0.05))

        for (q, r), celda in tablero.celdas.items():
            cx, cy = self.axial_to_pixel(q, r)
            pts    = self.hex_corners(cx, cy)
            color  = celda.get_color()

            # Overlays en orden de prioridad
            if celda.en_camino_jugador:
                color = self.mix(color, C_JUGADOR, 0.50)
            if celda.visitada:
                color = self.mix(color, (120, 120, 200), 0.40)
            if celda.en_camino:
                color = self.mix(color, C_ALGO, 0.60)

            # Sugerencia de Coco: pulso naranja
            if celda.es_sugerencia:
                color = self.mix(color, C_SUGER, 0.55 + pulso * 0.35)

            # Celda activa del jugador
            es_activa = (self.e.celda_activa and
                         celda.q == self.e.celda_activa.q and
                         celda.r == self.e.celda_activa.r)
            if es_activa:
                color = self.mix(color, C_JUGADOR, 0.85)

            pygame.draw.polygon(screen, color, pts)

            # Borde especial para sugerencia y celda activa
            if celda.es_sugerencia:
                pygame.draw.polygon(screen, C_COCO, pts, 3)
            elif es_activa:
                pygame.draw.polygon(screen, C_JUGADOR, pts, 3)
            else:
                pygame.draw.polygon(screen, C_BORDE, pts, 1)

            radio_s = self.HEX_SIZE - 10

            # Sprites de terreno
            if celda.tipo not in ("libre",):
                dibujar_tipo_celda(screen, celda.tipo, int(cx), int(cy), radio_s)

            if celda.emocion:
                dibujar_personaje(screen, celda.emocion, int(cx), int(cy), radio_s)
            elif celda.estacion and celda.tipo != "obstaculo":
                dibujar_estacion(screen, celda.estacion, int(cx), int(cy), radio_s)

            # Modo tecnico
            if self.e.modo_tecnico:
                screen.blit(font_s.render(f"{q},{r}", True, (240,240,255)), (cx-16, cy+4))
                screen.blit(font_s.render(f"c{celda.get_costo()}", True, (240,240,255)), (cx-16, cy+18))

        # Numeracion del camino del jugador
        for i, celda in enumerate(self.e.camino_jugador):
            cx, cy = self.axial_to_pixel(celda.q, celda.r)
            lbl = font_s.render(str(i), True, (20,20,20))
            screen.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))

        # Flecha apuntando a la celda sugerida por Coco
        if self.e.coco_celda_sugerida and self.e.coco_visible:
            self._draw_coco_flecha(screen, font_s, pulso)

    def _draw_coco_flecha(self, screen, font_s, pulso):
        """Dibuja una flecha y etiqueta sobre la celda sugerida por Coco."""
        celda = self.e.coco_celda_sugerida
        cx, cy = self.axial_to_pixel(celda.q, celda.r)

        # Flecha hacia abajo apuntando a la celda
        arrow_y = cy - self.HEX_SIZE - 8 - int(pulso * 6)
        pts_flecha = [
            (cx,       arrow_y + 14),
            (cx - 10,  arrow_y),
            (cx + 10,  arrow_y),
        ]
        pygame.draw.polygon(screen, C_COCO, pts_flecha)

        # Etiqueta "COCO"
        lbl = font_s.render("COCO", True, C_COCO)
        screen.blit(lbl, (cx - lbl.get_width()//2, arrow_y - 16))

    # -----------------------------------------------------------
    # PANEL LATERAL
    # -----------------------------------------------------------
    def _draw_panel(self, screen, font, font_s):
        px = self.PANEL_X
        pygame.draw.rect(screen, C_PANEL, (px, 0, self.W-px, self.H))
        pygame.draw.line(screen, C_BORDE, (px, 0), (px, self.H), 2)

        e = self.e; y = 14

        def txt(t, col=C_TEXTO, f=None):
            nonlocal y
            s = (f or font).render(t, True, col)
            screen.blit(s, (px+12, y)); y += s.get_height()+5

        def sep():
            nonlocal y
            pygame.draw.line(screen, C_BORDE, (px+8, y), (self.W-8, y), 1)
            y += 10

        txt("CONEXION MENTAL", C_ACENTO)
        txt(f"Nivel {e.nivel_actual}/5  |  Puntos: {e.puntuacion}", C_DIM, font_s)
        sep()

        # Instruccion
        instrucciones = {
            ST["SELECCIONAR"]:    ("Haz clic en un personaje",        C_TEXTO),
            ST["JUGADOR_TRAZA"]:  ("Traza tu camino al destino",      C_JUGADOR),
            ST["RESUMEN_NIVEL"]:  ("ESPACIO → ver soluciones",        C_EXITO),
            ST["DEMO_ALGORITMO"]: ("Algoritmo buscando...",           C_ACENTO),
            ST["ENTRE_DEMOS"]:    ("ESPACIO → siguiente demo",        C_EXITO),
            ST["NIVEL_COMPLETO"]: ("[N] Siguiente nivel",             C_EXITO),
        }
        inst, col_i = instrucciones.get(e.get_estado(), ("", C_DIM))
        txt(inst, col_i, font_s)
        sep()

        # Algoritmo
        txt("ALGORITMO DEMO:", C_DIM, font_s)
        for k, tec, nom in [("1","amplitud","BFS Amplitud"),
                             ("2","profundidad","DFS Profundidad"),
                             ("3","costouniforme","Costo Uniforme")]:
            act = e.tecnica_actual == tec
            txt(f"[{k}] {'▶' if act else ' '} {nom}",
                C_ACENTO if act else C_DIM, font_s)
        sep()

        # Emocion activa
        if e.emocion_activa:
            txt(f"Trazando: {e.emocion_activa.upper()}", C_JUGADOR, font_s)
            txt(f"Pasos: {len(e.camino_jugador)}", C_TEXTO, font_s)
            sep()

        # Demo actual
        if e.demo_actual and e.get_estado() in (ST["DEMO_ALGORITMO"], ST["ENTRE_DEMOS"]):
            txt(f"Demo: {e.demo_actual.upper()}", C_ACENTO, font_s)
            pj = e.resultados_jugador.get(e.demo_actual,{}).get("pasos_jugador","?")
            pa = len(e.camino_algoritmo)
            txt(f"Tu: {pj} pasos", C_JUGADOR, font_s)
            txt(f"Algo: {pa} pasos", C_ACENTO, font_s)
            sep()

        # Emociones
        from juego.tablero_hexagonal import EMOCIONES
        txt("EMOCIONES:", C_DIM, font_s)
        mini = 13
        for em in e.emociones_pendientes:
            col_em = EMOCIONES.get(em,{}).get("color", C_TEXTO)
            dibujar_personaje(screen, em, px+22, y+mini, mini)
            screen.blit(font_s.render(f"  {em}", True, col_em), (px+40, y+4))
            y += mini*2+6
        for em in e.emociones_completadas:
            res   = e.resultados_jugador.get(em, {})
            pasos = res.get("pasos_jugador","?")
            usos  = res.get("usos_coco", 0)
            texto = f"  ✓ {em}: {pasos}p"
            if usos > 0:
                texto += f" (Coco:{usos})"
            screen.blit(font_s.render(texto, True, C_EXITO), (px+12, y))
            y += font_s.get_height()+4
        sep()

        # --- BOTON COCO ---
        estados_con_coco = (ST["SELECCIONAR"], ST["JUGADOR_TRAZA"])
        coco_disponible  = e.get_estado() in estados_con_coco

        coco_y  = y
        coco_col = C_COCO if coco_disponible else (80, 60, 30)
        pygame.draw.rect(screen, coco_col,
            (px+12, coco_y, self.W-px-24, 38), border_radius=10)

        # Cara de Coco (circulo simple con ojos)
        face_cx, face_cy = px+30, coco_y+19
        pygame.draw.circle(screen, (255,220,100), (face_cx, face_cy), 14)
        pygame.draw.circle(screen, (40,40,40),    (face_cx-4, face_cy-3), 3)
        pygame.draw.circle(screen, (40,40,40),    (face_cx+4, face_cy-3), 3)
        pygame.draw.arc(screen, (40,40,40),
            pygame.Rect(face_cx-6, face_cy, 12, 8), math.pi, 2*math.pi, 2)

        # Texto del boton
        coco_txt = "Pedir ayuda a Coco [H]" if coco_disponible else "Coco no disponible aqui"
        screen.blit(font_s.render(coco_txt, True, (255,255,255)), (px+50, coco_y+12))
        y += 48

        # Mensaje de Coco si hay sugerencia activa
        if e.coco_visible and e.coco_mensaje:
            sep()
            # Fondo del mensaje
            pygame.draw.rect(screen, (60, 45, 20),
                (px+8, y, self.W-px-16, 55), border_radius=8)
            pygame.draw.rect(screen, C_COCO,
                (px+8, y, self.W-px-16, 55), 2, border_radius=8)
            # Texto del mensaje (con wrap manual)
            palabras = e.coco_mensaje.split()
            linea = ""
            ly = y + 6
            for pal in palabras:
                prueba = linea + (" " if linea else "") + pal
                if font_s.size(prueba)[0] < self.W-px-30:
                    linea = prueba
                else:
                    screen.blit(font_s.render(linea, True, C_COCO), (px+14, ly))
                    ly += 16; linea = pal
            if linea:
                screen.blit(font_s.render(linea, True, C_COCO), (px+14, ly))
            y += 64

        sep()

        # Leyenda
        txt("LEYENDA:", C_DIM, font_s)
        for col_l, nom_l in [
            (C_JUGADOR,    "Tu camino"),
            (C_ALGO,       "Camino optimo"),
            (C_COCO,       "Sugerencia Coco"),
            ((120,120,200),"Celdas exploradas"),
        ]:
            pygame.draw.rect(screen, col_l, (px+12, y+3, 14, 14), border_radius=3)
            screen.blit(font_s.render(f"  {nom_l}", True, C_DIM), (px+28, y))
            y += 20
        sep()

        # Controles
        for ctrl in ["[Clic] Mover/Seleccionar",
                     "[H] Pedir ayuda a Coco",
                     "[SPACE] Continuar/Demo",
                     "[1/2/3] Algoritmo",
                     "[T] Tecnico  [R] Reset",
                     "[N] Siguiente  [M] Voz",
                     "[ESC] Salir"]:
            txt(ctrl, C_DIM, font_s)

        # Toggle voz
        vc = C_EXITO if e.voz.habilitada else C_PELIGRO
        vt = "VOZ ON [M]" if e.voz.habilitada else "VOZ OFF [M]"
        pygame.draw.rect(screen, vc, (px+12, self.H-42, 130, 30), border_radius=7)
        screen.blit(font_s.render(vt, True, (255,255,255)), (px+20, self.H-35))

    # -----------------------------------------------------------
    # OVERLAY RESUMEN
    # -----------------------------------------------------------
    def _draw_resumen_overlay(self, screen, font, font_s):
        ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov.fill((0,0,0,175))
        screen.blit(ov, (0,0))

        cx = self.PANEL_X // 2
        y  = self.H//2 - 160

        s = font.render("¡TODAS LAS EMOCIONES CONECTADAS!", True, C_EXITO)
        screen.blit(s, (cx - s.get_width()//2, y)); y += 45

        header = font_s.render(
            f"{'EMOCION':<13} {'TUS PASOS':>10} {'ALGORITMO':>11} {'COCO':>6}",
            True, C_ACENTO)
        screen.blit(header, (cx - header.get_width()//2, y)); y += 25
        pygame.draw.line(screen, C_DIM, (cx-170, y), (cx+170, y), 1); y += 10

        for em in self.e.emociones_completadas:
            res = self.e.resultados_jugador.get(em, {})
            pj  = res.get("pasos_jugador", "?")
            uc  = res.get("usos_coco", 0)
            pos_i = self.e.tablero.personajes.get(em)
            pos_m = self.e.tablero.metas.get(em)
            if pos_i and pos_m:
                ci = self.e.tablero.get_celda(*pos_i)
                cm = self.e.tablero.get_celda(*pos_m)
                pa = len(self.e.agente.buscar(ci, cm, self.e.tecnica_actual))
            else:
                pa = "?"
            col_row = C_EXITO if (isinstance(pj,int) and isinstance(pa,int) and pj<=pa) else C_JUGADOR
            row = font_s.render(
                f"{em:<13} {str(pj):>10} {str(pa):>11} {str(uc):>6}",
                True, col_row)
            screen.blit(row, (cx - row.get_width()//2, y)); y += 22

        y += 15
        inst = font.render("Presiona ESPACIO para ver las soluciones del algoritmo", True, C_TEXTO)
        screen.blit(inst, (cx - inst.get_width()//2, y))

    # -----------------------------------------------------------
    # OVERLAY NIVEL COMPLETO
    # -----------------------------------------------------------
    def _draw_nivel_completo(self, screen, font, font_s):
        ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        ov.fill((0,0,0,160))
        screen.blit(ov, (0,0))
        cx = self.PANEL_X//2
        y  = self.H//2 - 90
        ems = self.e.emociones_completadas
        for i, em in enumerate(ems):
            ex = cx - (len(ems)-1)*35 + i*70
            dibujar_personaje(screen, em, ex, y, 26)
        y += 50
        for t, col in [("¡NIVEL COMPLETADO!", C_EXITO),
                       (f"Puntuacion: {self.e.puntuacion}", C_ACENTO),
                       ("[N] Siguiente  [R] Reintentar", C_TEXTO)]:
            s = font.render(t, True, col)
            screen.blit(s, (cx - s.get_width()//2, y)); y += 45

    # -----------------------------------------------------------
    # DRAW
    # -----------------------------------------------------------
    def draw(self, screen, font, font_s):
        screen.fill(C_BG)
        self._draw_tablero(screen, font_s)
        self._draw_panel(screen, font, font_s)
        estado = self.e.get_estado()
        if estado == ST["RESUMEN_NIVEL"]:
            self._draw_resumen_overlay(screen, font, font_s)
        elif estado == ST["NIVEL_COMPLETO"]:
            self._draw_nivel_completo(screen, font, font_s)

    # -----------------------------------------------------------
    # MAIN LOOP
    # -----------------------------------------------------------
    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Conexion Mental")
        clock  = pygame.time.Clock()
        font   = pygame.font.SysFont("consolas", 17)
        font_s = pygame.font.SysFont("consolas", 13)

        self.e.cargar_nivel(1)

        while True:
            now = pygame.time.get_ticks()
            self._coco_pulse += 1   # animacion pulso Coco

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.e.cerrar(); pygame.quit(); return

                if ev.type == pygame.KEYDOWN:
                    k = ev.key
                    if   k == pygame.K_ESCAPE:
                        self.e.cerrar(); pygame.quit(); return
                    elif k == pygame.K_t: self.e.toggle_modo_tecnico()
                    elif k == pygame.K_1: self.e.cambiar_tecnica("amplitud")
                    elif k == pygame.K_2: self.e.cambiar_tecnica("profundidad")
                    elif k == pygame.K_3: self.e.cambiar_tecnica("costouniforme")
                    elif k == pygame.K_r: self.e.cargar_nivel(self.e.nivel_actual)
                    elif k == pygame.K_n: self.e.siguiente_nivel()
                    elif k == pygame.K_m: self.e.voz.toggle_voz()
                    elif k == pygame.K_h: self.e.pedir_ayuda_coco()   # H = Help = Coco
                    elif k == pygame.K_SPACE:
                        estado = self.e.get_estado()
                        if   estado == ST["RESUMEN_NIVEL"]: self.e.iniciar_demos()
                        elif estado == ST["ENTRE_DEMOS"]:   self.e.confirmar_siguiente_demo()

                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mx, my = ev.pos
                    if mx >= self.PANEL_X: continue

                    q, r   = self.pixel_to_axial(mx, my)
                    estado = self.e.get_estado()

                    if estado == ST["SELECCIONAR"]:
                        celda = self.e.tablero.get_celda(q, r)
                        if celda and celda.emocion:
                            self.e.seleccionar_emocion(celda.emocion)

                    elif estado == ST["JUGADOR_TRAZA"]:
                        self.e.intentar_mover_jugador(q, r)

            # Animacion algoritmo
            if self.e.get_estado() == ST["DEMO_ALGORITMO"]:
                if now - self.last_step >= self.step_ms:
                    self.last_step = now
                    self.e.avanzar_animacion_algoritmo()

            self.draw(screen, font, font_s)
            pygame.display.flip()
            clock.tick(60)