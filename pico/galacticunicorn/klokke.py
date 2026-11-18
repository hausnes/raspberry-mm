# Klokke med vêr på Galactic Unicorn (53 x 11 pikslar).
# Hentar rett tid frå internett (NTP) og reknar om til norsk tid,
# med sommartid frå siste søndag i mars til siste søndag i oktober.
#
#   [ 14:37 ][ikon][ 7° ]   klokke til venstre, lite vêrsymbol og temperatur til høgre
#
#   Dag (06:30-20:00):  lyse fargar som glir sakte gjennom regnbogen i løpet av dagen
#   Natt (20:00-06:30): dempa, varme raud-/oransjefargar som ikkje lyser opp rommet
#
#   A:              vis datoen i nokre sekund
#   B:              skru sekund-linja nedst av/på
#   C:              nedteljing til julaften (trykk igjen for å gå tilbake)
#   Lysstyrke +/-:  lysstyrke
#   Zzz:            skru skjermen av/på
#
# Treng secrets.py (WIFI_SSID, WIFI_PASSWORD, gjerne KONTAKT) og verdata.py på Picoen.
# Gi fila namnet main.py på Picoen om ho skal starte av seg sjølv.
import time
import math
import random
import network
import ntptime
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY
from verdata import hent_ver

W = GalacticUnicorn.WIDTH      # 53
H = GalacticUnicorn.HEIGHT     # 11

NATT_START = 20 * 60           # 20:00, i minutt etter midnatt
NATT_SLUTT = 6 * 60 + 30       # 06:30
NATT_DEMP = 0.35               # kor mykje vêrsymbol og tekst blir dempa om natta
SYNK_KVAR = 6 * 3600           # hent tida frå internett på nytt kvar 6. time
VER_KVAR = 20 * 60             # hent nytt vêr kvart 20. minutt
DATO_SEK = 4                   # kor lenge datoen blir vist når du trykkjer A
JUL_SEK = 10                   # kor lenge julenedteljinga blir vist når du trykkjer C

MAANADER = ("JAN", "FEB", "MAR", "APR", "MAI", "JUN",
            "JUL", "AUG", "SEP", "OKT", "NOV", "DES")


# ---------------------------------------------------------------- tid

def siste_sondag(aar, mnd):
    """Klokka 01:00 UTC siste søndag i månaden (mars og oktober har 31 dagar)."""
    t = time.mktime((aar, mnd, 31, 1, 0, 0, 0, 0))
    vekedag = time.localtime(t)[6]          # 0 = måndag, 6 = søndag
    dag = 31 - (vekedag + 1) % 7
    return time.mktime((aar, mnd, dag, 1, 0, 0, 0, 0))


def norsk_tid():
    """RTC-en går på UTC etter ntptime.settime(). Legg til 1 eller 2 timar."""
    utc = time.time()
    aar = time.localtime(utc)[0]
    sommar = siste_sondag(aar, 3) <= utc < siste_sondag(aar, 10)
    return time.localtime(utc + (2 if sommar else 1) * 3600)


def er_natt(t):
    m = t[3] * 60 + t[4]
    return m >= NATT_START or m < NATT_SLUTT


def dagar_til_jul(t):
    aar = t[0]
    if t[1] == 12 and t[2] > 24:
        aar += 1                            # jula er over, tel ned til neste år
    i_dag = time.mktime((t[0], t[1], t[2], 12, 0, 0, 0, 0))
    jul = time.mktime((aar, 12, 24, 12, 0, 0, 0, 0))
    return (jul - i_dag) // 86400


def koble_til_wifi(wlan):
    if wlan.isconnected():
        return
    from secrets import WIFI_SSID, WIFI_PASSWORD
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)


def synk_tid():
    try:
        ntptime.settime()
        print("Tida er henta:", norsk_tid())
        return True
    except Exception as e:
        print("Klarte ikkje hente tida:", e)
        return False


# ---------------------------------------------------------------- fargar

gu = GalacticUnicorn()
g = PicoGraphics(DISPLAY)
gu.set_brightness(0.5)

SVART = g.create_pen(0, 0, 0)
GRAA = g.create_pen(90, 90, 90)
demp = 1.0                     # 1.0 om dagen, NATT_DEMP om natta (blir sett i hovudløkka)


def penn(r, gr, b):
    """Lag ein penn, dempa om det er natt."""
    return g.create_pen(int(r * demp), int(gr * demp), int(b * demp))


def hsv(h, s, v):
    """Fargetone h (0-1), metning s (0-1), lysstyrke v (0-1) -> (r, g, b)."""
    h = h % 1.0
    i = int(h * 6)
    f = h * 6 - i
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    r, g_, b = ((v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q))[i % 6]
    return int(r * 255), int(g_ * 255), int(b * 255)


