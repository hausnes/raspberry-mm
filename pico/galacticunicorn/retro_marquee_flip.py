"""
Retro attract-mode marquee for Pimoroni Galactic Unicorn (53 x 11).
Beregnet for en Picade Max-kabinett.

Fire modus som bytter automatisk hvert 10. sekund:
  0  Rulletekst   - regnbuegradient med lopelys over og under
  1  Invaders     - marsjerende sprites og skytende kanon
  2  Krom-tittel  - "PICADE" / "MAX" med glidende metallglans
  3  Synthwave    - solnedgang med skannelinjer og rullende grid

Knapper:
  A B C D          - velg modus manuelt (slar av auto-loop)
  VOLUME UP/DOWN   - tilbake til auto-loop
  LUX UP/DOWN      - lysstyrke
  SLEEP            - skru panelet av/pa

Krever Pimoroni MicroPython-bygget for Galactic Unicorn.
Lagre som main.py pa panelet for autostart.
"""

import time
import math
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY

gu = GalacticUnicorn()

WIDTH = GalacticUnicorn.WIDTH    # 53
HEIGHT = GalacticUnicorn.HEIGHT  # 11

# Panelet er montert opp-ned i kabinettet. Sett til False hvis du snur det.
FLIP = True

# Egen framebuffer, sa vi kan rotere bildet for det sendes til panelet.
# Galactic Unicorn bruker RGB888 pakket i en uint32, altsa fire byte per piksel.
_PIXELS = WIDTH * HEIGHT
_buf = bytearray(_PIXELS * 4)
graphics = PicoGraphics(display=DISPLAY, buffer=_buf)
_mv = memoryview(_buf)


