"""
======================================================================
VERTICAL SCROLLING SHOOTER - A simple 1945/Star Force style game
======================================================================

A beginner-friendly arcade shooter written with Pygame.
You fly upward (the world scrolls down past you), shooting enemies
that fly down toward you. Avoid their bullets and don't get rammed!

--------------------------------------------------------------------
AGREGADOS:
--------------------------------------------------------------------
- Un jefe (boss) que aparece cada cierto puntaje, con su propia
  barra de vida arriba de la pantalla.
- Bonificadores que caen de la parte superior de la pantalla: tiro doble, tiro triple y
  escudo. Duran un tiempo limitado y despues desaparecen solos.
- Colores institucionales del colegio (bordo, amarillo, rojo, blanco).
- El escudo del colegio se puede mostrar en la esquina de la pantalla,
  cargando una imagen desde una carpeta (ver ESCUDO_IMAGEN mas abajo).
--------------------------------------------------------------------

CONTROLS:
    Arrow keys or WASD .... Move ship
    Space or Z ............ Shoot
    P ..................... Pause
    R ..................... Restart (after game over)
    Esc ................... Quit

REQUIREMENTS:
    Python 3.8+
    pygame   (install with: pip install pygame)

The whole game lives in this single file and uses NO external
images, sounds, or fonts. Everything visual is drawn with Pygame's
basic shape primitives so you can read and tweak it easily.
"""

import math
import random
import sys

import pygame


# =====================================================================
# CONFIGURATION CONSTANTS
# =====================================================================
# Tweak any of these to change how the game looks and feels.
# They are grouped by topic so you can find what you want quickly.
# ---------------------------------------------------------------------

# --- Window / display -------------------------------------------------
SCREEN_WIDTH = 480           # Window width in pixels.  Try 360 for a
                             # narrower "arcade cabinet" feel, or 600+ for
                             # more room to dodge.
SCREEN_HEIGHT = 720           # Window height in pixels.  Vertical shooters
                              # traditionally use a tall (portrait) screen.
FPS = 60                      # Frames per second.  Higher = smoother, but
                              # more CPU.  All movement values below are
                              # tuned for 60 FPS.
WINDOW_TITLE = "Sky Striker"  # Text in the window's title bar.

# --- Colors (RGB tuples, 0..255) -------------------------------------
# Colores institucionales del colegio: bordo, amarillo, rojo y blanco.
# Cambia estos valores si queres recolorear todo el juego de una.
COLOR_BG_TOP    = (35, 5, 12)      # Bordo bien oscuro arriba.
COLOR_BG_BOTTOM = (10, 2, 5)       # Casi negro abajo (gradiente).
COLOR_STAR      = (255, 255, 255)  # Estrellas blancas.
COLOR_PLAYER    = (255, 205, 0)    # Nave del jugador: amarillo.
COLOR_PLAYER_HI = (255, 255, 255)  # Detalle de la cabina: blanco.
COLOR_PLAYER_THRUST = (230, 60, 30)  # Llama del motor: rojo/naranja.
COLOR_PLAYER_BULLET = (255, 225, 60)  # Disparos del jugador: amarillo.
COLOR_ENEMY     = (200, 30, 40)    # Enemigo comun: rojo.
COLOR_ENEMY_FAST = (230, 90, 70)   # Enemigo rapido: rojo mas claro.
COLOR_ENEMY_TANK = (120, 15, 35)   # Enemigo tanque: bordo.
COLOR_ENEMY_BULLET = (255, 130, 130)  # Disparos enemigos: rojo claro.
COLOR_EXPLOSION = (255, 200, 40)   # Particulas de explosion: amarillo.
COLOR_HUD_TEXT  = (255, 255, 255)  # Texto del HUD: blanco.
COLOR_HUD_DIM   = (210, 160, 165)  # Texto secundario del HUD.

# --- Colores del jefe (boss) y de los bonificadores ---------------------
COLOR_BOSS         = (120, 10, 30)   # Cuerpo del jefe: bordo.
COLOR_BOSS_DETALLE = (255, 205, 0)   # Detalle/armadura: amarillo.
COLOR_BOSS_BULLET  = (255, 60, 60)   # Balas del jefe: rojo.
COLOR_BOSS_BARRA_FONDO = (60, 10, 15)
COLOR_BOSS_BARRA_VIDA  = (220, 30, 40)

COLOR_BONI_BURBUJA = (255, 255, 255)  # Burbuja exterior de los bonificadores.
COLOR_BONI_DOBLE   = (255, 210, 0)    # Icono tiro doble: amarillo.
COLOR_BONI_TRIPLE  = (220, 30, 40)    # Icono tiro triple: rojo.
COLOR_BONI_ESCUDO  = (255, 255, 255)  # Icono escudo: blanco.
COLOR_ESCUDO_JUGADOR = (255, 220, 80)  # Circulo del escudo del jugador.

# --- Star field (background) -----------------------------------------
NUM_STARS = 80                # How many stars are visible at once.
                              # Lower this on slow machines.
STAR_SPEED_MIN = 1.0          # Slowest star speed (pixels/frame).
STAR_SPEED_MAX = 4.0          # Fastest star speed.  The variation is
                              # what creates the parallax depth effect.

# --- Player ship ------------------------------------------------------
PLAYER_WIDTH = 36             # Ship hitbox/visual width.
PLAYER_HEIGHT = 36            # Ship hitbox/visual height.
PLAYER_SPEED = 5.5            # Movement speed in pixels/frame.  Higher
                              # = twitchier; lower = more deliberate.
PLAYER_FIRE_COOLDOWN_MS = 180 # Milliseconds between shots.  Lower this
                              # for a rapid-fire feel.
PLAYER_START_LIVES = 3        # Extra lives on a fresh game.
PLAYER_INVULN_MS = 1500       # How long the player flashes and is
                              # immune after losing a life.

# --- Bullets ----------------------------------------------------------
PLAYER_BULLET_SPEED = 10.0    # How fast your shots travel upward.
PLAYER_BULLET_WIDTH = 4
PLAYER_BULLET_HEIGHT = 14

ENEMY_BULLET_SPEED = 4.5      # How fast enemy shots travel downward.
                              # Keep this well below player bullet speed
                              # so the player can outrun their own shots.
ENEMY_BULLET_RADIUS = 5

