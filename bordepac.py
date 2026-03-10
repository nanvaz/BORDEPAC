#!/usr/bin/env python3
"""
BORDEPAC — Border Collie come bolinhas de tênis!
Jogo estilo Pac-Man: setas para mover, colete todas as bolinhas.
Power-up: pastoreie os Beagles de volta ao canil!
"""
import sys, math, random, array
import pygame

# ═══════════════════════════════════════════════════════════
#  CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════
T        = 32          # pixels por tile
COLS     = 21
ROWS     = 19
HUD_H    = 56
SW       = COLS * T            # 672
SH       = ROWS * T + HUD_H   # 664
FPS      = 60

SPD_P    = 5.0     # tiles/s (jogador)
SPD_G    = 3.4     # tiles/s (beagles)
SPD_INC  = 0.3     # aceleração por fase
LIVES    = 3
KENNEL_S = 4.0     # segundos preso no canil após pastoreio
POWER_S  = 10.0    # duração do power-up (fase 1)
POWER_MIN= 3.0
POWER_DEC= 1.0
PTS_DOT  = 10
PTS_PWR  = 50
PTS_HERD = 200     # dobra por beagle consecutivo

# ─── Tipos de tile ─────────────────────────────────────────
EMPTY = 0
WALL  = 1
DOT   = 2
POWER = 3

# ─── Cores ─────────────────────────────────────────────────
BG_C    = (0,   0,   30)
WALL_C  = (28,  80,  220)
DOT_C   = (175, 215, 40)
PWR_C   = (240, 225, 50)
WHT     = (255, 255, 255)
BLK     = (0,   0,   0)
HUD_C   = (180, 180, 180)
WIN_C   = (90,  250, 60)
LOSE_C  = (255, 65,  65)

# Border Collie
BC_BD   = (15,  15,  15)    # corpo preto
BC_WH   = (228, 228, 228)   # barriga / manchas brancas
BC_BR   = (140, 85,  35)    # focinho marrom
BC_NS   = (30,  15,  8)     # nariz

# Beagle base
BG_TN   = (185, 128, 60)    # tan
BG_WH   = (228, 228, 228)   # branco
BG_NS   = (62,  30,  20)    # nariz

# Accent por personalidade: [Biscuit, Caramel, Pepper, Nugget]
ACCENTS = [
    (215, 60,  45),    # Biscuit  — vermelho
    (210, 145, 190),   # Caramel  — rosa
    (40,  185, 185),   # Pepper   — ciano
    (225, 145, 20),    # Nugget   — laranja
]

SCR_C   = (20,  20,  165)   # beagle assustado
SCF_C   = (205, 205, 205)   # beagle assustado piscando
KNL_C   = (90,  55,  18)    # canil (fill)
KNB_C   = (40,  20,  4)     # canil (barras)

# ═══════════════════════════════════════════════════════════
#  LABIRINTO  21×19
#  0=vazio  1=parede  2=bolinha  3=power-up
# ═══════════════════════════════════════════════════════════
_MAP = [
#   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # r0
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # r1
    [1, 3, 1, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1, 1, 3, 1],  # r2
    [1, 2, 1, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1, 1, 2, 1],  # r3
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # r4
    [1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1],  # r5
    [1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1],  # r6
    [1, 1, 1, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 1, 1, 1],  # r7 (topo canil)
    [1, 2, 2, 2, 2, 2, 1, 0, 1, 1, 1, 1, 1, 0, 1, 2, 2, 2, 2, 2, 1],  # r8
    [1, 2, 1, 1, 1, 2, 1, 0, 1, 0, 0, 0, 1, 0, 1, 2, 1, 1, 1, 2, 1],  # r9 (canil)
    [1, 2, 2, 2, 2, 2, 1, 0, 1, 0, 0, 0, 1, 0, 1, 2, 2, 2, 2, 2, 1],  # r10
    [1, 1, 1, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 1, 1, 1],  # r11 (base canil)
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # r12
    [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],  # r13
    [1, 3, 2, 1, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 1, 2, 3, 1],  # r14 (início jogador)
    [1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1],  # r15
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # r16
    [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1],  # r17
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # r18
]