def farge(t, nr):
    """Farge til teikn nummer nr (0-4) i klokka."""
    if er_natt(t):
        # raud mot oransje, dempa
        return hsv(0.02 + nr * 0.012, 1.0, NATT_DEMP)
    # fargetonen går ein heil runde i løpet av dagen, kvart teikn litt forskyvd
    minutt = t[3] * 60 + t[4]
    return hsv(minutt / 840 + nr * 0.05, 0.55, 1.0)


def teikn_bilete(bilete, x, y, fargar):
    """Teikn eit lite pikselbilete. fargar: {teikn: penn}, '.' er gjennomsiktig."""
    for dy, rad in enumerate(bilete):
        for dx, c in enumerate(rad):
            if c in fargar:
                g.set_pen(fargar[c])
                g.pixel(x + dx, y + dy)


# ---------------------------------------------------------------- liten font (3 x 5) til temperaturen

SMAA = {
    "0": ("###", "#.#", "#.#", "#.#", "###"),
    "1": (".#", "##", ".#", ".#", ".#"),
    "2": ("###", "..#", "###", "#..", "###"),
    "3": ("###", "..#", ".##", "..#", "###"),
    "4": ("#.#", "#.#", "###", "..#", "..#"),
    "5": ("###", "#..", "###", "..#", "###"),
    "6": ("###", "#..", "###", "#.#", "###"),
    "7": ("###", "..#", "..#", ".#.", ".#."),
    "8": ("###", "#.#", "###", "#.#", "###"),
    "9": ("###", "#.#", "###", "..#", "###"),
    "-": ("..", "..", "##", "..", ".."),
    "°": (".#.", "#.#", ".#.", "...", "..."),
}


def smaa_breidd(tekst):
    return sum(len(SMAA[c][0]) for c in tekst) + len(tekst) - 1


def smaa_tekst(tekst, x, y, p):
    for c in tekst:
        teikn_bilete(SMAA[c], x, y, {"#": p})
        x += len(SMAA[c][0]) + 1


# ---------------------------------------------------------------- vêrsymbol (ca. 11 x 10 pikslar)

SKY = (
    "...###...",
    ".#######.",
    "#########",
    "#########",
    ".+++++++.",
)
LYN = ((6, 5), (5, 6), (4, 7), (5, 7), (6, 7), (5, 8), (4, 9))


def sky(x, y, mork=False):
    if mork:
        teikn_bilete(SKY, x, y, {"#": penn(110, 110, 125), "+": penn(60, 60, 70)})
    else:
        teikn_bilete(SKY, x, y, {"#": penn(210, 210, 220), "+": penn(130, 130, 145)})