# --- Enemies ----------------------------------------------------------
# We have three "kinds" of enemies. Each kind has its own stats below.
# A new enemy spawns roughly every ENEMY_SPAWN_INTERVAL_MS milliseconds.
ENEMY_SPAWN_INTERVAL_MS = 800   # Lower = more enemies = harder.
ENEMY_SPAWN_JITTER_MS = 400     # Random extra time added to each spawn,
                                # so the rhythm doesn't feel mechanical.

# Probability weights for each enemy type. They don't need to sum to 1.0;
# they're relative to each other.
ENEMY_WEIGHT_BASIC = 6.0
ENEMY_WEIGHT_FAST  = 3.0
ENEMY_WEIGHT_TANK  = 1.0

# Basic enemy: average size, average speed, 1 HP.
ENEMY_BASIC_SIZE = 32
ENEMY_BASIC_SPEED = 2.2
ENEMY_BASIC_HP = 1
ENEMY_BASIC_SCORE = 100
ENEMY_BASIC_FIRE_CHANCE = 0.004  # Per-frame chance to shoot.  At 60 FPS,
                                 # 0.004 ≈ once every ~4 seconds per enemy.

# Fast enemy: small, quick, can't take a punch but rarely shoots.
ENEMY_FAST_SIZE = 24
ENEMY_FAST_SPEED = 4.0
ENEMY_FAST_HP = 1
ENEMY_FAST_SCORE = 200
ENEMY_FAST_FIRE_CHANCE = 0.002

# Tank enemy: big, slow, takes several hits, fires more often.
ENEMY_TANK_SIZE = 48
ENEMY_TANK_SPEED = 1.4
ENEMY_TANK_HP = 4
ENEMY_TANK_SCORE = 400
ENEMY_TANK_FIRE_CHANCE = 0.008

# Difficulty ramp: every DIFFICULTY_RAMP_SECONDS, spawn interval shrinks
# by DIFFICULTY_RAMP_FACTOR (multiplicative). Set RAMP_FACTOR to 1.0 to
# disable the ramp entirely.
DIFFICULTY_RAMP_SECONDS = 20
DIFFICULTY_RAMP_FACTOR = 0.92
ENEMY_SPAWN_INTERVAL_MIN_MS = 250  # Floor — never spawn faster than this.

# --- Explosions / particles ------------------------------------------
EXPLOSION_PARTICLES = 14      # Particles per explosion.  Bigger numbers
                              # look juicier but cost more performance.
EXPLOSION_SPEED_MIN = 1.0
EXPLOSION_SPEED_MAX = 4.0
EXPLOSION_LIFE_FRAMES = 30    # How many frames each particle lives.

# --- HUD --------------------------------------------------------------
HUD_FONT_SIZE = 22
HUD_MARGIN = 10               # Distance from screen edges, in pixels.

# --- Jefe (boss) ---------------------------------------------------------
# Aparece cada BOSS_PUNTAJE_INTERVALO puntos. Es mas grande y aguanta
# mas disparos que un enemigo comun. Tiene una barra de vida arriba
# de la pantalla mientras esta vivo.
BOSS_PUNTAJE_INTERVALO = 5000   # Cada cuantos puntos aparece un jefe.
BOSS_TAMANO = 110               # Mucho mas grande que el enemigo tanque (48).
BOSS_VIDA = 60                  # Cantidad de disparos que aguanta.
BOSS_PUNTOS = 1500              # Puntos que da al morir.
BOSS_ALTURA_QUIETO = 130        # Y donde se queda flotando.
BOSS_VELOCIDAD_ENTRADA = 1.6
BOSS_VELOCIDAD_PATRULLA = 1.6
BOSS_COOLDOWN_DISPARO_MS = 900  # Cada cuanto dispara su tanda de balas.
BOSS_CANTIDAD_BALAS = 5         # Balas por tanda (en abanico).
BOSS_VELOCIDAD_BALA = 4.0
BOSS_BARRA_ANCHO = SCREEN_WIDTH - 40
BOSS_BARRA_ALTO = 16

# --- Bonificadores (power-ups) -------------------------------------------
# Caen desde arriba, igual que los enemigos, y el jugador los agarra
# tocandolos con la nave. Si no los agarra, desaparecen solos despues
# de un ratito (BONI_TIEMPO_VIDA_MS): asi nunca quedan "colgados".
BONI_TAMANO = 30
BONI_VELOCIDAD_CAIDA = 2.2
BONI_TIEMPO_VIDA_MS = 7000          # Tiempo que dura la burbuja en pantalla.
BONI_SPAWN_INTERVALO_MS = 9000      # Cada cuanto aparece uno nuevo, +/- jitter.
BONI_SPAWN_JITTER_MS = 4000
BONI_PESO_DOBLE = 3.0
BONI_PESO_TRIPLE = 1.5
BONI_PESO_ESCUDO = 2.0

BONI_DURACION_ARMA_MS = 12000    # Cuanto dura el tiro doble/triple una vez agarrado.
BONI_DURACION_ESCUDO_MS = 15000  # Cuanto dura el escudo una vez agarrado.
BONI_SEPARACION_BALAS = 9        # Separacion entre balas en tiro doble/triple.

# --- Escudo del colegio (imagen) -----------------------------------------
ESCUDO_IMAGEN = "escudo_escuela.jpg"
ESCUDO_TAMANO = 48   # Tamaño (ancho y alto) al que se escala la imagen.

# =====================================================================
# END OF CONFIGURATION
# =====================================================================


# ---------------------------------------------------------------------
# Helper: pick a weighted random choice.
# ---------------------------------------------------------------------
# random.choices does this for us, but a tiny wrapper makes the calling
# code easier to read.
def weighted_choice(options_with_weights):
    """Return one option chosen by weight.

    `options_with_weights` is a list of (option, weight) tuples.
    """
    options = [pair[0] for pair in options_with_weights]
    weights = [pair[1] for pair in options_with_weights]
    return random.choices(options, weights=weights, k=1)[0]