PLAYER_START = (10, 14)
GHOST_STARTS = [(9, 9), (10, 9), (11, 9), (10, 10)]

# ═══════════════════════════════════════════════════════════
#  SONS SINTÉTICOS
# ═══════════════════════════════════════════════════════════
_SR = 22050   # sample rate

def _tone(freq, ms, vol=0.35, shape="sine", fade=8):
    n = int(_SR * ms / 1000)
    buf = array.array("h")
    fade_n = int(_SR * fade / 1000)
    for i in range(n):
        t = i / _SR
        if shape == "square":
            v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        else:
            v = math.sin(2 * math.pi * freq * t)
        env = 1.0
        if i < fade_n:
            env = i / fade_n
        elif i > n - fade_n:
            env = (n - i) / fade_n
        buf.append(int(v * env * vol * 32767))
    return pygame.sndarray.make_sound(
        __import__("numpy").array(buf, dtype="int16").reshape(-1, 1).repeat(2, axis=1)
    )

def _sweep(f0, f1, ms, vol=0.38):
    n = int(_SR * ms / 1000)
    buf = array.array("h")
    for i in range(n):
        t = i / _SR
        freq = f0 + (f1 - f0) * (i / n)
        v = math.sin(2 * math.pi * freq * t)
        fade_n = int(_SR * 10 / 1000)
        env = 1.0
        if i < fade_n:
            env = i / fade_n
        elif i > n - fade_n:
            env = (n - i) / fade_n
        buf.append(int(v * env * vol * 32767))
    return pygame.sndarray.make_sound(
        __import__("numpy").array(buf, dtype="int16").reshape(-1, 1).repeat(2, axis=1)
    )

class Sounds:
    def __init__(self):
        self.ok = False
        self._s = {}

    def init(self):
        try:
            import numpy  # noqa: F401
            pygame.mixer.init(frequency=_SR, size=-16, channels=2, buffer=512)
            self._s = {
                "dot":   _tone(880, 55, vol=0.25),
                "power": _sweep(350, 1400, 220, vol=0.45),
                "herd":  _tone(200, 130, vol=0.55, shape="square"),
                "die":   _sweep(650, 90, 650, vol=0.45),
                "win":   _sweep(380, 1700, 420, vol=0.45),
            }
            self.ok = True
        except Exception as e:
            print(f"[sons] desativado: {e}")

    def play(self, name):
        if self.ok and name in self._s:
            self._s[name].play()

# ═══════════════════════════════════════════════════════════
#  DESENHO DE PERSONAGENS
# ═══════════════════════════════════════════════════════════

