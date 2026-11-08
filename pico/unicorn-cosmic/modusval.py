# Modusval for Cosmic Unicorn
#
#   A: The Matrix        (lyd: blippetiblopp)
#   B: Regnboge          (lyd: Korobeiniki / "Tetris-melodien")
#   C: Veret i Bergen    (lyd: regn, vind, torden, fuglar ...)
#   D: Peis              (lyd: knitring)
#
#   Eitt klikk på A-D:   byt modus
#   Dobbeltklikk A-D:    slå lyd av/på
#   Lysstyrke +/-:       lysstyrke
#   Volum +/-:           volum
#   Zzz:                 skru skjermen (og lyden) av/på
#
# Treng: lyd.py, veret.py, rainbow.py og secrets.py (WIFI_SSID / WIFI_PASSWORD) på Picoen.
# Gi fila namnet main.py på Picoen om ho skal starte av seg sjølv.

import time
import math
import random
import gc
import machine
from machine import Timer
from cosmic import CosmicUnicorn, Channel
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY
from ulab import numpy

import rainbow
import veret
from lyd import Ko, frekvens

machine.freq(200_000_000)

cu = CosmicUnicorn()
g = PicoGraphics(DISPLAY)
W = CosmicUnicorn.WIDTH
H = CosmicUnicorn.HEIGHT

ticks_ms = time.ticks_ms
_diff = time.ticks_diff
_add = time.ticks_add