# ---------------------------------------------------------------------
# Star: a single twinkling dot in the parallax background.
# ---------------------------------------------------------------------
class Star:
    """One pixel of the scrolling star field.

    Stars at different speeds create a sense of depth (parallax):
    fast stars feel close, slow stars feel far away.
    """
    def __init__(self):
        # Pick a random position and a random speed.
        # We re-randomize on respawn (when the star scrolls off the bottom).
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.speed = random.uniform(STAR_SPEED_MIN, STAR_SPEED_MAX)
        # Faster stars are drawn brighter to enhance the depth illusion.
        brightness_ratio = (self.speed - STAR_SPEED_MIN) / max(
            0.0001, (STAR_SPEED_MAX - STAR_SPEED_MIN)
        )
        gray = int(120 + 135 * brightness_ratio)  # 120..255
        self.color = (gray, gray, gray)

    def update(self):
        # Move down by the star's speed each frame.
        self.y += self.speed
        # Wrap to the top once we leave the screen.
        if self.y > SCREEN_HEIGHT:
            self.y = 0.0
            self.x = random.uniform(0, SCREEN_WIDTH)
            # Re-pick speed/brightness for variety.
            self.speed = random.uniform(STAR_SPEED_MIN, STAR_SPEED_MAX)

    def draw(self, surface):
        # A 1- or 2-pixel rectangle is cheaper than a circle and looks fine.
        size = 1 if self.speed < (STAR_SPEED_MIN + STAR_SPEED_MAX) / 2 else 2
        surface.fill(self.color, (int(self.x), int(self.y), size, size))


# ---------------------------------------------------------------------
# Bullet: used for both the player's shots and enemy shots.
# ---------------------------------------------------------------------
class Bullet:
    """A simple projectile that moves in a straight line.

    `vy` (vertical velocity) is negative for upward (player) shots
    and positive for downward (enemy) shots. The same class handles both.
    """
    def __init__(self, x, y, vy, color, is_player_bullet, vx=0.0):
        self.x = x
        self.y = y
        self.vy = vy
        self.vx = vx  # Normalmente 0 (recto). El jefe la usa para tirar en angulo.
        self.color = color
        self.is_player_bullet = is_player_bullet
        self.alive = True
        # Player bullets are little rectangles; enemy bullets are circles.
        # That makes it easier for the player to distinguish friend from foe
        # at a glance — a small but important readability trick.
        if is_player_bullet:
            self.rect = pygame.Rect(
                int(x - PLAYER_BULLET_WIDTH / 2),
                int(y - PLAYER_BULLET_HEIGHT / 2),
                PLAYER_BULLET_WIDTH,
                PLAYER_BULLET_HEIGHT,
            )
        else:
            r = ENEMY_BULLET_RADIUS
            self.rect = pygame.Rect(int(x - r), int(y - r), r * 2, r * 2)

    def update(self):
        self.y += self.vy
        self.x += self.vx
        # Sync the collision rectangle to the new position.
        self.rect.centery = int(self.y)
        self.rect.centerx = int(self.x)
        # Mark dead once off-screen (top, bottom, or a los costados).
        if self.y < -20 or self.y > SCREEN_HEIGHT + 20:
            self.alive = False
        if self.x < -20 or self.x > SCREEN_WIDTH + 20:
            self.alive = False

    def draw(self, surface):
        if self.is_player_bullet:
            # A bright rectangle with a slightly lighter center for "pew" feel.
            pygame.draw.rect(surface, self.color, self.rect, border_radius=2)
        else:
            pygame.draw.circle(
                surface, self.color, (int(self.x), int(self.y)),
                ENEMY_BULLET_RADIUS,
            )
            # Inner highlight makes enemy bullets pop against dark sky.
            pygame.draw.circle(
                surface, (255, 230, 240),
                (int(self.x), int(self.y)),
                max(1, ENEMY_BULLET_RADIUS - 2),
            )