def draw_border_collie(surf, x, y, dx, dy, frame, powered):
    """Desenha o Border Collie no pixel (x, y)."""
    cx, cy = x + T // 2, y + T // 2
    r = T // 2 - 2

    # Corpo preto
    pygame.draw.ellipse(surf, BC_BD, (x + 4, y + 8, T - 8, T - 10))
    # Barriga branca
    pygame.draw.ellipse(surf, BC_WH, (x + 7, y + 13, T - 14, T - 18))

    # Cabeça (muda de posição conforme direção)
    hx_off = {"right": 7, "left": -7, "up": 0, "down": 0}
    hy_off = {"right": -2, "left": -2, "up": -8, "down": 6}
    dir_name = _dir_name(dx, dy)
    hcx = cx + hx_off.get(dir_name, 7)
    hcy = cy + hy_off.get(dir_name, -2)

    pygame.draw.circle(surf, BC_BD, (hcx, hcy), 8)
    # Mancha branca na testa
    pygame.draw.circle(surf, BC_WH, (hcx, hcy - 3), 3)
    # Focinho
    mx_off = {"right": 5, "left": -5, "up": 0, "down": 0}
    my_off = {"right": 3, "left": 3,  "up": 5, "down": 5}
    mox, moy = mx_off.get(dir_name, 5), my_off.get(dir_name, 3)
    pygame.draw.ellipse(surf, BC_BR, (hcx + mox - 4, hcy + moy - 2, 8, 5))
    pygame.draw.circle(surf, BC_NS, (hcx + mox, hcy + moy), 2)

    # Olho
    ex_off = {"right": 2, "left": -2, "up": 3, "down": 3}
    ey_off = {"right": -3, "left": -3, "up": -2, "down": -2}
    eox, eoy = ex_off.get(dir_name, 2), ey_off.get(dir_name, -3)
    pygame.draw.circle(surf, BC_NS, (hcx + eox, hcy + eoy), 2)

    # Orelha caída
    er_off = {"right": (-6, -4), "left": (6, -4), "up": (-6, 0), "down": (-6, 0)}
    erox, eroy = er_off.get(dir_name, (-6, -4))
    pygame.draw.ellipse(surf, BC_BD, (hcx + erox, hcy + eroy, 6, 9))

    # Patas animadas
    paw_y = y + T - 6 + (frame % 2) * 2
    pygame.draw.circle(surf, BC_BD, (x + 9, paw_y), 3)
    pygame.draw.circle(surf, BC_BD, (x + T - 9, paw_y - (1 if frame == 1 else 0)), 3)

    # Rabo (oposto à direção)
    tx_off = {"right": -10, "left": 10, "up": 0, "down": 0}
    ty_off = {"right": 0, "left": 0, "up": 8, "down": -8}
    pygame.draw.line(surf, BC_WH,
                     (cx, cy + 5),
                     (cx + tx_off.get(dir_name, -10), cy + 5 + ty_off.get(dir_name, 0)), 3)

    # Aura dourada se com power-up
    if powered:
        pygame.draw.circle(surf, (255, 220, 50), (cx, cy), r + 3, 2)