def show():
    """Send bildet til panelet, eventuelt rotert 180 grader."""
    if FLIP:
        # 180 grader = snu rekkefolgen pa alle pikslene i bufferet
        for i in range(_PIXELS // 2):
            a = i * 4
            b = (_PIXELS - 1 - i) * 4
            _mv[a], _mv[b] = _mv[b], _mv[a]
            _mv[a + 1], _mv[b + 1] = _mv[b + 1], _mv[a + 1]
            _mv[a + 2], _mv[b + 2] = _mv[b + 2], _mv[a + 2]
            _mv[a + 3], _mv[b + 3] = _mv[b + 3], _mv[a + 3]
    gu.update(graphics)

# Start lavt. Panelet star rett over hodet ditt i kabinettet.
BRIGHTNESS = 0.35
gu.set_brightness(BRIGHTNESS)

MODE_SECONDS = 10.0   # hvor lenge hver modus vises i auto-loop
FADE_SECONDS = 0.35   # inn- og uttoning mellom modus

BLACK = graphics.create_pen(0, 0, 0)
_fade = 1.0


def pen(r, g, b):
    """Lag en pen med global inn/uttoning pafort."""
    r = int(max(0, min(255, r)) * _fade)
    g = int(max(0, min(255, g)) * _fade)
    b = int(max(0, min(255, b)) * _fade)
    return graphics.create_pen(r, g, b)


def hsv_pen(h, s, v):
    """HSV til RGB i ren Python. Eldre firmware mangler create_pen_hsv."""
    h = h % 1.0
    i = int(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    u = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        r, g, b = v, u, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, u
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = u, p, v
    else:
        r, g, b = v, p, q
    return pen(r * 255, g * 255, b * 255)


def sprite(rows, x0, y0, r, g, b):
    """Tegn en sprite gitt som liste av strenger med '1' og '0'."""
    graphics.set_pen(pen(r, g, b))
    for dy, row in enumerate(rows):
        y = y0 + dy
        if y < 0 or y >= HEIGHT:
            continue
        for dx, c in enumerate(row):
            if c == "1":
                x = x0 + dx
                if 0 <= x < WIDTH:
                    graphics.pixel(x, y)


# ---------------------------------------------------------------- modus 0
MSG = "PICADE MAX * INSERT COIN * 1 PLAYER * PRESS START * "


def mode_scroll(t):
    graphics.set_font("bitmap8")
    total = graphics.measure_text(MSG, 1)
    offset = (t * 21.0) % total

    # To gjennomkjoringer sa teksten loper somlost rundt
    for lap in (0, 1):
        cx = -offset + lap * total
        for ch in MSG:
            cw = graphics.measure_text(ch, 1)
            if -8 < cx < WIDTH:
                graphics.set_pen(hsv_pen(cx * 0.012 - t * 0.35, 0.95, 1.0))
                graphics.text(ch, int(cx), 2, -1, 1)
            cx += cw
            if cx > WIDTH:
                break

    # Lopelys pa oyerste og nederste rad
    step = int(t * 16)
    for x in range(WIDTH):
        v = 1.0 if ((x + step) % 6) == 0 else 0.08
        graphics.set_pen(pen(255 * v, 140 * v, 20 * v))
        graphics.pixel(x, 0)
        graphics.pixel(x, 10)


# ---------------------------------------------------------------- modus 1
INVADER_A = ["00100100",
             "01111110",
             "11011011",
             "11111111",
             "01000010"]

INVADER_B = ["10100101",
             "01111110",
             "11011011",
             "11111111",
             "00111100"]

CANNON = ["0001000",
          "0111110",
          "1111111"]

SHOT_PERIOD = 1.05


def _cannon_x(t):
    return int(23 + 19 * math.sin(t * 0.85))


def mode_invaders(t):
    step = int(t * 4)
    phase = step % 16
    xo = phase if phase < 8 else 16 - phase          # marsj fram og tilbake
    frame = INVADER_B if step % 2 else INVADER_A     # to animasjonsbilder

    for i in range(4):
        graphics.set_pen(hsv_pen(0.42 + i * 0.12, 0.85, 1.0))
        for dy, row in enumerate(frame):
            for dx, c in enumerate(row):
                if c == "1":
                    x = 2 + i * 11 + xo + dx
                    if 0 <= x < WIDTH:
                        graphics.pixel(x, 1 + dy)

    sprite(CANNON, _cannon_x(t), 8, 70, 255, 120)

    # Skudd: deterministisk, sa vi slipper a holde styr pa tilstand
    n = int(t / SHOT_PERIOD)
    for k in range(max(0, n - 2), n + 1):
        dt = t - k * SHOT_PERIOD
        if dt < 0:
            continue
        y = 8 - dt * 13
        if y < -1:
            continue
        x = _cannon_x(k * SHOT_PERIOD) + 3
        if 0 <= x < WIDTH:
            if y >= 0:
                graphics.set_pen(pen(255, 255, 200))
                graphics.pixel(x, int(y))
            if 0 <= y + 1 < HEIGHT:
                graphics.set_pen(pen(90, 90, 40))
                graphics.pixel(x, int(y) + 1)
            if -0.6 < y < 1.2:                       # liten trefftreff-blink
                graphics.set_pen(pen(220, 200, 60))
                for d in range(-2, 3):
                    if 0 <= x + d < WIDTH:
                        graphics.pixel(x + d, 1)


# ---------------------------------------------------------------- modus 2
WORDS = ("PICADE", "HAUSNES")
WORD_SECONDS = 2.6


def mode_chrome(t):
    graphics.set_font("bitmap8")
    word = WORDS[int(t / WORD_SECONDS) % 2]
    w = graphics.measure_text(word, 1)
    x0 = (WIDTH - w) // 2

    # Loddrett kromgradient: hvit topp, blatt bunn. En klipperad om gangen.
    for row in range(HEIGHT):
        f = row / 10.0
        graphics.set_clip(0, row, WIDTH, 1)
        graphics.set_pen(pen(255 - f * 170, 255 - f * 90, 255 - f * 10))
        graphics.text(word, x0, 2, -1, 1)

    # Glans som sveiper over bokstavene
    sweep = int((t * 26) % (WIDTH + 20)) - 10
    for dx in range(-1, 2):
        graphics.set_clip(sweep + dx, 0, 1, HEIGHT)
        graphics.set_pen(pen(255, 255, 255))
        graphics.text(word, x0, 2, -1, 1)
    graphics.remove_clip()

    # Pulserende ramme
    b = 0.35 + 0.65 * abs(math.sin(t * 2.1))
    graphics.set_pen(pen(255 * b, 60 * b, 200 * b))
    for x in range(WIDTH):
        graphics.pixel(x, 0)
        graphics.pixel(x, HEIGHT - 1)
    for y in range(HEIGHT):
        graphics.pixel(0, y)
        graphics.pixel(WIDTH - 1, y)


# ---------------------------------------------------------------- modus 3
SUN_X = 26
SUN_Y = 9
SUN_R = 9
HORIZON = 7


def mode_synthwave(t):
    # Stjerner
    for i in range(16):
        x = (i * 17 + 5) % WIDTH
        y = (i * 7) % 6
        tw = 0.5 + 0.5 * math.sin(t * 2.2 + i)
        graphics.set_pen(pen(45 * tw, 35 * tw, 80 * tw))
        graphics.pixel(x, y)

    # Sol. Fargen avhenger bare av rad, sa hver rad tegnes som en linje.
    scan = int(t * 5)
    for y in range(HORIZON):
        dy = y - SUN_Y
        span2 = SUN_R * SUN_R - dy * dy
        if span2 <= 0:
            continue
        half = int(math.sqrt(span2))
        f = y / 7.0
        band = 0.12 if ((y * 2 + scan) % 5) < 1 else 1.0
        graphics.set_pen(pen(255 * band, (40 + 180 * f) * band, (150 - 95 * f) * band))
        graphics.line(max(0, SUN_X - half), y, min(WIDTH - 1, SUN_X + half), y)

    # Horisont
    graphics.set_pen(pen(255, 60, 170))
    graphics.line(0, HORIZON, WIDTH - 1, HORIZON)

    # Perspektivgrid under horisonten
    graphics.set_pen(pen(0, 70, 110))
    for k in range(-9, 10):
        for row in range(8, HEIGHT):
            x = int(SUN_X + k * (1.1 + (row - 7) * 2.3))
            if 0 <= x < WIDTH:
                graphics.pixel(x, row)

    # Tverrlinje som ruller mot betrakteren
    hr = 8 + (int(t * 4) % 3)
    graphics.set_pen(pen(0, 150 - (hr - 8) * 30, 210))
    graphics.line(0, hr, WIDTH - 1, hr)


MODES = (mode_scroll, mode_invaders, mode_chrome, mode_synthwave)
SWITCHES = (GalacticUnicorn.SWITCH_A,
            GalacticUnicorn.SWITCH_B,
            GalacticUnicorn.SWITCH_C,
            GalacticUnicorn.SWITCH_D)


# ---------------------------------------------------------------- hovedlokke
mode = 0
auto = True
asleep = False
started = time.ticks_ms()
last_button = time.ticks_ms()

while True:
    now = time.ticks_ms()

    # --- knapper (med enkel sperre mot dobbelttrykk)
    if time.ticks_diff(now, last_button) > 200:
        for i, sw in enumerate(SWITCHES):
            if gu.is_pressed(sw):
                mode = i
                auto = False
                started = now
                last_button = now

        if gu.is_pressed(GalacticUnicorn.SWITCH_VOLUME_UP) or \
           gu.is_pressed(GalacticUnicorn.SWITCH_VOLUME_DOWN):
            auto = True
            started = now
            last_button = now

        if gu.is_pressed(GalacticUnicorn.SWITCH_SLEEP):
            asleep = not asleep
            last_button = now

    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
        BRIGHTNESS = min(1.0, BRIGHTNESS + 0.01)
        gu.set_brightness(BRIGHTNESS)
    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
        BRIGHTNESS = max(0.05, BRIGHTNESS - 0.01)
        gu.set_brightness(BRIGHTNESS)

    if asleep:
        graphics.set_pen(BLACK)
        graphics.clear()
        gu.update(graphics)
        time.sleep_ms(80)
        continue

    # --- modusbytte
    t = time.ticks_diff(now, started) / 1000.0
    if auto and t > MODE_SECONDS:
        mode = (mode + 1) % len(MODES)
        started = now
        t = 0.0

    # --- inn- og uttoning
    _fade = min(1.0, t / FADE_SECONDS)
    if auto:
        _fade = min(_fade, max(0.0, (MODE_SECONDS - t) / FADE_SECONDS))

    graphics.set_pen(BLACK)
    graphics.clear()
    MODES[mode](t)
    show()

    time.sleep_ms(16)   # ca. 60 bilder i sekundet