def sol(cx, cy, straale, f):
    lys, mork = penn(255, 200, 40), penn(200, 90, 0)
    for i in range(8):
        a = i * 0.785
        g.set_pen(lys if (i + f // 10) % 2 else mork)
        g.pixel(int(cx + math.cos(a) * straale + 0.5), int(cy + math.sin(a) * straale + 0.5))
    g.set_pen(penn(255, 180, 0))
    g.circle(cx, cy, 2)


def maane(cx, cy, r):
    g.set_pen(penn(230, 225, 170))
    g.circle(cx, cy, r)
    g.set_pen(SVART)
    g.circle(cx + 2, cy - 1, r)


def nedbor(x, ver, f):
    """Regndropar og/eller snøflak under ei sky."""
    n = ver["styrke"] + 1           # 2-4 dropar, spreidde under skya
    for i in range(n):
        px = x + 2 + i * 6 // (n - 1)
        py = 5 + (f // 4 + i * 2) % 5
        snoe = ver["type"] == "snoe" or (ver["type"] == "sludd" and i % 2)
        if snoe:
            g.set_pen(penn(255, 255, 255))
            g.pixel(px, py)
        else:
            g.set_pen(penn(80, 150, 255))
            g.pixel(px, py)
            if py > 5:
                g.set_pen(penn(25, 55, 140))
                g.pixel(px, py - 1)


def teikn_ver(x, ver, f):
    t = ver["type"]
    natt = ver["natt"]
    if t == "sol":
        if natt:
            maane(x + 5, 5, 3)
            g.set_pen(penn(200, 200, 230) if (f // 20) % 3 else penn(50, 50, 60))
            g.pixel(x + 1, 1)
            g.pixel(x + 9, 8)
        else:
            sol(x + 5, 5, 4, f)
    elif t == "delvis":
        if natt:
            maane(x + 6, 3, 2)
        else:
            sol(x + 6, 3, 3, f)
        sky(x + (f // 40) % 2, 5)
    elif t == "sky":
        sky(x + 2, 0, mork=True)
        sky(x, 4)
    elif t == "taake":
        for rad in (1, 3, 5, 7, 9):
            for i in range(10):
                if (i + f // 8 + rad) % 6:
                    v = 60 + 30 * ((i + rad) % 3)
                    g.set_pen(penn(v, v, v + 5))
                    g.pixel(x + i, rad)
    else:   # regn, sludd, snø, torden
        nedbor(x, ver, f)
        if t == "torden" and f % 70 < 5:
            g.set_pen(penn(255, 255, 120))
            for px, py in LYN:
                g.pixel(x + px, py)
        sky(x + 1, 0, mork=t in ("regn", "torden"))


def teikn_temp(x0, x1, temp):
    """Temperatur sentrert mellom x0 og x1, med gradteikn om det er plass."""
    temp = int(round(temp))
    tekst = "{}°".format(temp)
    if smaa_breidd(tekst) > x1 - x0:
        tekst = str(temp)
    w = smaa_breidd(tekst)
    p = penn(255, 140, 40) if temp > 0 else penn(100, 170, 255)
    smaa_tekst(tekst, x0 + (x1 - x0 - w) // 2, 3, p)


# ---------------------------------------------------------------- klokke

g.set_font("bitmap8")
# Fast breidd per siffer, så klokka ikkje hoppar når t.d. "1" blir til "2"
SIFFER_B = max(g.measure_text(str(d), 1) for d in range(10))
KOLON_B = 3
KLOKKE_B = 4 * SIFFER_B + KOLON_B
TEKST_Y = 1


def teikn_klokke(t, x, vis_sekund):
    g.set_font("bitmap8")
    tekst = "{:02d}{:02d}".format(t[3], t[4])
    for nr in range(5):
        g.set_pen(g.create_pen(*farge(t, nr)))
        if nr == 2:
            # kolonet blinkar ein gong i sekundet
            if t[5] % 2 == 0:
                g.rectangle(x, TEKST_Y + 1, 2, 2)
                g.rectangle(x, TEKST_Y + 4, 2, 2)
            x += KOLON_B
        else:
            c = tekst[nr if nr < 2 else nr - 1]
            g.text(c, x + (SIFFER_B - g.measure_text(c, 1)) // 2, TEKST_Y, -1, 1)
            x += SIFFER_B

    if vis_sekund:
        # sekund-linje nedst: veks frå venstre til høgre i løpet av minuttet
        lengd = (t[5] + 1) * W // 60
        r, gr, b = farge(t, 4)
        g.set_pen(g.create_pen(r // 4, gr // 4, b // 4))
        g.line(0, H - 1, W, H - 1)
        g.set_pen(g.create_pen(r, gr, b))
        if lengd > 0:
            g.line(0, H - 1, lengd, H - 1)


def teikn_dato(t):
    g.set_font("bitmap8")
    tekst = "{}. {}".format(t[2], MAANADER[t[1] - 1])
    w = g.measure_text(tekst, 1)
    g.set_pen(g.create_pen(*farge(t, 2)))
    g.text(tekst, (W - w) // 2, TEKST_Y + 1, -1, 1)


def teikn_melding(tekst, f):
    g.set_font("bitmap8")
    w = g.measure_text(tekst, 1)
    g.set_pen(GRAA)
    g.text(tekst, (40 - w) // 2, 2, -1, 1)
    aktiv = (f // 8) % 3
    for i in range(3):
        g.set_pen(g.create_pen(255, 255, 255) if i == aktiv else GRAA)
        g.rectangle(41 + i * 4, 5, 2, 2)


# ---------------------------------------------------------------- julenedteljing

TRE = (
    "...*...",
    "...#...",
    "..#o#..",
    ".#####.",
    "..#o#..",
    ".o###o.",
    "###o###",
    "...|...",
    "...|...",
)
KULER = ((255, 40, 40), (255, 200, 0), (60, 120, 255), (255, 80, 200))
snoflak = [[random.uniform(0, W), random.uniform(0, H), random.uniform(0.05, 0.15)] for _ in range(14)]


def skriv_som_passar(kandidatar, x0, x1, y_bitmap8, p):
    """Skriv den første teksten som får plass mellom x0 og x1."""
    for tekst, font in kandidatar:
        g.set_font(font)
        w = g.measure_text(tekst, 1)
        if w <= x1 - x0:
            g.set_pen(p)
            g.text(tekst, x0 + (x1 - x0 - w) // 2, y_bitmap8 + (1 if font == "bitmap6" else 0), -1, 1)
            return


def teikn_jul(t, f):
    # snø som dalar sakte i bakgrunnen
    g.set_pen(penn(70, 70, 90))
    for s in snoflak:
        s[1] += s[2]
        s[0] += math.sin(f * 0.05 + s[2] * 40) * 0.05
        if s[1] >= H:
            s[0], s[1] = random.uniform(0, W), 0
        g.pixel(int(s[0]), int(s[1]))

    # juletre med blinkande kuler
    kule = (f // 10) % len(KULER)
    teikn_bilete(TRE, 1, 1, {
        "#": penn(0, 150, 40),
        "|": penn(110, 60, 20),
        "*": penn(255, 230, 80) if (f // 6) % 2 else penn(160, 120, 20),
    })
    nr = 0
    for y, rad in enumerate(TRE):
        for x, c in enumerate(rad):
            if c == "o":
                g.set_pen(penn(*KULER[(kule + nr) % len(KULER)]))
                g.pixel(1 + x, 1 + y)
                nr += 1

    n = dagar_til_jul(t)
    x0 = 10
    if n == 0:
        r, gr, b = hsv(f / 100, 0.8, 1.0)
        skriv_som_passar((("GOD JUL!", "bitmap8"), ("GOD JUL!", "bitmap6"), ("JUL!", "bitmap8")),
                         x0, W, 2, penn(r, gr, b))
    elif (f // 40) % 3 == 2:
        # annankvar gong: kva vi tel ned til
        skriv_som_passar((("TIL JUL", "bitmap8"), ("TIL JUL", "bitmap6")), x0, W, 2, penn(200, 30, 30))
    else:
        eining = "DAG" if n == 1 else "DAGAR"
        skriv_som_passar((("{} {}".format(n, eining), "bitmap8"),
                          ("{} {}".format(n, eining), "bitmap6"),
                          (str(n), "bitmap8")),
                         x0, W, 2, penn(255, 255, 255))


# ---------------------------------------------------------------- hovudprogram

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
koble_til_wifi(wlan)

har_tid = False
sist_synk = 0
wifi_start = time.ticks_ms()

ver = None
neste_ver = 0                  # time.time() når vi skal hente vêr neste gong

vis_sekund = True
modus = "klokke"               # "klokke", "dato" eller "jul"
modus_til = 0
sover = False
var_nede = {}
f = 0


def trykt(knapp):
    """True berre i augneblinken knappen blir trykt ned."""
    nede = gu.is_pressed(knapp)
    ny = nede and not var_nede.get(knapp, False)
    var_nede[knapp] = nede
    return ny


while True:
    f += 1
    no = time.time()

    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
        gu.adjust_brightness(+0.01)
    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
        gu.adjust_brightness(-0.01)
    if trykt(GalacticUnicorn.SWITCH_SLEEP):
        sover = not sover
    if trykt(GalacticUnicorn.SWITCH_A):
        modus, modus_til = "dato", no + DATO_SEK
    if trykt(GalacticUnicorn.SWITCH_B):
        vis_sekund = not vis_sekund
    if trykt(GalacticUnicorn.SWITCH_C):
        if modus == "jul":
            modus = "klokke"
        else:
            modus, modus_til = "jul", no + JUL_SEK
    if modus != "klokke" and no >= modus_til:
        modus = "klokke"

    # hent tida første gong, og deretter med jamne mellomrom
    if not har_tid or no - sist_synk > SYNK_KVAR:
        if wlan.isconnected():
            if synk_tid():
                har_tid = True
                sist_synk = no = time.time()
                neste_ver = 0
            elif har_tid:
                sist_synk += 300          # prøv igjen om 5 minutt
        elif time.ticks_diff(time.ticks_ms(), wifi_start) > 20000:
            koble_til_wifi(wlan)          # prøv å koble til på nytt
            wifi_start = time.ticks_ms()

    # hent vêret (tek eit par sekund, då står klokka stille litt)
    if har_tid and wlan.isconnected() and no >= neste_ver:
        ny = hent_ver()
        if ny is not None:
            ver = ny
            neste_ver = time.time() + VER_KVAR
        else:
            neste_ver = time.time() + 120     # prøv igjen om 2 minutt
        no = time.time()

    g.set_pen(SVART)
    g.clear()
    if sover:
        pass
    elif not har_tid:
        teikn_melding("WIFI" if not wlan.isconnected() else "TID", f)
    else:
        t = norsk_tid()
        demp = NATT_DEMP if er_natt(t) else 1.0
        if modus == "dato":
            teikn_dato(t)
        elif modus == "jul":
            teikn_jul(t, f)
        elif ver is None:
            teikn_klokke(t, (W - KLOKKE_B) // 2, vis_sekund)
        else:
            teikn_klokke(t, 0, vis_sekund)
            ikon_x = KLOKKE_B + 1
            teikn_ver(ikon_x, ver, f)
            teikn_temp(ikon_x + 12, W, ver["temp"])

    gu.update(g)
    time.sleep_ms(50)
