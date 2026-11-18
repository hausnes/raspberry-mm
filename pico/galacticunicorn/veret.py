# Veret i Bergen frå YR (api.met.no) på Galactic Unicorn (53 x 11 pikslar).
# Animasjon til venstre, temperatur (og vind når det blæs) til høgre.
# Fell tilbake på Open-Meteo om YR ikkje svarar.
#
#   Lysstyrke +/-:  lysstyrke
#   Zzz:            skru skjermen av/på
#
# Treng secrets.py på Picoen med WIFI_SSID og WIFI_PASSWORD
# (og gjerne KONTAKT = "di@epost.no", sjå under).
# Gi fila namnet main.py på Picoen om ho skal starte av seg sjølv.
import time
import math
import random
import gc
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY

_diff = time.ticks_diff
_add = time.ticks_add

# Bergen sentrum (met.no vil ha maks 4 desimalar)
LAT = 60.3913
LON = 5.3221

YR_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={}&lon={}".format(LAT, LON)

# met.no krev at User-Agent seier kven du er, med kontaktinfo (e-post eller nettside).
# Legg KONTAKT i secrets.py, elles kan du bli blokkert (svar 403).
try:
    from secrets import KONTAKT
except ImportError:
    KONTAKT = "byt-ut-med-di-epost@example.com"
USER_AGENT = "GalacticUnicornVeret/1.0 " + KONTAKT

OPEN_METEO_URL = ("http://api.open-meteo.com/v1/forecast?latitude={}&longitude={}"
                  "&current=temperature_2m,precipitation,weather_code,wind_speed_10m,is_day"
                  "&wind_speed_unit=ms").format(LAT, LON)

OPPDATER_MS = 20 * 60 * 1000   # hent nytt ver kvart 20. minutt
VINDGRENSE = 6.0               # m/s - frå denne farten viser vi vind

W = GalacticUnicorn.WIDTH      # 53
H = GalacticUnicorn.HEIGHT     # 11
ANIM_W = 23                    # kolonne 0-22: animasjon, 23-52: tekst
ANIM_H = H


# ---------------------------------------------------------------- henting

def _tal(seg, nokkel, start=0):
    i = seg.find(b'"' + nokkel + b'"', start)
    if i < 0:
        return None
    i = seg.find(b":", i) + 1
    while seg[i:i + 1] == b" ":
        i += 1
    j = i
    while j < len(seg) and seg[j:j + 1] in b"-+0123456789.eE":
        j += 1
    return float(str(seg[i:j], "utf-8"))


def _tekst(seg, nokkel, start=0):
    i = seg.find(b'"' + nokkel + b'"', start)
    if i < 0:
        return None
    i = seg.find(b'"', seg.find(b":", i)) + 1
    j = seg.find(b'"', i)
    return str(seg[i:j], "utf-8")


def fra_symbol(sym):
    """YR symbol_code -> (type, styrke 1-3, natt)"""
    natt = sym.endswith("_night")
    s = sym.split("_")[0]
    styrke = 1 if s.startswith("light") else 3 if s.startswith("heavy") else 2
    if "thunder" in s:
        return "torden", styrke, natt
    if "sleet" in s:
        return "sludd", styrke, natt
    if "snow" in s:
        return "snoe", styrke, natt
    if "rain" in s:
        return "regn", styrke, natt
    if s == "fog":
        return "taake", 1, natt
    if s == "cloudy":
        return "sky", 1, natt
    if s == "partlycloudy":
        return "delvis", 1, natt
    return "sol", 1, natt   # clearsky, fair


def fra_wmo(kode):
    """Open-Meteo weather_code -> (type, styrke)"""
    if kode in (0, 1):
        return "sol", 1
    if kode == 2:
        return "delvis", 1
    if kode == 3:
        return "sky", 1
    if kode in (45, 48):
        return "taake", 1
    if kode in (51, 53, 55, 56, 57, 61, 80):
        return "regn", 1
    if kode in (63, 81):
        return "regn", 2
    if kode in (65, 82):
        return "regn", 3
    if kode in (66, 67):
        return "sludd", 2
    if kode in (71, 73, 75, 77, 85, 86):
        return "snoe", 2
    if kode >= 95:
        return "torden", 2
    return "sky", 1


