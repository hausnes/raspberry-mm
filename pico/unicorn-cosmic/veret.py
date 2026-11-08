# Veret i Bergen frå YR (api.met.no), med animasjon og lydeffektar.
# Fell tilbake på Open-Meteo om YR ikkje svarar.
import time
import math
import random
import gc
from cosmic import Channel
from lyd import Ko

_diff = time.ticks_diff
_add = time.ticks_add

# Bergen sentrum (met.no vil ha maks 4 desimalar)
LAT = 60.3913
LON = 5.3221

YR_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={}&lon={}".format(LAT, LON)

# met.no krev at User-Agent seier kven du er, med kontaktinfo (e-post eller nettside).
# Byt ut KONTAKT med din eigen, elles kan du bli blokkert (svar 403).
KONTAKT = "byt-ut-med-di-epost@example.com"
USER_AGENT = "CosmicUnicornVeret/1.0 " + KONTAKT

OPEN_METEO_URL = ("http://api.open-meteo.com/v1/forecast?latitude={}&longitude={}"
                  "&current=temperature_2m,precipitation,weather_code,wind_speed_10m,is_day"
                  "&wind_speed_unit=ms").format(LAT, LON)

OPPDATER_MS = 20 * 60 * 1000   # hent nytt ver kvart 20. minutt
VINDGRENSE = 6.0               # m/s - frå denne farten viser/spelar vi vind

ANIM_H = 23                    # rad 0-22: animasjon, rad 23-31: tekst


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
    if kode in (51, 53, 55, 56, 57):
        return "regn", 1
    if kode in (61, 80):
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