def draw_beagle(surf, x, y, accent, scared, flashing, locked):
    """Desenha um Beagle no pixel (x, y)."""
    cx, cy = x + T // 2, y + T // 2

    if locked:
        # Beagle no canil: círculo com grades
        pygame.draw.circle(surf, KNL_C, (cx, cy), T // 2 - 2)
        for bx in range(x + 4, x + T - 3, 6):
            pygame.draw.line(surf, KNB_C, (bx, y + 4), (bx, y + T - 4), 2)
        pygame.draw.line(surf, KNB_C, (x + 4, cy), (x + T - 4, cy), 2)
        return

    color = (SCF_C if flashing else SCR_C) if scared else None

    # Corpo
    body_c = color if color else BG_TN
    pygame.draw.ellipse(surf, body_c, (x + 5, y + 11, T - 10, T - 14))
    if not scared:
        pygame.draw.ellipse(surf, BG_WH, (x + 8, y + 15, T - 16, T - 20))

    # Cabeça
    pygame.draw.circle(surf, body_c, (cx, cy - 2), 8)
    if not scared:
        # Mancha colorida de personalidade no topo da cabeça
        pygame.draw.circle(surf, accent, (cx, cy - 5), 5)
        # Focinho branco
        pygame.draw.ellipse(surf, BG_WH, (cx - 4, cy + 2, 8, 5))
        pygame.draw.circle(surf, BG_NS, (cx, cy + 4), 2)
        # Olhos
        pygame.draw.circle(surf, WHT, (cx - 3, cy - 4), 2)
        pygame.draw.circle(surf, WHT, (cx + 3, cy - 4), 2)
        pygame.draw.circle(surf, (35, 15, 0), (cx - 3, cy - 4), 1)
        pygame.draw.circle(surf, (35, 15, 0), (cx + 3, cy - 4), 1)
    else:
        # Olhos X (assustado)
        for ox in [-4, 2]:
            pygame.draw.line(surf, BLK, (cx+ox, cy-6), (cx+ox+3, cy-3), 2)
            pygame.draw.line(surf, BLK, (cx+ox+3, cy-6), (cx+ox, cy-3), 2)

    # Orelhas longas (característica do Beagle)
    ear_c = color if color else BG_TN
    pygame.draw.ellipse(surf, ear_c, (cx - 12, cy - 9, 8, 13))
    pygame.draw.ellipse(surf, ear_c, (cx + 4,  cy - 9, 8, 13))

    # Patas
    paw_c = color if color else BG_TN
    pygame.draw.circle(surf, paw_c, (x + 9,  y + T - 5), 3)
    pygame.draw.circle(surf, paw_c, (x + T - 9, y + T - 5), 3)

    # Rabo curto
    pygame.draw.line(surf, BG_WH if not scared else body_c,
                     (cx, cy + 11), (cx - 5, cy + 7), 3)


def draw_tennis_ball(surf, cx, cy, radius):
    """Bolinha de tênis: círculo amarelo-verde com listra branca."""
    pygame.draw.circle(surf, DOT_C, (cx, cy), radius)
    # Listra branca curva
    if radius >= 4:
        pygame.draw.arc(surf, WHT,
                        (cx - radius + 1, cy - radius + 1,
                         radius * 2 - 2, radius * 2 - 2),
                        0.5, 2.4, max(1, radius // 4))


def _dir_name(dx, dy):
    return {(1,0): "right", (-1,0): "left", (0,-1): "up", (0,1): "down"}.get((dx,dy), "right")

# ═══════════════════════════════════════════════════════════
#  LABIRINTO
# ═══════════════════════════════════════════════════════════
class Maze:
    def __init__(self):
        self._orig = [row[:] for row in _MAP]
        self.grid  = [row[:] for row in _MAP]

    def reset(self):
        self.grid = [row[:] for row in self._orig]

    def is_wall(self, col, row):
        if not (0 <= col < COLS and 0 <= row < ROWS):
            return True
        return self.grid[row][col] == WALL

    def collect(self, col, row):
        t = self.grid[row][col]
        if t in (DOT, POWER):
            self.grid[row][col] = EMPTY
        return t

    def all_collected(self):
        return all(t not in (DOT, POWER) for row in self.grid for t in row)

    def draw(self, surf, flash_on):
        for r, row in enumerate(self.grid):
            for c, tile in enumerate(row):
                x, y = c * T, r * T
                rect = pygame.Rect(x, y, T, T)
                if tile == WALL:
                    pygame.draw.rect(surf, WALL_C, rect)
                elif tile == DOT:
                    draw_tennis_ball(surf, x + T // 2, y + T // 2, 4)
                elif tile == POWER:
                    if flash_on:
                        draw_tennis_ball(surf, x + T // 2, y + T // 2, 8)

# ═══════════════════════════════════════════════════════════
#  JOGADOR (Border Collie)
# ═══════════════════════════════════════════════════════════
class Player:
    def __init__(self, maze):
        self.maze = maze
        self.sc, self.sr = PLAYER_START
        self.col, self.row = self.sc, self.sr
        self.x = float(self.col * T)
        self.y = float(self.row * T)
        self.dx = self.dy = 0
        self._ndx = self._ndy = 0
        self.speed = SPD_P
        self.lives = LIVES
        self.score = 0
        self.powered = False
        self._ptimer = 0.0
        self._atimer = 0.0
        self._frame  = 0

    def direction(self, dx, dy):
        self._ndx, self._ndy = dx, dy

    def snap(self):
        self.x = float(self.col * T)
        self.y = float(self.row * T)

    def power_on(self, secs):
        self.powered  = True
        self._ptimer  = secs

    def update(self, dt):
        # Tentar mudar direção
        nc, nr = self.col + self._ndx, self.row + self._ndy
        if not self.maze.is_wall(nc, nr):
            self.dx, self.dy = self._ndx, self._ndy

        px = self.speed * T * dt
        self.x += self.dx * px
        self.y += self.dy * px

        nc2 = int(self.x / T + 0.5)
        nr2 = int(self.y / T + 0.5)
        if nc2 != self.col or nr2 != self.row:
            if not self.maze.is_wall(nc2, nr2):
                self.col, self.row = nc2, nr2
                return self.maze.collect(self.col, self.row)
            else:
                self.snap()
                self.dx = self.dy = 0
        return EMPTY

    def update_power(self, dt):
        if self.powered:
            self._ptimer -= dt
            if self._ptimer <= 0:
                self.powered  = False
                self._ptimer  = 0.0

    def update_anim(self, dt):
        self._atimer += dt
        if self._atimer >= 0.1:
            self._atimer = 0.0
            self._frame  = (self._frame + 1) % 3

    def die(self):
        self.lives -= 1
        self.col, self.row = self.sc, self.sr
        self.snap()
        self.dx = self.dy = 0
        self.powered = False
        self._ptimer = 0.0

    def dead(self):
        return self.lives <= 0

    def rect(self):
        return pygame.Rect(int(self.x) + 5, int(self.y) + 5, T - 10, T - 10)

    def draw(self, surf):
        draw_border_collie(surf,
                           int(self.x), int(self.y),
                           self.dx, self.dy,
                           self._frame, self.powered)

# ═══════════════════════════════════════════════════════════
#  BEAGLE (inimigo)
# ═══════════════════════════════════════════════════════════
DIRS = [(1,0),(-1,0),(0,1),(0,-1)]

class Beagle:
    def __init__(self, idx, maze):
        self.idx  = idx
        self.maze = maze
        sc, sr    = GHOST_STARTS[idx]
        self.sc, self.sr = sc, sr
        self.col, self.row = sc, sr
        self.x = float(sc * T)
        self.y = float(sr * T)
        self.dx, self.dy = 0, -1
        self.speed  = SPD_G
        self.scared = False
        self._stimer = 0.0
        self.locked  = False
        self._ltimer = 0.0
        self._ftimer = 0.0
        self._flash  = True

    def scare(self, secs):
        self.scared  = True
        self._stimer = secs

    def herd(self):
        """Enviado ao canil pelo Border Collie com power-up."""
        self.scared  = False
        self._stimer = 0.0
        self.locked  = True
        self._ltimer = KENNEL_S
        self.col, self.row = self.sc, self.sr
        self.x = float(self.sc * T)
        self.y = float(self.sr * T)
        self.dx, self.dy = 0, -1

    def reset(self):
        self.col, self.row = self.sc, self.sr
        self.x = float(self.sc * T)
        self.y = float(self.sr * T)
        self.dx, self.dy = 0, -1
        self.scared  = False
        self._stimer = 0.0
        self.locked  = False
        self._ltimer = 0.0

    def is_flashing(self):
        return self.scared and self._stimer <= 2.5

    def _target(self, player):
        if self.scared:
            # Fugir do jogador
            return (self.col + (self.col - player.col),
                    self.row + (self.row - player.row))
        if self.idx == 0:   # Biscuit: perseguir direto
            return player.col, player.row
        elif self.idx == 1: # Caramel: antecipar
            return player.col + player.dx * 4, player.row + player.dy * 4
        elif self.idx == 2: # Pepper: aleatório
            if random.random() < 0.5:
                return player.col, player.row
            return random.randint(0, COLS-1), random.randint(0, ROWS-1)
        else:               # Nugget: tático (persegue perto, foge longe)
            d = math.hypot(self.col - player.col, self.row - player.row)
            if d < 8:
                return COLS - 1 - player.col, ROWS - 1 - player.row
            return player.col, player.row

    def _choose_dir(self, player):
        tc, tr = self._target(player)
        best, best_d = (0, 0), float("inf")
        rev = (-self.dx, -self.dy)
        opts = [d for d in DIRS if not self.maze.is_wall(self.col+d[0], self.row+d[1])]
        if len(opts) > 1 and rev in opts:
            opts.remove(rev)
        random.shuffle(opts)
        for d in opts:
            nc, nr = self.col + d[0], self.row + d[1]
            dist = math.hypot(nc - tc, nr - tr)
            if dist < best_d:
                best_d, best = dist, d
        return best

    def update(self, dt, player):
        # Canil: esperar
        if self.locked:
            self._ltimer -= dt
            if self._ltimer <= 0:
                self.locked  = False
                self._ltimer = 0.0
            return

        # Timer de susto
        if self.scared:
            self._stimer -= dt
            if self._stimer <= 0:
                self.scared  = False
                self._stimer = 0.0

        # Flash
        self._ftimer += dt
        if self._ftimer >= 0.22:
            self._ftimer = 0.0
            self._flash  = not self._flash

        # Mover (snap-to-grid)
        snap_x = round(self.x / T) * T
        snap_y = round(self.y / T) * T
        if abs(self.x - snap_x) < 2 and abs(self.y - snap_y) < 2:
            self.x, self.y = float(snap_x), float(snap_y)
            self.col = snap_x // T
            self.row = snap_y // T
            nd = self._choose_dir(player)
            self.dx, self.dy = nd

        px = self.speed * T * dt
        self.x += self.dx * px
        self.y += self.dy * px

    def rect(self):
        return pygame.Rect(int(self.x) + 5, int(self.y) + 5, T - 10, T - 10)

    def draw(self, surf):
        draw_beagle(surf,
                    int(self.x), int(self.y),
                    ACCENTS[self.idx],
                    self.scared,
                    self.is_flashing() and not self._flash,
                    self.locked)

# ═══════════════════════════════════════════════════════════
#  HUD
# ═══════════════════════════════════════════════════════════
class HUD:
    def __init__(self):
        self.font_lg = None
        self.font_sm = None

    def init(self):
        self.font_lg = pygame.font.SysFont("monospace", 28, bold=True)
        self.font_sm = pygame.font.SysFont("monospace", 20)

    def draw(self, surf, score, lives, level):
        y = ROWS * T
        pygame.draw.rect(surf, (0, 0, 18), (0, y, SW, HUD_H))

        # Score
        s = self.font_lg.render(f"  {score:05d}", True, HUD_C)
        surf.blit(s, (8, y + 12))

        # Nível
        lv = self.font_sm.render(f"FASE {level}", True, HUD_C)
        surf.blit(lv, (SW // 2 - lv.get_width() // 2, y + 18))

        # Vidas (bolinhas de tênis)
        for i in range(lives):
            draw_tennis_ball(surf, SW - 20 - i * 26, y + HUD_H // 2, 7)

    def msg(self, surf, text, color):
        s = self.font_lg.render(text, True, color)
        surf.blit(s, (SW // 2 - s.get_width() // 2,
                      ROWS * T // 2 - s.get_height() // 2))
        sub = self.font_sm.render("ENTER para continuar", True, (160, 160, 160))
        surf.blit(sub, (SW // 2 - sub.get_width() // 2,
                        ROWS * T // 2 + 30))

# ═══════════════════════════════════════════════════════════
#  JOGO
# ═══════════════════════════════════════════════════════════
class State:
    PLAY    = "play"
    DYING   = "dying"
    WIN     = "win"
    OVER    = "over"


class Game:
    def __init__(self, surf):
        self.surf  = surf
        self.clock = pygame.time.Clock()
        self.level = 1
        self.state = State.PLAY
        self._timer = 0.0
        self._mult  = 1       # multiplicador de pontos por pastoreio consecutivo
        self._ftimer = 0.0    # timer para piscar power-ups
        self._flash  = True

        self.snd  = Sounds()
        self.snd.init()

        self.hud = HUD()
        self.hud.init()

        self._build_level()

    def _power_secs(self):
        return max(POWER_MIN, POWER_S - (self.level - 1) * POWER_DEC)

    def _ghost_speed(self):
        return SPD_G + (self.level - 1) * SPD_INC

    def _build_level(self):
        self.maze   = Maze()
        self.player = Player(self.maze)
        self.beagles = [Beagle(i, self.maze) for i in range(4)]
        for b in self.beagles:
            b.speed = self._ghost_speed()

    def _next_level(self):
        self.level += 1
        self.maze.reset()
        self.player.col, self.player.row = PLAYER_START
        self.player.snap()
        self.player.dx = self.player.dy = 0
        self.player.powered = False
        self._mult = 1
        for b in self.beagles:
            b.reset()
            b.speed = self._ghost_speed()
        self.state = State.PLAY

    def _full_reset(self):
        self.level = 1
        self._build_level()
        self.state = State.PLAY

    def events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if self.state == State.PLAY:
                    if   ev.key == pygame.K_RIGHT: self.player.direction(1, 0)
                    elif ev.key == pygame.K_LEFT:  self.player.direction(-1, 0)
                    elif ev.key == pygame.K_UP:    self.player.direction(0, -1)
                    elif ev.key == pygame.K_DOWN:  self.player.direction(0, 1)
                elif self.state in (State.WIN, State.OVER):
                    if ev.key == pygame.K_RETURN:
                        if self.state == State.WIN:
                            self._next_level()
                        else:
                            self.player.score = 0
                            self.player.lives = LIVES
                            self._full_reset()

    def update(self, dt):
        # Piscar power-ups
        self._ftimer += dt
        if self._ftimer >= 0.45:
            self._ftimer = 0.0
            self._flash  = not self._flash

        if self.state == State.DYING:
            self._timer -= dt
            if self._timer <= 0:
                self.state = State.PLAY
            return

        if self.state != State.PLAY:
            return

        prev_powered = self.player.powered
        prev_score   = self.player.score

        tile = self.player.update(dt)
        self.player.update_power(dt)
        self.player.update_anim(dt)

        if tile == DOT:
            self.player.score += PTS_DOT
            self.snd.play("dot")
        elif tile == POWER:
            self.player.score += PTS_PWR
            dur = self._power_secs()
            self.player.power_on(dur)
            self._mult = 1
            for b in self.beagles:
                b.scare(dur)
            self.snd.play("power")

        for b in self.beagles:
            b.update(dt, self.player)

            if b.rect().colliderect(self.player.rect()):
                if self.player.powered and b.scared:
                    self.player.score += PTS_HERD * self._mult
                    self._mult *= 2
                    b.herd()
                    self.snd.play("herd")
                elif not self.player.powered and not b.locked:
                    self.snd.play("die")
                    self.player.die()
                    for bb in self.beagles:
                        bb.reset()
                        bb.speed = self._ghost_speed()
                    self._mult = 1
                    if self.player.dead():
                        self.state = State.OVER
                    else:
                        self.state = State.DYING
                        self._timer = 1.5
                    break

        if self.maze.all_collected():
            self.snd.play("win")
            self.state = State.WIN
            self._timer = 2.5

    def draw(self):
        self.surf.fill(BG_C)
        self.maze.draw(self.surf, self._flash)
        self.player.draw(self.surf)
        for b in self.beagles:
            b.draw(self.surf)
        self.hud.draw(self.surf, self.player.score, self.player.lives, self.level)

        if self.state == State.WIN:
            self.hud.msg(self.surf, "  BOLA SALVA!  ", WIN_C)
        elif self.state == State.OVER:
            self.hud.msg(self.surf, "  APANHADO!  ", LOSE_C)

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update(dt)
            self.draw()

# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════
def main():
    pygame.init()
    surf = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption("BORDEPAC — Border Collie come bolinhas de tênis!")
    Game(surf).run()

if __name__ == "__main__":
    main()