# ---------------------------------------------------------------------
# Player: the ship you control.
# ---------------------------------------------------------------------
class Player:
    """The player's ship.

    Holds position, lives, and shooting cooldown. Also handles brief
    invulnerability after being hit, so the player isn't instantly killed
    again after respawning at the center.
    """
    def __init__(self):
        # Start near the bottom-center.
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT - PLAYER_HEIGHT * 1.5
        self.lives = PLAYER_START_LIVES
        self.last_shot_time_ms = 0
        # When pygame.time.get_ticks() < invuln_until_ms, we ignore hits
        # and flicker the sprite to signal "just respawned".
        self.invuln_until_ms = pygame.time.get_ticks() + PLAYER_INVULN_MS

        # --- Bonificadores del jugador ---------------------------------
        # nivel_arma: 1 = tiro normal, 2 = tiro doble, 3 = tiro triple.
        # Cuando pasa arma_hasta_ms, vuelve solo a nivel 1.
        self.nivel_arma = 1
        self.arma_hasta_ms = 0
        # escudo_hasta_ms: mientras now_ms sea menor a esto, el jugador
        # tiene escudo activo. Se gasta apenas recibe un golpe.
        self.escudo_hasta_ms = 0

        # The collision rectangle. We center it on (x, y) and update each
        # frame inside `update`.
        self.rect = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.rect.center = (int(self.x), int(self.y))

    def is_invulnerable(self, now_ms):
        return now_ms < self.invuln_until_ms

    def tiene_escudo(self, now_ms):
        return now_ms < self.escudo_hasta_ms

    def agarrar_bonificador(self, tipo, now_ms):
        """Se llama cuando el jugador toca una burbuja de bonificador."""
        if tipo == "doble":
            self.nivel_arma = 2
            self.arma_hasta_ms = now_ms + BONI_DURACION_ARMA_MS
        elif tipo == "triple":
            self.nivel_arma = 3
            self.arma_hasta_ms = now_ms + BONI_DURACION_ARMA_MS
        elif tipo == "escudo":
            self.escudo_hasta_ms = now_ms + BONI_DURACION_ESCUDO_MS

    def update(self, keys, now_ms):
        # --- Movement --------------------------------------------------
        # Read both arrow keys and WASD so users can pick.
        dx = 0.0
        dy = 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            dx -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1.0
        if keys[pygame.K_UP]    or keys[pygame.K_w]:
            dy -= 1.0
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]:
            dy += 1.0

        # Diagonal movement should not be faster than straight movement.
        # We normalize the (dx, dy) vector so its length is 1, then scale
        # by PLAYER_SPEED. This is a classic 2D-game gotcha worth knowing!
        if dx != 0.0 or dy != 0.0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

        self.x += dx * PLAYER_SPEED
        self.y += dy * PLAYER_SPEED

        # Keep the ship inside the play area.
        half_w = PLAYER_WIDTH / 2
        half_h = PLAYER_HEIGHT / 2
        if self.x < half_w:
            self.x = half_w
        if self.x > SCREEN_WIDTH - half_w:
            self.x = SCREEN_WIDTH - half_w
        if self.y < half_h:
            self.y = half_h
        if self.y > SCREEN_HEIGHT - half_h:
            self.y = SCREEN_HEIGHT - half_h

        self.rect.center = (int(self.x), int(self.y))

        # Si el tiro doble/triple ya se vencio, volvemos al tiro normal.
        if self.nivel_arma > 1 and now_ms >= self.arma_hasta_ms:
            self.nivel_arma = 1

    def can_shoot(self, now_ms):
        return (now_ms - self.last_shot_time_ms) >= PLAYER_FIRE_COOLDOWN_MS

    def shoot(self, bullets, now_ms):
        """Dispara 1, 2 o 3 balas segun el nivel de arma actual."""
        if not self.can_shoot(now_ms):
            return
        self.last_shot_time_ms = now_ms
        nose_y = self.y - PLAYER_HEIGHT / 2

        if self.nivel_arma == 3:
            offsets = (-BONI_SEPARACION_BALAS, 0, BONI_SEPARACION_BALAS)
        elif self.nivel_arma == 2:
            offsets = (-BONI_SEPARACION_BALAS / 2, BONI_SEPARACION_BALAS / 2)
        else:
            offsets = (0,)

        for dx in offsets:
            bullets.append(Bullet(
                x=self.x + dx,
                y=nose_y,
                vy=-PLAYER_BULLET_SPEED,    # Negative = moving UP the screen.
                color=COLOR_PLAYER_BULLET,
                is_player_bullet=True,
            ))

    def hit(self, now_ms):
        """Called when an enemy or enemy bullet touches the ship.
        """
        if self.is_invulnerable(now_ms):
            return "invuln"

        if self.tiene_escudo(now_ms):
            # El escudo recibe un impacto y se rompe.
            self.escudo_hasta_ms = 0
            self.invuln_until_ms = now_ms + 400  # Un respiro cortito.
            return "escudo"

        self.lives -= 1
        # Re-grant invulnerability so the next frame doesn't kill us again.
        self.invuln_until_ms = now_ms + PLAYER_INVULN_MS
        # Recenter the ship so the player has a moment to reorient.
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT - PLAYER_HEIGHT * 1.5
        self.rect.center = (int(self.x), int(self.y))
        return "hit"

    def draw(self, surface, now_ms):
        # Flicker while invulnerable: skip drawing every other ~80 ms.
        if self.is_invulnerable(now_ms):
            # Integer-divide the time to get a slow on/off cycle.
            if (now_ms // 80) % 2 == 0:
                return  # Skip this frame's draw; ship "blinks".

        cx, cy = int(self.x), int(self.y)
        hw = PLAYER_WIDTH // 2
        hh = PLAYER_HEIGHT // 2

        # Engine flame behind the ship — drawn first so it sits *under* the body.
        # The flame jitters a few pixels each frame for an animated feel.
        flame_jitter = random.randint(-2, 2)
        flame_points = [
            (cx - 6, cy + hh - 2),
            (cx + 6, cy + hh - 2),
            (cx,     cy + hh + 10 + flame_jitter),
        ]
        pygame.draw.polygon(surface, COLOR_PLAYER_THRUST, flame_points)

        # The hull: a triangle pointing UP (since we shoot upward).
        hull_points = [
            (cx,         cy - hh),       # Nose
            (cx - hw,    cy + hh - 4),   # Bottom-left
            (cx + hw,    cy + hh - 4),   # Bottom-right
        ]
        pygame.draw.polygon(surface, COLOR_PLAYER, hull_points)

        # Wings: two small rectangles sticking out the sides.
        pygame.draw.rect(surface, COLOR_PLAYER,
                         (cx - hw - 4, cy + 2, 6, 10))
        pygame.draw.rect(surface, COLOR_PLAYER,
                         (cx + hw - 2, cy + 2, 6, 10))

        # Cockpit highlight: a small circle near the nose.
        pygame.draw.circle(surface, COLOR_PLAYER_HI, (cx, cy - 2), 4)

        # Si tiene escudo activo, dibujamos un circulo alrededor de la nave.
        if self.tiene_escudo(now_ms):
            radio = max(PLAYER_WIDTH, PLAYER_HEIGHT) // 2 + 10
            pygame.draw.circle(surface, COLOR_ESCUDO_JUGADOR, (cx, cy), radio, width=3)


# ---------------------------------------------------------------------
# Enemy: comes in three flavors driven by `kind`.
# ---------------------------------------------------------------------
class Enemy:
    """An enemy ship that flies down and occasionally shoots.

    `kind` is one of "basic", "fast", "tank". Each kind reads its own
    constants from the configuration block above. Centralizing them
    there means you can rebalance the game without touching this code.
    """
    def __init__(self, kind):
        self.kind = kind
        if kind == "fast":
            self.size = ENEMY_FAST_SIZE
            self.speed = ENEMY_FAST_SPEED
            self.hp = ENEMY_FAST_HP
            self.score = ENEMY_FAST_SCORE
            self.fire_chance = ENEMY_FAST_FIRE_CHANCE
            self.color = COLOR_ENEMY_FAST
        elif kind == "tank":
            self.size = ENEMY_TANK_SIZE
            self.speed = ENEMY_TANK_SPEED
            self.hp = ENEMY_TANK_HP
            self.score = ENEMY_TANK_SCORE
            self.fire_chance = ENEMY_TANK_FIRE_CHANCE
            self.color = COLOR_ENEMY_TANK
        elif kind == "jefe":
            # El jefe (boss): es mucho mas grande, mucha mas vida, y se
            # mueve/dispara distinto
            self.size = BOSS_TAMANO
            self.speed = BOSS_VELOCIDAD_ENTRADA
            self.hp = BOSS_VIDA
            self.max_hp = BOSS_VIDA
            self.score = BOSS_PUNTOS
            self.fire_chance = 0  # El jefe no usa el disparo al azar normal.
            self.color = COLOR_BOSS
            self.patrullando = False
            self.direccion = random.choice((-1, 1))
            self.proximo_disparo_ms = 0
        else:  # "basic"
            self.size = ENEMY_BASIC_SIZE
            self.speed = ENEMY_BASIC_SPEED
            self.hp = ENEMY_BASIC_HP
            self.score = ENEMY_BASIC_SCORE
            self.fire_chance = ENEMY_BASIC_FIRE_CHANCE
            self.color = COLOR_ENEMY

        # Spawn at a random horizontal position, just above the screen.
        half = self.size / 2
        self.x = random.uniform(half, SCREEN_WIDTH - half)
        self.y = -half

        # Light side-to-side wobble so enemies don't fly in straight lines.
        # `wobble_phase` is just the starting angle of the sine wave.
        self.wobble_phase = random.uniform(0, math.tau)
        self.wobble_amount = random.uniform(0.5, 1.5)
        # `age_frames` drives the wobble over time.
        self.age_frames = 0

        self.alive = True
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = (int(self.x), int(self.y))

    def update(self, bullets):
        if self.kind == "jefe":
            self._actualizar_jefe(bullets)
            return

        # Move straight down + a little sideways sine-wave wobble.
        self.age_frames += 1
        self.y += self.speed
        wobble_dx = math.sin(self.age_frames * 0.05 + self.wobble_phase)
        self.x += wobble_dx * self.wobble_amount

        # Stay on-screen horizontally (for tanks especially, the sprite is wide).
        half = self.size / 2
        if self.x < half:
            self.x = half
        if self.x > SCREEN_WIDTH - half:
            self.x = SCREEN_WIDTH - half

        self.rect.center = (int(self.x), int(self.y))

        # If we've left the bottom, mark dead so the game removes us.
        if self.y - half > SCREEN_HEIGHT:
            self.alive = False
            return

        # Random chance to shoot. Only shoot once we're actually on-screen,
        # so the player isn't surprised by bullets from invisible enemies.
        if self.y > 0 and random.random() < self.fire_chance:
            bullets.append(Bullet(
                x=self.x,
                y=self.y + half,
                vy=ENEMY_BULLET_SPEED,   # Positive = moving DOWN.
                color=COLOR_ENEMY_BULLET,
                is_player_bullet=False,
            ))

    def _actualizar_jefe(self, bullets):
        """Movimiento y disparo del jefe: entra, flota y dispara en abanico."""
        half = self.size / 2

        if not self.patrullando:
            # Primero baja hasta la altura donde se va a quedar flotando.
            self.y += self.speed
            if self.y >= BOSS_ALTURA_QUIETO:
                self.y = BOSS_ALTURA_QUIETO
                self.patrullando = True
        else:
            # Se mueve para los costados, rebotando en los bordes.
            self.x += self.direccion * BOSS_VELOCIDAD_PATRULLA
            if self.x < half:
                self.x = half
                self.direccion = 1
            elif self.x > SCREEN_WIDTH - half:
                self.x = SCREEN_WIDTH - half
                self.direccion = -1

            now_ms = pygame.time.get_ticks()
            if now_ms >= self.proximo_disparo_ms:
                self._disparar_abanico(bullets)
                self.proximo_disparo_ms = now_ms + BOSS_COOLDOWN_DISPARO_MS

        self.rect.center = (int(self.x), int(self.y))

    def _disparar_abanico(self, bullets):
        """Tira varias balas juntas en forma de abanico hacia abajo."""
        cantidad = BOSS_CANTIDAD_BALAS
        angulo_total = 70  # Grados de ancho del abanico.
        angulo_inicial = 90 - angulo_total / 2  # 90 = derecho hacia abajo.
        paso = angulo_total / (cantidad - 1)

        for i in range(cantidad):
            angulo = math.radians(angulo_inicial + i * paso)
            vx = math.cos(angulo) * BOSS_VELOCIDAD_BALA
            vy = math.sin(angulo) * BOSS_VELOCIDAD_BALA
            bullets.append(Bullet(
                x=self.x, y=self.y + self.size / 2,
                vy=vy, vx=vx,
                color=COLOR_BOSS_BULLET,
                is_player_bullet=False,
            ))

    def take_damage(self, amount=1):
        """Subtract HP and return True if the enemy just died."""
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        half = self.size // 2

        if self.kind == "jefe":
            # Forma mas ancha y grande para demostrar que es el jefe.
            body = [
                (cx,               cy + half),
                (cx - half,        cy + half * 0.2),
                (cx - half * 0.6,  cy - half),
                (cx + half * 0.6,  cy - half),
                (cx + half,        cy + half * 0.2),
            ]
            pygame.draw.polygon(surface, self.color, body)
            pygame.draw.rect(
                surface, COLOR_BOSS_DETALLE,
                (cx - half + 6, cy - 6, self.size - 12, 12), border_radius=4,
            )
            pygame.draw.circle(surface, (30, 0, 10), (cx, cy - half // 3), 10)
            return

        # Body: a triangle pointing DOWN (toward the player).
        body = [
            (cx,         cy + half),       # Bottom point
            (cx - half,  cy - half + 4),   # Top-left
            (cx + half,  cy - half + 4),   # Top-right
        ]
        pygame.draw.polygon(surface, self.color, body)

        # Tank enemies get an extra "armor band" rectangle for visual weight.
        if self.kind == "tank":
            pygame.draw.rect(
                surface, (40, 20, 60),
                (cx - half + 4, cy - 4, self.size - 8, 8),
            )

        # A small dark "cockpit" circle near the top.
        pygame.draw.circle(surface, (30, 0, 30), (cx, cy - half + 8), 4)


# ---------------------------------------------------------------------
# PowerUp: una burbuja de bonificador que cae del cielo.
# ---------------------------------------------------------------------
class PowerUp:
    """Bonificador que cae desde arriba de la pantalla.

    `kind` puede ser "doble", "triple" o "escudo". Tiene un tiempo
    limite en pantalla (BONI_TIEMPO_VIDA_MS): si el jugador no lo
    agarra a tiempo, desaparece solo.
    """
    def __init__(self, kind):
        self.kind = kind
        self.size = BONI_TAMANO
        half = self.size / 2
        self.x = random.uniform(half + 4, SCREEN_WIDTH - half - 4)
        self.y = -half
        self.speed = BONI_VELOCIDAD_CAIDA

        # Tiempo en el que aparecio: si pasa mucho tiempo, desaparece.
        self.nacio_ms = pygame.time.get_ticks()

        self.alive = True
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = (int(self.x), int(self.y))

    def update(self):
        self.y += self.speed
        self.rect.center = (int(self.x), int(self.y))

        now_ms = pygame.time.get_ticks()
        # Se muere si se cae de la pantalla o si ya paso su tiempo de vida.
        if self.y - self.size / 2 > SCREEN_HEIGHT:
            self.alive = False
        if now_ms - self.nacio_ms > BONI_TIEMPO_VIDA_MS:
            self.alive = False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        radio = self.size // 2

        # Burbuja exterior (circulo blanco con contorno).
        pygame.draw.circle(surface, COLOR_BONI_BURBUJA, (cx, cy), radio, width=2)

        # Icono de adentro, distinto para cada tipo de bonificador.
        if self.kind == "doble":
            for dx in (-5, 5):
                pygame.draw.rect(surface, COLOR_BONI_DOBLE,
                                  (cx + dx - 2, cy - 8, 4, 16), border_radius=2)
        elif self.kind == "triple":
            for dx in (-8, 0, 8):
                pygame.draw.rect(surface, COLOR_BONI_TRIPLE,
                                  (cx + dx - 2, cy - 8, 4, 16), border_radius=2)
        else:  # "escudo"
            puntos = [
                (cx,     cy - 9), (cx - 8, cy - 4), (cx - 8, cy + 4),
                (cx,     cy + 10), (cx + 8, cy + 4), (cx + 8, cy - 4),
            ]
            pygame.draw.polygon(surface, COLOR_BONI_ESCUDO, puntos)


# ---------------------------------------------------------------------
# Particle: a single dot in an explosion.
# ---------------------------------------------------------------------
class Particle:
    """One spark of an explosion.

    Particles are intentionally simple — just position, velocity, and a
    countdown timer. When the timer hits zero, they're removed.
    """
    def __init__(self, x, y, color_base=None):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(EXPLOSION_SPEED_MIN, EXPLOSION_SPEED_MAX)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = EXPLOSION_LIFE_FRAMES
        # A tiny size variation makes the explosion look less uniform.
        self.size = random.randint(2, 4)
        # Slight color variation per particle. Si no mandan color_base,
        # usa el color de explosion normal (naranja/amarillo).
        base = color_base if color_base is not None else COLOR_EXPLOSION
        r = min(255, base[0] + random.randint(-20, 20))
        g = min(255, base[1] + random.randint(-30, 30))
        b = min(255, base[2] + random.randint(-20, 20))
        self.color = (max(0, r), max(0, g), max(0, b))

    @property
    def alive(self):
        return self.life > 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # A bit of "drag" so particles slow to a halt instead of flying off.
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1

    def draw(self, surface):
        # Particles fade out by shrinking near end-of-life.
        # (We could also fade alpha, but that's slower and not needed here.)
        s = self.size if self.life > 8 else max(1, self.size - 1)
        surface.fill(self.color, (int(self.x), int(self.y), s, s))


# ---------------------------------------------------------------------
# Game: the top-level state machine.
# ---------------------------------------------------------------------
class Game:
    """Owns every entity and the main loop's per-frame logic.

    Putting the loop body in methods keeps `main()` short and makes it
    easy for a beginner to find a specific feature (e.g. "where do
    collisions happen?" -> `_handle_collisions`).
    """
    # State constants — using plain strings keeps them readable when printed.
    STATE_PLAYING = "playing"
    STATE_PAUSED = "paused"
    STATE_GAME_OVER = "game_over"

    def __init__(self, screen, font_big, font_small):
        self.screen = screen
        self.font_big = font_big
        self.font_small = font_small


        self.escudo_img = None
        try:
            img = pygame.image.load(ESCUDO_IMAGEN).convert_alpha()
            self.escudo_img = pygame.transform.smoothscale(
                img, (ESCUDO_TAMANO, ESCUDO_TAMANO)
            )
        except (pygame.error, FileNotFoundError):
            self.escudo_img = None

        self.reset()

    def reset(self):
        """Start (or restart) a fresh game."""
        self.state = Game.STATE_PLAYING
        self.score = 0

        self.player = Player()
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.particles = []
        self.powerups = []

        self.stars = [Star() for _ in range(NUM_STARS)]

        # Spawn timing:
        now_ms = pygame.time.get_ticks()
        self.next_enemy_spawn_ms = now_ms + ENEMY_SPAWN_INTERVAL_MS
        self.current_spawn_interval_ms = ENEMY_SPAWN_INTERVAL_MS
        self.last_difficulty_ramp_ms = now_ms
        self.start_ms = now_ms

        # Bonificadores: cuando aparece el proximo.
        self.next_powerup_spawn_ms = now_ms + BONI_SPAWN_INTERVALO_MS

        # Jefe: puntaje al que tiene que llegar el score para que aparezca.
        self.next_boss_score = BOSS_PUNTAJE_INTERVALO
        self.boss = None  # Referencia al jefe vivo, si hay uno.

    # -----------------------------------------------------------------
    # Spawning
    # -----------------------------------------------------------------
    def _maybe_spawn_enemy(self, now_ms):
        if now_ms < self.next_enemy_spawn_ms:
            return
        if self.boss is not None:
            # Mientras el jefe esta vivo, no aparecen enemigos comunes.
            self.next_enemy_spawn_ms = now_ms + 500
            return
        kind = weighted_choice([
            ("basic", ENEMY_WEIGHT_BASIC),
            ("fast",  ENEMY_WEIGHT_FAST),
            ("tank",  ENEMY_WEIGHT_TANK),
        ])
        self.enemies.append(Enemy(kind))
        # Schedule the next spawn with a little randomness.
        jitter = random.randint(-ENEMY_SPAWN_JITTER_MS, ENEMY_SPAWN_JITTER_MS)
        self.next_enemy_spawn_ms = (
            now_ms + max(50, self.current_spawn_interval_ms + jitter)
        )

    def _maybe_ramp_difficulty(self, now_ms):
        # Every DIFFICULTY_RAMP_SECONDS, shrink the spawn interval.
        if now_ms - self.last_difficulty_ramp_ms < DIFFICULTY_RAMP_SECONDS * 1000:
            return
        self.last_difficulty_ramp_ms = now_ms
        new_interval = self.current_spawn_interval_ms * DIFFICULTY_RAMP_FACTOR
        self.current_spawn_interval_ms = max(
            ENEMY_SPAWN_INTERVAL_MIN_MS, new_interval
        )

    def _spawn_explosion(self, x, y, cantidad=EXPLOSION_PARTICLES, color=None):
        for _ in range(cantidad):
            self.particles.append(Particle(x, y, color_base=color))

    def _maybe_spawn_powerup(self, now_ms):
        if now_ms < self.next_powerup_spawn_ms:
            return
        kind = weighted_choice([
            ("doble",  BONI_PESO_DOBLE),
            ("triple", BONI_PESO_TRIPLE),
            ("escudo", BONI_PESO_ESCUDO),
        ])
        self.powerups.append(PowerUp(kind))
        jitter = random.randint(-BONI_SPAWN_JITTER_MS, BONI_SPAWN_JITTER_MS)
        self.next_powerup_spawn_ms = now_ms + max(1000, BONI_SPAWN_INTERVALO_MS + jitter)

    def _maybe_spawn_boss(self):
        # Solo puede haber un jefe a la vez.
        if self.boss is not None:
            return
        if self.score < self.next_boss_score:
            return
        jefe = Enemy("jefe")
        self.boss = jefe
        self.enemies.append(jefe)
        self.next_boss_score += BOSS_PUNTAJE_INTERVALO

    # -----------------------------------------------------------------
    # Input
    # -----------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Pause toggling
            if event.key == pygame.K_p and self.state == Game.STATE_PLAYING:
                self.state = Game.STATE_PAUSED
            elif event.key == pygame.K_p and self.state == Game.STATE_PAUSED:
                self.state = Game.STATE_PLAYING
            # Restart after game over
            elif event.key == pygame.K_r and self.state == Game.STATE_GAME_OVER:
                self.reset()

    def _handle_continuous_input(self, now_ms):
        keys = pygame.key.get_pressed()
        self.player.update(keys, now_ms)
        # Holding Space or Z = continuous fire (rate-limited by cooldown).
        if keys[pygame.K_SPACE] or keys[pygame.K_z]:
            self.player.shoot(self.player_bullets, now_ms)

    # -----------------------------------------------------------------
    # Per-frame update
    # -----------------------------------------------------------------
    def update(self):
        if self.state != Game.STATE_PLAYING:
            return  # Pause and game-over freeze the world.

        now_ms = pygame.time.get_ticks()

        # 1) Background
        for star in self.stars:
            star.update()

        # 2) Input + player movement / shooting
        self._handle_continuous_input(now_ms)

        # 3) Bullets
        for b in self.player_bullets:
            b.update()
        for b in self.enemy_bullets:
            b.update()

        # 4) Enemies
        self._maybe_ramp_difficulty(now_ms)
        self._maybe_spawn_boss()
        self._maybe_spawn_enemy(now_ms)
        for e in self.enemies:
            e.update(self.enemy_bullets)

        # 4b) Bonificadores
        self._maybe_spawn_powerup(now_ms)
        for pu in self.powerups:
            pu.update()

        # 5) Particles
        for p in self.particles:
            p.update()

        # 6) Collisions
        self._handle_collisions(now_ms)

        # 7) Cull dead objects.
        # Doing this *after* collision keeps the per-frame logic tidy:
        # collisions just flip `alive` flags or call hit/take_damage.
        self.player_bullets = [b for b in self.player_bullets if b.alive]
        self.enemy_bullets  = [b for b in self.enemy_bullets  if b.alive]
        self.enemies        = [e for e in self.enemies        if e.alive]
        self.particles      = [p for p in self.particles      if p.alive]
        self.powerups       = [pu for pu in self.powerups     if pu.alive]

        # Si el jefe ya murio, nos olvidamos de la referencia (asi vuelve
        # a aparecer el spawn normal de enemigos y se esconde la barra).
        if self.boss is not None and not self.boss.alive:
            self.boss = None

        # 8) Game over check
        if self.player.lives <= 0:
            self.state = Game.STATE_GAME_OVER

    def _handle_collisions(self, now_ms):
        # --- Player bullets vs enemies --------------------------------
        # rect-vs-rect collision is plenty for an arcade shooter; no need
        # for pixel-perfect masks.
        for bullet in self.player_bullets:
            if not bullet.alive:
                continue
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                if bullet.rect.colliderect(enemy.rect):
                    bullet.alive = False
                    died = enemy.take_damage(1)
                    if died:
                        self.score += enemy.score
                        if enemy.kind == "jefe":
                            # Explosion mas grande para el jefe.
                            self._spawn_explosion(enemy.x, enemy.y, cantidad=EXPLOSION_PARTICLES * 3)
                        else:
                            self._spawn_explosion(enemy.x, enemy.y)
                    break  # One bullet, one hit.

        # --- Enemy bullets vs player ----------------------------------
        for bullet in self.enemy_bullets:
            if not bullet.alive:
                continue
            if bullet.rect.colliderect(self.player.rect):
                bullet.alive = False
                self._golpear_jugador(now_ms)

        # --- Enemies vs player (ramming) ------------------------------
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            if enemy.rect.colliderect(self.player.rect):
                self._golpear_jugador(now_ms)
                # Ramming kills the enemy too — feels fair and clears the
                # screen. El jefe es demasiado grande para morir de un
                # choque, asi que solo le hace daño al jugador.
                if enemy.kind != "jefe":
                    enemy.alive = False
                    self.score += enemy.score // 2
                    self._spawn_explosion(enemy.x, enemy.y)

        # --- Bonificadores vs jugador (agarrarlos) ----------------------
        for powerup in self.powerups:
            if not powerup.alive:
                continue
            if powerup.rect.colliderect(self.player.rect):
                powerup.alive = False
                self.player.agarrar_bonificador(powerup.kind, now_ms)

    def _golpear_jugador(self, now_ms):
        """Le pega al jugador y dibuja el efecto que corresponda."""
        resultado = self.player.hit(now_ms)
        if resultado == "hit":
            self._spawn_explosion(self.player.x, self.player.y)
        elif resultado == "escudo":
            # Animacion de que el escudo se rompe (particulas blancas).
            self._spawn_explosion(self.player.x, self.player.y, color=COLOR_ESCUDO_JUGADOR)

    # -----------------------------------------------------------------
    # Drawing
    # -----------------------------------------------------------------
    def draw(self):
        self._draw_background()

        for star in self.stars:
            star.draw(self.screen)

        for e in self.enemies:
            e.draw(self.screen)

        for pu in self.powerups:
            pu.draw(self.screen)

        for b in self.player_bullets:
            b.draw(self.screen)
        for b in self.enemy_bullets:
            b.draw(self.screen)

        # Player on top of bullets so it's never hidden by its own shots.
        now_ms = pygame.time.get_ticks()
        self.player.draw(self.screen, now_ms)

        for p in self.particles:
            p.draw(self.screen)

        self._draw_hud()
        if self.boss is not None:
            self._draw_barra_jefe()

        # Overlay messages
        if self.state == Game.STATE_PAUSED:
            self._draw_center_message("PAUSED", "Press P to resume")
        elif self.state == Game.STATE_GAME_OVER:
            self._draw_center_message(
                "GAME OVER",
                f"Final score: {self.score}    Press R to restart",
            )

    def _draw_background(self):
        # A very simple top-to-bottom gradient using horizontal lines.
        # For a flat color, replace this whole method with screen.fill(...).
        for y in range(SCREEN_HEIGHT):
            t = y / max(1, SCREEN_HEIGHT - 1)  # 0.0 .. 1.0
            r = int(COLOR_BG_TOP[0] + (COLOR_BG_BOTTOM[0] - COLOR_BG_TOP[0]) * t)
            g = int(COLOR_BG_TOP[1] + (COLOR_BG_BOTTOM[1] - COLOR_BG_TOP[1]) * t)
            b = int(COLOR_BG_TOP[2] + (COLOR_BG_BOTTOM[2] - COLOR_BG_TOP[2]) * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def _draw_hud(self):
        # Score (top-left)
        score_surf = self.font_small.render(
            f"SCORE  {self.score:07d}", True, COLOR_HUD_TEXT
        )
        self.screen.blit(score_surf, (HUD_MARGIN, HUD_MARGIN))

        # Lives (top-right) — one tiny ship icon per life.
        lives_label = self.font_small.render("LIVES", True, COLOR_HUD_DIM)
        self.screen.blit(
            lives_label,
            (SCREEN_WIDTH - HUD_MARGIN - lives_label.get_width() - 8 - 18 * self.player.lives,
             HUD_MARGIN),
        )
        for i in range(self.player.lives):
            icon_x = SCREEN_WIDTH - HUD_MARGIN - (i + 1) * 18
            icon_y = HUD_MARGIN + 4
            # Mini triangle in the player's color.
            points = [
                (icon_x + 7,  icon_y),
                (icon_x,      icon_y + 14),
                (icon_x + 14, icon_y + 14),
            ]
            pygame.draw.polygon(self.screen, COLOR_PLAYER, points)

        # Hint line (bottom-left) — only while playing, fades after a bit.
        elapsed_ms = pygame.time.get_ticks() - self.start_ms
        if self.state == Game.STATE_PLAYING and elapsed_ms < 4000:
            hint = self.font_small.render(
                "Move: arrows/WASD   Shoot: Space/Z   Pause: P",
                True, COLOR_HUD_DIM,
            )
            self.screen.blit(
                hint,
                (HUD_MARGIN, SCREEN_HEIGHT - HUD_MARGIN - hint.get_height()),
            )

        # Escudo del colegio, abajo a la derecha (si la imagen existe).
        if self.escudo_img is not None:
            self.screen.blit(
                self.escudo_img,
                (SCREEN_WIDTH - HUD_MARGIN - ESCUDO_TAMANO,
                 SCREEN_HEIGHT - HUD_MARGIN - ESCUDO_TAMANO),
            )

    def _draw_barra_jefe(self):
        """Barra de vida grande en la parte superior de la pantalla que muestra cuanta vida le queda al jefe."""
        barra_x = (SCREEN_WIDTH - BOSS_BARRA_ANCHO) // 2
        barra_y = HUD_MARGIN + 28

        etiqueta = self.font_small.render("JEFE", True, COLOR_HUD_TEXT)
        self.screen.blit(
            etiqueta, (SCREEN_WIDTH // 2 - etiqueta.get_width() // 2, barra_y - 20)
        )

        pygame.draw.rect(
            self.screen, COLOR_BOSS_BARRA_FONDO,
            (barra_x, barra_y, BOSS_BARRA_ANCHO, BOSS_BARRA_ALTO), border_radius=4,
        )
        proporcion_vida = max(0.0, self.boss.hp / self.boss.max_hp)
        ancho_lleno = int(BOSS_BARRA_ANCHO * proporcion_vida)
        if ancho_lleno > 0:
            pygame.draw.rect(
                self.screen, COLOR_BOSS_BARRA_VIDA,
                (barra_x, barra_y, ancho_lleno, BOSS_BARRA_ALTO), border_radius=4,
            )
        pygame.draw.rect(
            self.screen, COLOR_HUD_TEXT,
            (barra_x, barra_y, BOSS_BARRA_ANCHO, BOSS_BARRA_ALTO), width=2, border_radius=4,
        )

    def _draw_center_message(self, big_text, small_text):
        # Translucent dark veil makes overlay text readable.
        veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 140))  # The 4th value is alpha (0..255).
        self.screen.blit(veil, (0, 0))

        big_surf = self.font_big.render(big_text, True, COLOR_HUD_TEXT)
        small_surf = self.font_small.render(small_text, True, COLOR_HUD_TEXT)

        self.screen.blit(
            big_surf,
            (SCREEN_WIDTH // 2 - big_surf.get_width() // 2,
             SCREEN_HEIGHT // 2 - big_surf.get_height()),
        )
        self.screen.blit(
            small_surf,
            (SCREEN_WIDTH // 2 - small_surf.get_width() // 2,
             SCREEN_HEIGHT // 2 + 8),
        )


# ---------------------------------------------------------------------
# main(): set up Pygame, then run the loop until the user quits.
# ---------------------------------------------------------------------
def main():
    # pygame.init initializes ALL pygame submodules (display, font, ...).
    # If you're worried about startup time, you can init them individually.
    pygame.init()

    # Create the window. The flags argument (3rd positional) can include
    # pygame.RESIZABLE or pygame.FULLSCREEN if you want to experiment.
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    # The Clock keeps the frame rate steady. tick(FPS) sleeps just long
    # enough to hold the game at FPS frames per second.
    clock = pygame.time.Clock()

    # We use the default system font (None) so we don't need a .ttf file.
    # Try changing the family name to e.g. "consolas" or "couriernew" for
    # a different look — pygame will fall back to a default if not found.
    font_small = pygame.font.SysFont(None, HUD_FONT_SIZE)
    font_big   = pygame.font.SysFont(None, HUD_FONT_SIZE * 3, bold=True)

    game = Game(screen, font_big, font_small)

    # The main loop. This pattern — events, update, draw, flip — is the
    # backbone of essentially every Pygame game.
    running = True
    while running:
        # 1) Process discrete events (key presses, window close, ...).
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                game.handle_event(event)

        # 2) Update the game state.
        game.update()

        # 3) Draw the new frame.
        game.draw()

        # 4) Show what we drew.
        pygame.display.flip()

        # 5) Wait so we hit (at most) FPS frames per second.
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


# Standard "only run when executed directly, not when imported" idiom.
if __name__ == "__main__":
    main()