def hent_yr():
    import urequests
    r = urequests.get(YR_URL, headers={"User-Agent": USER_AGENT})
    try:
        if r.status_code != 200:
            raise OSError("YR svarte {}".format(r.status_code))
        # Heile varselet er for stort for minnet til Picoen.
        # Vi les berre til vi har fått med det første tidspunktet.
        buf = b""
        while len(buf) < 20000:
            bit = r.raw.read(512)
            if not bit:
                break
            buf += bit
            a = buf.find(b'"time"')
            if a >= 0 and buf.find(b'"time"', a + 6) >= 0:
                break
    finally:
        r.close()

    a = buf.find(b'"time"')
    if a < 0:
        raise ValueError("fann ikkje verdata")
    b = buf.find(b'"time"', a + 6)
    seg = buf[a:b] if b > 0 else buf[a:]

    temp = _tal(seg, b"air_temperature")
    vind = _tal(seg, b"wind_speed") or 0.0
    n1 = max(seg.find(b'"next_1_hours"'), 0)
    sym = _tekst(seg, b"symbol_code", n1) or "cloudy"
    type_, styrke, natt = fra_symbol(sym)
    print("YR:", temp, "grader,", vind, "m/s,", sym)
    return {"temp": temp, "vind": vind, "type": type_, "styrke": styrke, "natt": natt}


def hent_open_meteo():
    import urequests
    r = urequests.get(OPEN_METEO_URL)
    try:
        j = r.json()["current"]
    finally:
        r.close()
    type_, styrke = fra_wmo(j["weather_code"])
    print("Open-Meteo:", j)
    return {"temp": j["temperature_2m"], "vind": j["wind_speed_10m"],
            "type": type_, "styrke": styrke, "natt": not j["is_day"]}


# ---------------------------------------------------------------- visning