# ====================================================================== A: Matrix
class Matrise:
    """Same effekt som the_matrix.py, men med lyd og utan eiga hovudløkke."""

    # pentatonisk skala (C-dur) for blippane
    SKALA = [frekvens(n) for n in (72, 74, 76, 79, 81, 84, 86, 88, 91, 93, 96)]

    def __init__(self, g):
        self.g = g
        self.felt = numpy.zeros((H, W))
        # same palett som the_matrix.py: grøn hale + lysegrøne gnistar
        self.pennar = [g.create_pen(0, i, 0) for i in range(128)] + \
                      [g.create_pen(128, 128 + i, 128) for i in range(128)]
        self.ko = Ko()
        self.neste = 0

    def start(self):
        self.felt[:] = 0

    def draw(self, no):
        felt = self.felt
        felt[:] *= 0.65
        for _ in range(2):
            x = random.randint(0, W - 1)
            y = random.randint(0, H // 2)
            felt[y][x] = random.randint(128, 255) / 255.0
        gammal = numpy.array(felt) * 0.5
        felt[:] = numpy.roll(felt, 1, axis=0)
        felt[:] += gammal
        self._teikn(numpy.array(numpy.clip(felt, 0, 1) * 254, dtype=numpy.uint8).tobytes())

    @micropython.native  # noqa: F821
    def _teikn(self, verdiar):
        g = self.g
        pennar = self.pennar
        i = 0
        for y in range(H):
            for x in range(W):
                g.set_pen(pennar[verdiar[i]])
                g.pixel(x, y)
                i += 1

    def lyd_start(self, k):
        self.ko.tom()
        k[0].configure(waveforms=Channel.SQUARE, attack=2, decay=70, sustain=0, release=20, volume=0.18)
        k[1].configure(waveforms=Channel.TRIANGLE, attack=5, decay=200, sustain=0, release=60, volume=0.4)
        self.neste = _add(ticks_ms(), 300)

    def lyd(self, k, no):
        self.ko.kjor(no)
        if _diff(no, self.neste) < 0:
            return
        # ein liten datamaskin-"setning": blipp-blipp-blipp ... blopp
        n = random.randint(3, 7)
        steg = random.choice((60, 80, 100))
        botn = random.randint(0, 4)
        for i in range(n):
            f = self.SKALA[min(botn + random.randint(0, 6), len(self.SKALA) - 1)]
            self.ko.om(no, i * steg, self._blipp, k[0], f)
        f = random.choice((131, 165, 196))
        t = n * steg
        self.ko.om(no, t, self._blipp, k[1], f)
        self.ko.om(no, t + 30, k[1].frequency, int(f * 0.85))
        self.ko.om(no, t + 60, k[1].frequency, int(f * 0.7))
        self.neste = _add(no, t + random.randint(400, 2200))

    @staticmethod
    def _blipp(c, f):
        c.frequency(f)
        c.trigger_attack()


# ====================================================================== B: Regnboge
# Korobeiniki (russisk folkesong frå 1800-talet, fri å bruke) i åttedelar.
# (MIDI-note, lengd i åttedelar), 0 = pause
MELODI = [
    (76, 2), (71, 1), (72, 1), (74, 2), (72, 1), (71, 1),
    (69, 2), (69, 1), (72, 1), (76, 2), (74, 1), (72, 1),
    (71, 3), (72, 1), (74, 2), (76, 2),
    (72, 2), (69, 2), (69, 2), (0, 2),
    (0, 1), (74, 2), (77, 1), (81, 2), (79, 1), (77, 1),
    (76, 3), (72, 1), (76, 2), (74, 1), (72, 1),
    (71, 2), (71, 1), (72, 1), (74, 2), (76, 2),
    (72, 2), (69, 2), (69, 2), (0, 2),
]
# grunntone per to åttedelar (spelast som "oktav-pumping": låg, høg)
BASS = [40] * 4 + [45] * 4 + [44] * 2 + [40] * 2 + [45] * 4 + \
       [38] * 4 + [36] * 4 + [35] * 2 + [40] * 2 + [45] * 4


class Regnboge:
    def __init__(self, g):
        rainbow.graphics = g
        rainbow.init()
        self.ko = Ko()

    def start(self):
        pass

    def draw(self, no):
        rainbow.draw()

    def lyd_start(self, k):
        self.ko.tom()
        k[0].configure(waveforms=Channel.SQUARE, attack=5, decay=100, sustain=0.5, release=40, volume=0.28)
        k[1].configure(waveforms=Channel.TRIANGLE, attack=5, decay=80, sustain=0.5, release=30, volume=0.5)
        k[2].configure(waveforms=Channel.NOISE, frequency=9000, attack=1, decay=15, sustain=0, release=5, volume=0.06)
        no = _add(ticks_ms(), 100)
        self.mi = 0
        self.bi = 0
        self.m_neste = no
        self.b_neste = no
        self.runde = 0
        self.attandel = 200   # ms per åttedel (150 BPM)

    def lyd(self, k, no):
        self.ko.kjor(no)
        # melodi
        while _diff(no, self.m_neste) >= 0:
            note, lengd = MELODI[self.mi]
            dur = lengd * self.attandel
            if note:
                k[0].frequency(frekvens(note))
                k[0].trigger_attack()
                self.ko.legg_til(_add(self.m_neste, int(dur * 0.85)), k[0].trigger_release)
            self.m_neste = _add(self.m_neste, dur)
            self.mi += 1
            if self.mi >= len(MELODI):
                self.mi = 0
                # litt raskare for kvar runde - som i spelet!
                self.runde = (self.runde + 1) % 4
                self.attandel = 200 - self.runde * 20
        # bass + hihat
        while _diff(no, self.b_neste) >= 0:
            note = BASS[(self.bi // 2) % len(BASS)] + 12 + (12 if self.bi % 2 else 0)
            k[1].frequency(frekvens(note))
            k[1].trigger_attack()
            self.ko.legg_til(_add(self.b_neste, int(self.attandel * 0.7)), k[1].trigger_release)
            if self.bi % 2:
                k[2].trigger_attack()
            self.b_neste = _add(self.b_neste, self.attandel)
            self.bi = (self.bi + 1) % (len(BASS) * 2)
            if self.bi == 0:
                # hald bass og melodi i takt
                self.b_neste = self.m_neste


# ====================================================================== D: Peis
class Peis:
    OX, OY, OW, OH = 4, 6, 24, 23   # opninga: x 4-27, y 6-28

    def __init__(self, g):
        self.g = g
        self.bw = self.OW + 2
        self.bh = self.OH + 3
        self.varme = [[0.0] * self.bh for _ in range(self.bw)]
        stopp = ((0.0, (0, 0, 0)), (0.1, (30, 0, 0)), (0.22, (120, 8, 0)), (0.35, (220, 45, 0)),
                 (0.5, (255, 115, 10)), (0.68, (255, 185, 60)), (0.85, (255, 235, 170)), (1.0, (255, 255, 240)))
        self.pal = [g.create_pen(*self._blend(stopp, i / 63)) for i in range(64)]
        self.bakgrunn = self._lag_bakgrunn()
        self.gnistar = []
        self.gnist_bestilling = 0
        self.glod = 1.0
        self.ko = Ko()
        p = g.create_pen
        self.VED = p(75, 38, 14)
        self.VED_MORK = p(45, 22, 8)
        self.VED_ENDE = p(140, 95, 55)
        self.GLO = [p(120, 10, 0), p(200, 40, 0), p(255, 100, 0)]

    @staticmethod
    def _blend(stopp, v):
        for i in range(len(stopp) - 1):
            a, ca = stopp[i]
            b, cb = stopp[i + 1]
            if v <= b:
                t = (v - a) / (b - a)
                return tuple(int(ca[j] + (cb[j] - ca[j]) * t) for j in range(3))
        return stopp[-1][1]

    def _lag_bakgrunn(self):
        """Murstein, peishylle og golv rundt opninga. (x, y, r, g, b, nærleik)"""
        ox, oy, ow, oh = self.OX, self.OY, self.OW, self.OH
        ut = []
        for y in range(H):
            for x in range(W):
                if ox <= x < ox + ow and oy <= y < oy + oh:
                    continue
                if y <= 2:      # peishylle i tre
                    c = ((110, 58, 22), (80, 40, 14), (40, 20, 8))[y]
                elif y >= 29:   # steingolv
                    c = (60, 55, 50) if y == 29 else (38, 34, 30)
                    if y > 29 and (x + y * 3) % 8 == 0:
                        c = (22, 20, 18)
                else:           # murstein
                    yy = y - 3
                    rad = yy // 3
                    forskyv = 2 if rad % 2 else 0
                    if yy % 3 == 2 or (x + forskyv) % 5 == 4:
                        c = (30, 18, 14)   # fuge
                    else:
                        v = (rad * 7 + ((x + forskyv) // 5) * 13) % 5
                        c = (100 - v * 7, 34 - v * 2, 20 - v * 2)
                dx = max(ox - x, 0, x - (ox + ow - 1))
                dy = max(oy - y, 0, y - (oy + oh - 1))
                naer = max(0.0, 1.0 - max(dx, dy) / 6.0)
                ut.append((x, y, c[0], c[1], c[2], naer))
        return ut

    def start(self):
        pass

    @micropython.native  # noqa: F821
    def _oppdater_eld(self):
        v = self.varme
        bw, bh = self.bw, self.bh
        for x in range(bw):
            v[x][bh - 1] = 0.0
            v[x][bh - 2] = 0.0
        for _ in range(6):
            # flest flammar på midten
            x = (random.randint(2, bw - 3) + random.randint(2, bw - 3)) // 2
            for dx in (-1, 0, 1):
                v[x + dx][bh - 1] = 1.0
                v[x + dx][bh - 2] = 1.0
        for y in range(bh - 2):
            for x in range(1, bw - 1):
                snitt = (v[x][y] + v[x][y + 1] + v[x][y + 2] + v[x - 1][y + 1] + v[x + 1][y + 1]) / 5.0
                v[x][y] = snitt * 0.955

    @micropython.native  # noqa: F821
    def _teikn_eld(self):
        g = self.g
        v = self.varme
        pal = self.pal
        ox, oy = self.OX, self.OY
        for y in range(self.OH):
            for x in range(self.OW):
                i = int(v[x + 1][y] * 63)
                g.set_pen(pal[63 if i > 63 else i])
                g.pixel(ox + x, oy + y)

    @micropython.native  # noqa: F821
    def _teikn_bakgrunn(self):
        g = self.g
        glod = self.glod
        for (x, y, r, gr, b, naer) in self.bakgrunn:
            f = (0.7 - 0.25 * naer) + 0.55 * naer * glod
            g.set_pen(g.create_pen(int(r * f), int(gr * f), int(b * f)))
            g.pixel(x, y)

    def draw(self, no):
        g = self.g
        self.glod += (random.uniform(0.6, 1.1) - self.glod) * 0.2
        self._oppdater_eld()
        self._teikn_bakgrunn()
        self._teikn_eld()

        # vedkubbar
        g.set_pen(self.VED)
        g.rectangle(5, 27, 22, 2)
        g.set_pen(self.VED_MORK)
        g.rectangle(9, 25, 14, 2)
        g.set_pen(self.VED_ENDE)
        g.pixel(5, 27)
        g.pixel(5, 28)
        g.pixel(26, 27)
        g.pixel(26, 28)
        g.pixel(22, 25)
        g.pixel(22, 26)
        # glør som blinkar på veden
        for x in range(6, 26):
            if random.random() < 0.25:
                g.set_pen(self.GLO[random.randint(0, 2)])
                g.pixel(x, 27 if x < 9 or x > 22 else 25)

        # gnistar (nokre kjem når det smell i lyden)
        if random.random() < 0.04:
            self.gnist_bestilling += 1
        while self.gnist_bestilling > 0 and len(self.gnistar) < 12:
            self.gnist_bestilling -= 1
            self.gnistar.append([random.uniform(self.OX + 6, self.OX + self.OW - 6), 24.0,
                                 random.uniform(-0.25, 0.25), random.uniform(-0.9, -0.4),
                                 random.randint(15, 35)])
        self.gnist_bestilling = 0
        att = []
        for s in self.gnistar:
            s[0] += s[2]
            s[1] += s[3]
            s[3] *= 0.97
            s[4] -= 1
            if s[4] > 0 and s[1] >= self.OY:
                g.set_pen(self.pal[min(63, 25 + s[4])])
                g.pixel(int(s[0]), int(s[1]))
                att.append(s)
        self.gnistar = att

    # ---------- lyd: knitring
    def lyd_start(self, k):
        self.ko.tom()
        k[0].configure(waveforms=Channel.NOISE, attack=1, decay=10, sustain=0, release=5, volume=0.3)
        k[1].configure(waveforms=Channel.NOISE, frequency=120, attack=500, decay=10, sustain=1.0, release=500, volume=0.03)
        k[2].configure(waveforms=Channel.NOISE, attack=1, decay=40, sustain=0, release=10, volume=0.4)
        k[1].trigger_attack()

    def lyd(self, k, no):
        self.ko.kjor(no)
        r = random.random()
        if r < 0.06:                      # knitter (ca. 6 i sekundet)
            self._knitter(k[0])
            if random.random() < 0.3:     # ofte i små klyngjer
                for _ in range(random.randint(1, 3)):
                    self.ko.om(no, random.randint(20, 90), self._knitter, k[0])
        elif r < 0.066:                   # av og til eit større smell + gnistar
            k[2].frequency(random.randint(500, 1200))
            k[2].trigger_attack()
            self.gnist_bestilling += random.randint(1, 3)
        # sus frå flammane
        if random.random() < 0.1:
            k[1].volume(random.uniform(0.02, 0.045))
            k[1].frequency(random.randint(80, 160))

    @staticmethod
    def _knitter(c):
        c.configure(frequency=random.randint(2500, 9000), volume=random.uniform(0.1, 0.35),
                    decay=random.randint(4, 18))
        c.trigger_attack()


# ====================================================================== hovudprogram
modusar = [Matrise(g), Regnboge(g), veret.Veret(g), Peis(g)]
kanalar = [cu.synth_channel(i) for i in range(5)]

KNAPPAR = (CosmicUnicorn.SWITCH_A, CosmicUnicorn.SWITCH_B,
           CosmicUnicorn.SWITCH_C, CosmicUnicorn.SWITCH_D)
DOBBELKLIKK_MS = 400

aktiv = 0
lyd_paa = False
lyd_klar = False
sover = False
varsel_til = 0

var_nede = [False] * 4
sist_knapp = -1
sist_klikk = 0
sov_var_nede = False


def kanalar_av():
    for c in kanalar:
        c.trigger_release()
        c.volume(0)


def lyd_start():
    global lyd_klar
    lyd_klar = False
    kanalar_av()
    modusar[aktiv].lyd_start(kanalar)
    cu.play_synth()
    lyd_klar = True


def lyd_stopp():
    global lyd_klar
    lyd_klar = False
    kanalar_av()
    cu.stop_playing()


def byt_modus(i):
    global aktiv, lyd_klar
    lyd_klar = False
    if lyd_paa:
        kanalar_av()
    aktiv = i
    gc.collect()
    modusar[i].start()
    if lyd_paa and not sover:
        modusar[i].lyd_start(kanalar)
        lyd_klar = True


def klikk(i, no):
    global sist_knapp, sist_klikk, lyd_paa, varsel_til
    if i == sist_knapp and _diff(no, sist_klikk) < DOBBELKLIKK_MS:
        lyd_paa = not lyd_paa
        if lyd_paa:
            lyd_start()
        else:
            lyd_stopp()
        varsel_til = _add(no, 1200)
        sist_knapp = -1
        return
    sist_knapp = i
    sist_klikk = no
    if i != aktiv:
        byt_modus(i)


def lyd_tikk(_t):
    # køyrer 100 gonger i sekundet, uavhengig av kor fort skjermen teiknar
    if lyd_paa and lyd_klar and not sover:
        try:
            modusar[aktiv].lyd(kanalar, ticks_ms())
        except Exception as e:
            print("Lydfeil:", e)


NOTE_IKON = ("..###", "..#.#", "..#..", "###..", "###..")


def teikn_lydvarsel():
    g.set_pen(g.create_pen(0, 0, 0))
    g.rectangle(24, 0, 8, 7)
    g.set_pen(g.create_pen(0, 255, 90) if lyd_paa else g.create_pen(255, 40, 0))
    for y, rad in enumerate(NOTE_IKON):
        for x, c in enumerate(rad):
            if c == "#":
                g.pixel(26 + x, 1 + y)
    if not lyd_paa:
        g.set_pen(g.create_pen(255, 255, 255))
        for i in range(6):
            g.pixel(25 + i, i)


def sjekk_knappar(no):
    global sover, sov_var_nede, lyd_klar
    for i, k in enumerate(KNAPPAR):
        nede = cu.is_pressed(k)
        if nede and not var_nede[i]:
            klikk(i, no)
        var_nede[i] = nede

    nede = cu.is_pressed(CosmicUnicorn.SWITCH_SLEEP)
    if nede and not sov_var_nede:
        sover = not sover
        if sover:
            if lyd_paa:
                lyd_stopp()
            g.set_pen(g.create_pen(0, 0, 0))
            g.clear()
            cu.update(g)
        elif lyd_paa:
            lyd_start()
    sov_var_nede = nede

    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):
        cu.adjust_brightness(+0.01)
    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):
        cu.adjust_brightness(-0.01)
    if cu.is_pressed(CosmicUnicorn.SWITCH_VOLUME_UP):
        cu.adjust_volume(+0.01)
    if cu.is_pressed(CosmicUnicorn.SWITCH_VOLUME_DOWN):
        cu.adjust_volume(-0.01)


cu.set_brightness(0.5)
cu.set_volume(0.5)
modusar[aktiv].start()
lydtimar = Timer(period=10, mode=Timer.PERIODIC, callback=lyd_tikk)

BILETE_MS = 30   # ca. 33 bilete i sekundet

while True:
    start = ticks_ms()
    sjekk_knappar(start)

    if not sover:
        modusar[aktiv].draw(start)
        if _diff(varsel_til, start) > 0:
            teikn_lydvarsel()
        cu.update(g)

    brukt = _diff(ticks_ms(), start)
    time.sleep_ms(max(1, BILETE_MS - brukt))