# ---------------------------------------------------------------- modus

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
        self.tore_tid = None
        self.ko = Ko()
        self.vind_fase = 0.0

        p = g.create_pen
        self.SVART = p(0, 0, 0)
        self.KVIT = p(255, 255, 255)
        self.GRAA = p(150, 150, 150)
        self.SOL = p(255, 180, 0)
        self.SOL_LYS = p(255, 230, 90)
        self.STRAALE = p(255, 130, 0)
        self.MANE = p(230, 225, 170)
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
        self.STJERNER = [(3, 3), (27, 5), (22, 16), (5, 14), (14, 2), (29, 19), (9, 20)]

    # ---------- livssyklus
    def start(self):
        self.f = 0
        if self.data is None or self._for_gammal(time.ticks_ms()):
            self._start_wifi()

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

        self._scene(no)

    def _melding(self, tekst):
        g = self.g
        g.set_pen(self.SVART)
        g.clear()
        g.set_font("bitmap6")
        w = g.measure_text(tekst, 1)
        g.set_pen(self.GRAA)
        g.text(tekst, (32 - w) // 2, 10, -1, 1)
        aktiv = (self.f // 8) % 3
        for i in range(3):
            g.set_pen(self.KVIT if i == aktiv else self.SKY_MORK)
            g.rectangle(10 + i * 5, 20, 2, 2)

    def _lag_partiklar(self):
        d = self.data
        t = d["type"]
        self.partiklar = []
        if t in ("regn", "torden", "sludd"):
            n = (6, 12, 20)[d["styrke"] - 1]
            for _ in range(n):
                self.partiklar.append([random.uniform(-8, 32), random.uniform(7, ANIM_H),
                                       random.uniform(0.7, 1.2), 0.0, 0])
        if t in ("snoe", "sludd"):
            n = (8, 14, 22)[d["styrke"] - 1]
            for _ in range(n):
                self.partiklar.append([random.uniform(-4, 32), random.uniform(4, ANIM_H),
                                       random.uniform(0.12, 0.3), random.uniform(0, 6.28), 1])
        self.straumar = []
        if d["vind"] >= VINDGRENSE:
            for _ in range(min(int(d["vind"] / 4), 5)):
                self.straumar.append([random.uniform(-30, 32), random.randint(1, ANIM_H - 2),
                                      random.randint(4, 9), random.uniform(0.8, 1.6)])

    def _scene(self, no):
        g = self.g
        d = self.data
        t = d["type"]
        natt = d["natt"]

        # bakgrunn
        if natt:
            g.set_pen(g.create_pen(0, 0, 5))
        elif t in ("sol", "delvis"):
            g.set_pen(g.create_pen(0, 10, 40))
        elif t in ("regn", "torden", "sludd"):
            g.set_pen(g.create_pen(3, 4, 10))
        else:
            g.set_pen(g.create_pen(7, 8, 14))
        if self.lyn > 0:
            g.set_pen(g.create_pen(60 * self.lyn, 60 * self.lyn, 70 * self.lyn))
        g.clear()

        g.set_clip(0, 0, 32, ANIM_H)
        f = self.f

        if t == "sol":
            if natt:
                self._stjerner()
                self._mane(16, 11)
            else:
                self._sol(16, 11, 6)
        elif t == "delvis":
            if natt:
                self._stjerner()
                self._mane(11, 8)
            else:
                self._sol(11, 8, 5)
            x = int(8 + 4 * math.sin(f * 0.01))
            self._sky(x, 9, self.SKY_LYS, self.SKY_SKUGGE)
        elif t == "sky":
            x1 = int((f * 0.12) % 52) - 20
            x2 = int((f * 0.2 + 26) % 52) - 20
            self._sky(x1, 1, self.SKY_SKUGGE, self.SKY_MORK)
            self._sky(x2, 9, self.SKY_LYS, self.SKY_SKUGGE)
        elif t == "taake":
            self._taake()
        else:
            # nedbør: mørke skyer øvst, partiklar under
            lys, skugge = (self.SKY_LYS, self.SKY_SKUGGE) if t == "snoe" else (self.SKY_MORK, self.SKY_MORK_SKUGGE)
            self._oppdater_partiklar(d["vind"])
            self._teikn_partiklar()
            self._sky(-6, -2, lys, skugge)
            self._sky(12, -3, lys, skugge)
            if t == "torden":
                self._torden(no)

        if self.straumar:
            self._vind()

        g.remove_clip()
        self._temperatur(no)

    # ---------- element
    def _sol(self, cx, cy, r):
        g = self.g
        g.set_pen(self.STRAALE)
        for i in range(8):
            a = i * 0.785 + self.f * 0.02
            ca, sa = math.cos(a), math.sin(a)
            lengd = 3 if (i + self.f // 10) % 2 else 2
            for s in range(r + 2, r + 2 + lengd):
                g.pixel(int(cx + ca * s + 0.5), int(cy + sa * s + 0.5))
        g.set_pen(self.SOL)
        g.circle(cx, cy, r)
        g.set_pen(self.SOL_LYS)
        g.circle(cx - 1, cy - 1, r - 3)

    def _mane(self, cx, cy):
        g = self.g
        g.set_pen(self.MANE)
        g.circle(cx, cy, 5)
        g.set_pen(g.create_pen(0, 0, 5))
        g.circle(cx + 3, cy - 2, 4)

    def _stjerner(self):
        g = self.g
        for i, (x, y) in enumerate(self.STJERNER):
            g.set_pen(self.STJERNE[1 if ((self.f + i * 13) // 20) % 4 else 0])
            g.pixel(x, y)

    def _sky(self, x, y, lys, skugge):
        g = self.g
        g.set_pen(skugge)
        g.circle(x + 5, y + 6, 4)
        g.circle(x + 11, y + 5, 5)
        g.circle(x + 16, y + 6, 4)
        g.rectangle(x + 5, y + 6, 12, 5)
        g.set_pen(lys)
        g.circle(x + 5, y + 5, 4)
        g.circle(x + 11, y + 4, 5)
        g.circle(x + 16, y + 5, 4)
        g.rectangle(x + 5, y + 5, 12, 4)

    def _oppdater_partiklar(self, vind):
        dx = min(vind / 8.0, 1.5)
        f = self.f
        for p in self.partiklar:
            if p[4] == 0:   # regndrope
                p[1] += p[2]
                p[0] += dx * p[2] * 0.6
                if p[1] >= ANIM_H or p[0] > 33:
                    p[0] = random.uniform(-10, 30)
                    p[1] = random.uniform(6, 9)
            else:           # snøflak
                p[1] += p[2]
                p[0] += math.sin(f * 0.05 + p[3]) * 0.25 + dx * 0.4
                if p[1] >= ANIM_H or p[0] > 33:
                    p[0] = random.uniform(-6, 30)
                    p[1] = random.uniform(5, 8)

    def _teikn_partiklar(self):
        g = self.g
        for p in self.partiklar:
            x, y = int(p[0]), int(p[1])
            if p[4] == 0:
                g.set_pen(self.DROPE_HALE)
                g.pixel(x - (1 if self.data["vind"] >= VINDGRENSE else 0), y - 1)
                g.set_pen(self.DROPE)
                g.pixel(x, y)
            else:
                g.set_pen(self.KVIT)
                g.pixel(x, y)

    def _torden(self, no):
        g = self.g
        if self.lyn == 0 and random.random() < 0.005:
            self.lyn = 4
            x = random.randint(8, 24)
            self.lyn_punkt = [(x, 8)]
            y = 8
            while y < ANIM_H:
                y += random.randint(2, 4)
                x += random.randint(-3, 3)
                self.lyn_punkt.append((x, y))
            # lyden kjem litt etter lynet, slik som i verkelegheita
            self.tore_tid = _add(no, random.randint(250, 1200))
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
            for x in range(32):
                v = math.sin(x * 0.25 + f * fart + y * 0.9) + math.sin(x * 0.11 - f * 0.02 + y * 0.3)
                g.set_pen(self.TAAKE[int((v + 2) * (n - 1) / 4)])
                g.pixel(x, y)

    def _vind(self):
        g = self.g
        for s in self.straumar:
            s[0] += s[3]
            if s[0] - s[2] > 32:
                s[0] = random.uniform(-25, -2)
                s[1] = random.randint(1, ANIM_H - 2)
            x, y, l = int(s[0]), s[1], s[2]
            for i in range(l):
                g.set_pen(self.VIND[min(2, (l - i) * 3 // l)])
                g.pixel(x - i, y)

    def _temperatur(self, no):
        g = self.g
        d = self.data
        g.set_pen(self.SVART)
        g.rectangle(0, ANIM_H, 32, 32 - ANIM_H)
        g.set_font("bitmap8")

        # vis vindfart i 3 av 10 sekund når det blæs
        if d["vind"] >= VINDGRENSE and (self.f // 30) % 10 >= 7:
            tekst = "{}m/s".format(int(d["vind"] + 0.5))
            w = g.measure_text(tekst, 1)
            if w > 32:
                g.set_font("bitmap6")
                w = g.measure_text(tekst, 1)
            g.set_pen(self.GRAA)
            g.text(tekst, (32 - w) // 2, ANIM_H + 1, -1, 1)
            return

        temp = int(round(d["temp"]))
        tekst = str(temp)
        w = g.measure_text(tekst, 1)
        cw = g.measure_text("C", 1)
        total = w + 4 + cw
        x = (32 - total) // 2
        y = ANIM_H + 1
        g.set_pen(self.VARM if temp > 0 else self.KALD)
        g.text(tekst, x, y, -1, 1)
        # gradsymbol (bitmap-fontane har ikkje °)
        gx = x + w
        g.pixel(gx + 1, y)
        g.pixel(gx, y + 1)
        g.pixel(gx + 2, y + 1)
        g.pixel(gx + 1, y + 2)
        g.text("C", gx + 4, y, -1, 1)

    # ---------- lyd
    def lyd_start(self, k):
        self.ko.tom()
        k[0].configure(waveforms=Channel.NOISE, attack=1, decay=12, sustain=0, release=5, volume=0.2)
        k[1].configure(waveforms=Channel.NOISE, frequency=400, attack=400, decay=10, sustain=1.0, release=400, volume=0.0)
        k[2].configure(waveforms=Channel.NOISE, frequency=120, attack=60, decay=1800, sustain=0, release=300, volume=0.8)
        k[3].configure(waveforms=Channel.SINE, attack=5, decay=10, sustain=0.8, release=30, volume=0.12)
        k[4].configure(waveforms=Channel.NOISE, frequency=9000, attack=400, decay=10, sustain=1.0, release=400, volume=0.0)
        k[1].trigger_attack()
        k[4].trigger_attack()

    def lyd(self, k, no):
        d = self.data
        if d is None:
            return
        self.ko.kjor(no)
        t = d["type"]
        vind = d["vind"]

        # vind: støy som blæs opp og legg seg
        maal = 0.0
        if vind >= 3:
            maal = min(0.03 + (vind - 3) * 0.015, 0.3)
        if t in ("sky", "taake"):
            maal = max(maal, 0.015)
        self.vind_fase += 0.01
        mod = 0.6 + 0.4 * math.sin(self.vind_fase * 1.3) * math.sin(self.vind_fase * 0.37 + 1)
        k[1].volume(maal * mod)
        k[1].frequency(int(250 + 350 * mod))

        # regn: sus + enkeltdropar
        if t in ("regn", "torden", "sludd"):
            k[4].volume(0.02 * d["styrke"])
            rate = (8, 18, 35)[d["styrke"] - 1]
            if random.random() < rate * 0.01:
                k[0].configure(frequency=random.randint(2000, 7000), volume=random.uniform(0.08, 0.25))
                k[0].trigger_attack()
        else:
            k[4].volume(0.0)

        # torebrak
        if self.tore_tid is not None and _diff(no, self.tore_tid) >= 0:
            self.tore_tid = None
            k[2].frequency(random.randint(60, 140))
            k[2].trigger_attack()

        # fuglekvitter når sola skin om dagen
        if not d["natt"] and t in ("sol", "delvis"):
            if random.random() < (0.0025 if t == "sol" else 0.0012):
                self._kvitter(k[3], no)

        # snø: lette, glitrande tonar
        if t in ("snoe", "sludd") and random.random() < 0.006:
            c = k[3]
            c.volume(0.05)
            c.frequency(random.choice((1568, 1760, 2093, 2349, 2637)))
            c.trigger_attack()
            self.ko.om(no, 50, c.trigger_release)

    def _kvitter(self, c, no):
        c.volume(0.12)
        start = 0
        for _ in range(random.randint(2, 4)):
            f0 = random.randint(2800, 3800)
            self.ko.om(no, start, self._tone_paa, c, f0)
            for s in range(1, 6):
                self.ko.om(no, start + s * 10, c.frequency, f0 + s * 150)
            self.ko.om(no, start + 60, c.trigger_release)
            start += random.randint(90, 140)

    @staticmethod
    def _tone_paa(c, f):
        c.frequency(f)
        c.trigger_attack()