class Veret:
    def __init__(self, g):
        self.g = g
        self.data = None
        self.sist_henta = None
        self.feil_tid = None
        self.tilstand = "wifi"
        self.wlan = None
        self.f = 0
        self.partiklar = []
        self.straumar = []
        self.lyn = 0
        self.lyn_punkt = []

        p = g.create_pen
        self.SVART = p(0, 0, 0)
        self.KVIT = p(255, 255, 255)
        self.GRAA = p(150, 150, 150)
        self.SOL = p(255, 180, 0)
        self.SOL_LYS = p(255, 230, 90)
        self.STRAALE = p(255, 130, 0)
        self.MANE = p(230, 225, 170)
        self.NATT = p(0, 0, 5)
        self.SKY_LYS = p(200, 200, 210)
        self.SKY_SKUGGE = p(120, 120, 135)
        self.SKY_MORK = p(80, 80, 95)
        self.SKY_MORK_SKUGGE = p(45, 45, 55)
        self.DROPE = p(80, 150, 255)
        self.DROPE_HALE = p(25, 55, 140)
        self.LYN = p(255, 255, 120)
        self.VARM = p(255, 140, 40)
        self.KALD = p(100, 170, 255)
        self.VIND = [p(30, 30, 35), p(70, 70, 80), p(140, 140, 155)]
        self.TAAKE = [p(v, v, v + 4) for v in range(8, 72, 8)]
        self.STJERNE = [p(40, 40, 50), p(200, 200, 230)]
        self.STJERNER = [(2, 2), (19, 1), (17, 9), (3, 8), (8, 1), (21, 6), (1, 5)]

        self._start_wifi()

    # ---------- wifi og henting
    def _for_gammal(self, no):
        return self.sist_henta is None or _diff(no, self.sist_henta) > OPPDATER_MS

    def _start_wifi(self):
        import network
        if self.wlan is None:
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
        if not self.wlan.isconnected():
            try:
                from secrets import WIFI_SSID, WIFI_PASSWORD
                self.wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            except ImportError:
                print("Lag secrets.py med WIFI_SSID og WIFI_PASSWORD")
        self.wifi_start = time.ticks_ms()
        self.tilstand = "wifi"

    def _hent(self, no):
        gc.collect()
        ny = None
        for kjelde in (hent_yr, hent_open_meteo):
            try:
                ny = kjelde()
                break
            except Exception as e:
                print("Klarte ikkje hente ver:", e)
        if ny is not None and ny["temp"] is not None:
            self.data = ny
            self.sist_henta = no
            self._lag_partiklar()
        elif self.data is not None:
            # prøv igjen om eitt minutt, behald gamle data
            self.sist_henta = _add(no, -OPPDATER_MS + 60000)
        else:
            self.feil_tid = no
        gc.collect()

    # ---------- teikning
    def draw(self, no):
        self.f += 1
        if self.tilstand == "wifi":
            if self.wlan.isconnected():
                self.tilstand = "hent"
                if self.data is None:
                    self._melding("HENTAR")
                    return
            elif _diff(no, self.wifi_start) > 20000:
                self._start_wifi()   # prøv på nytt
            if self.data is None:
                self._melding("WIFI")
                return

        if self.tilstand == "hent":
            if not self.wlan.isconnected():
                self._start_wifi()
                if self.data is None:
                    self._melding("WIFI")
                    return
            else:
                self._hent(no)
                self.tilstand = "vis"

        if self.data is None:
            self._melding("FEIL")
            if self.feil_tid is None or _diff(no, self.feil_tid) > 60000:
                self.feil_tid = no
                self.tilstand = "hent"
            return

        if self.tilstand == "vis" and self._for_gammal(no):
            self.tilstand = "hent"   # neste bilete hentar nytt ver

        self._scene()

    def _melding(self, tekst):
        g = self.g
        g.set_pen(self.SVART)
        g.clear()
        g.set_font("bitmap8")
        w = g.measure_text(tekst, 1)
        g.set_pen(self.GRAA)
        g.text(tekst, (40 - w) // 2, 2, -1, 1)
        aktiv = (self.f // 8) % 3
        for i in range(3):
            g.set_pen(self.KVIT if i == aktiv else self.SKY_MORK)
            g.rectangle(41 + i * 4, 5, 2, 2)

    def _lag_partiklar(self):
        d = self.data
        t = d["type"]
        self.partiklar = []
        if t in ("regn", "torden", "sludd"):
            n = (4, 7, 11)[d["styrke"] - 1]
            for _ in range(n):
                self.partiklar.append([random.uniform(-5, ANIM_W), random.uniform(3, ANIM_H),
                                       random.uniform(0.35, 0.6), 0.0, 0])
        if t in ("snoe", "sludd"):
            n = (5, 8, 12)[d["styrke"] - 1]
            for _ in range(n):
                self.partiklar.append([random.uniform(-3, ANIM_W), random.uniform(2, ANIM_H),
                                       random.uniform(0.05, 0.12), random.uniform(0, 6.28), 1])
        self.straumar = []
        if d["vind"] >= VINDGRENSE:
            for _ in range(min(int(d["vind"] / 5), 3)):
                self.straumar.append([random.uniform(-20, ANIM_W), random.randint(1, ANIM_H - 2),
                                      random.randint(3, 6), random.uniform(0.5, 1.0)])

    def _scene(self):
        g = self.g
        d = self.data
        t = d["type"]
        natt = d["natt"]

        # bakgrunn bak animasjonen
        if self.lyn > 0:
            g.set_pen(g.create_pen(60 * self.lyn, 60 * self.lyn, 70 * self.lyn))
        elif natt:
            g.set_pen(self.NATT)
        elif t in ("sol", "delvis"):
            g.set_pen(g.create_pen(0, 10, 40))
        elif t in ("regn", "torden", "sludd"):
            g.set_pen(g.create_pen(3, 4, 10))
        else:
            g.set_pen(g.create_pen(7, 8, 14))
        g.clear()

        g.set_clip(0, 0, ANIM_W, ANIM_H)
        f = self.f

        if t == "sol":
            if natt:
                self._stjerner()
                self._mane(11, 5)
            else:
                self._sol(11, 5, 3)
        elif t == "delvis":
            if natt:
                self._stjerner()
                self._mane(8, 4)
            else:
                self._sol(7, 4, 3)
            x = int(7 + 3 * math.sin(f * 0.01))
            self._sky(x, 4, self.SKY_LYS, self.SKY_SKUGGE)
        elif t == "sky":
            x1 = int((f * 0.08) % 38) - 15
            x2 = int((f * 0.14 + 19) % 38) - 15
            self._sky(x1, -1, self.SKY_SKUGGE, self.SKY_MORK)
            self._sky(x2, 4, self.SKY_LYS, self.SKY_SKUGGE)
        elif t == "taake":
            self._taake()
        else:
            # nedbør: skyer øvst, partiklar under
            if t == "snoe":
                lys, skugge = self.SKY_LYS, self.SKY_SKUGGE
            else:
                lys, skugge = self.SKY_MORK, self.SKY_MORK_SKUGGE
            self._oppdater_partiklar(d["vind"])
            self._teikn_partiklar()
            self._sky(-3, -3, lys, skugge)
            self._sky(9, -4, lys, skugge)
            if t == "torden":
                self._torden()

        if self.straumar:
            self._vind()

        g.remove_clip()
        self._temperatur()

    # ---------- element
    def _sol(self, cx, cy, r):
        g = self.g
        g.set_pen(self.STRAALE)
        for i in range(8):
            a = i * 0.785 + self.f * 0.02
            ca, sa = math.cos(a), math.sin(a)
            lengd = 2 if (i + self.f // 10) % 2 else 1
            for s in range(r + 2, r + 2 + lengd):
                g.pixel(int(cx + ca * s + 0.5), int(cy + sa * s + 0.5))
        g.set_pen(self.SOL)
        g.circle(cx, cy, r)
        g.set_pen(self.SOL_LYS)
        g.circle(cx - 1, cy - 1, 1)

    def _mane(self, cx, cy):
        g = self.g
        g.set_pen(self.MANE)
        g.circle(cx, cy, 4)
        g.set_pen(self.NATT)
        g.circle(cx + 2, cy - 2, 3)

    def _stjerner(self):
        g = self.g
        for i, (x, y) in enumerate(self.STJERNER):
            g.set_pen(self.STJERNE[1 if ((self.f + i * 13) // 20) % 4 else 0])
            g.pixel(x, y)

    def _sky(self, x, y, lys, skugge):
        # liten sky, ca. 13 x 7 pikslar
        g = self.g
        g.set_pen(skugge)
        g.circle(x + 3, y + 4, 2)
        g.circle(x + 7, y + 3, 3)
        g.circle(x + 11, y + 4, 2)
        g.rectangle(x + 3, y + 4, 9, 3)
        g.set_pen(lys)
        g.circle(x + 3, y + 3, 2)
        g.circle(x + 7, y + 2, 3)
        g.circle(x + 11, y + 3, 2)
        g.rectangle(x + 3, y + 3, 9, 2)

    def _oppdater_partiklar(self, vind):
        dx = min(vind / 8.0, 1.5)
        f = self.f
        for p in self.partiklar:
            if p[4] == 0:   # regndrope
                p[1] += p[2]
                p[0] += dx * p[2] * 0.6
                if p[1] >= ANIM_H or p[0] > ANIM_W:
                    p[0] = random.uniform(-6, ANIM_W - 2)
                    p[1] = random.uniform(3, 5)
            else:           # snøflak
                p[1] += p[2]
                p[0] += math.sin(f * 0.05 + p[3]) * 0.12 + dx * 0.2
                if p[1] >= ANIM_H or p[0] > ANIM_W:
                    p[0] = random.uniform(-3, ANIM_W - 2)
                    p[1] = random.uniform(2, 4)

    def _teikn_partiklar(self):
        g = self.g
        skeiv = 1 if self.data["vind"] >= VINDGRENSE else 0
        for p in self.partiklar:
            x, y = int(p[0]), int(p[1])
            if p[4] == 0:
                g.set_pen(self.DROPE_HALE)
                g.pixel(x - skeiv, y - 1)
                g.set_pen(self.DROPE)
                g.pixel(x, y)
            else:
                g.set_pen(self.KVIT)
                g.pixel(x, y)

    def _torden(self):
        g = self.g
        if self.lyn == 0 and random.random() < 0.005:
            self.lyn = 4
            x = random.randint(5, ANIM_W - 5)
            self.lyn_punkt = [(x, 3)]
            y = 3
            while y < ANIM_H:
                y += random.randint(1, 3)
                x += random.randint(-2, 2)
                self.lyn_punkt.append((x, y))
        if self.lyn > 0:
            g.set_pen(self.LYN)
            for i in range(len(self.lyn_punkt) - 1):
                a, b = self.lyn_punkt[i], self.lyn_punkt[i + 1]
                g.line(a[0], a[1], b[0], b[1])
            self.lyn -= 1

    def _taake(self):
        g = self.g
        f = self.f
        n = len(self.TAAKE)
        for y in range(ANIM_H):
            fart = 0.03 + (y % 3) * 0.015
            for x in range(ANIM_W):
                v = math.sin(x * 0.25 + f * fart + y * 0.9) + math.sin(x * 0.11 - f * 0.02 + y * 0.3)
                g.set_pen(self.TAAKE[int((v + 2) * (n - 1) / 4)])
                g.pixel(x, y)

    def _vind(self):
        g = self.g
        for s in self.straumar:
            s[0] += s[3]
            if s[0] - s[2] > ANIM_W:
                s[0] = random.uniform(-18, -2)
                s[1] = random.randint(1, ANIM_H - 2)
            x, y, l = int(s[0]), s[1], s[2]
            for i in range(l):
                g.set_pen(self.VIND[min(2, (l - i) * 3 // l)])
                g.pixel(x - i, y)

    def _temperatur(self):
        g = self.g
        d = self.data
        g.set_pen(self.SVART)
        g.rectangle(ANIM_W, 0, W - ANIM_W, H)
        bredde = W - ANIM_W
        y = 2
        g.set_font("bitmap8")

        # vis vindfart i 3 av 10 sekund når det blæs
        if d["vind"] >= VINDGRENSE and (self.f // 30) % 10 >= 7:
            tekst = "{}m/s".format(int(d["vind"] + 0.5))
            w = g.measure_text(tekst, 1)
            if w > bredde:
                g.set_font("bitmap6")
                w = g.measure_text(tekst, 1)
            g.set_pen(self.GRAA)
            g.text(tekst, ANIM_W + (bredde - w) // 2, y, -1, 1)
            return

        temp = int(round(d["temp"]))
        tekst = str(temp)
        w = g.measure_text(tekst, 1)
        cw = g.measure_text("C", 1)
        total = w + 4 + cw
        if total > bredde:
            g.set_font("bitmap6")
            w = g.measure_text(tekst, 1)
            cw = g.measure_text("C", 1)
            total = w + 4 + cw
        x = ANIM_W + (bredde - total) // 2
        g.set_pen(self.VARM if temp > 0 else self.KALD)
        g.text(tekst, x, y, -1, 1)
        # gradsymbol (bitmap-fontane har ikkje °)
        gx = x + w
        g.pixel(gx + 1, y)
        g.pixel(gx, y + 1)
        g.pixel(gx + 2, y + 1)
        g.pixel(gx + 1, y + 2)
        g.text("C", gx + 4, y, -1, 1)


# ---------------------------------------------------------------- hovudprogram

gu = GalacticUnicorn()
g = PicoGraphics(DISPLAY)
gu.set_brightness(0.5)

veret = Veret(g)
sover = False
sov_var_nede = False

BILETE_MS = 30   # ca. 33 bilete i sekundet

while True:
    start = time.ticks_ms()

    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
        gu.adjust_brightness(+0.01)
    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
        gu.adjust_brightness(-0.01)

    nede = gu.is_pressed(GalacticUnicorn.SWITCH_SLEEP)
    if nede and not sov_var_nede:
        sover = not sover
        if sover:
            g.set_pen(g.create_pen(0, 0, 0))
            g.clear()
            gu.update(g)
    sov_var_nede = nede

    if not sover:
        veret.draw(start)
        gu.update(g)

    brukt = time.ticks_diff(time.ticks_ms(), start)
    time.sleep_ms(max(1, BILETE_MS - brukt))
