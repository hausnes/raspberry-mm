# Hentar verdata frå YR (api.met.no), med Open-Meteo som reserve.
# Blir brukt av både veret.py og klokke.py - legg fila på Picoen saman med dei.
import gc

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


def hent_ver():
    """Prøv YR først, så Open-Meteo. Gir dict med temp, vind, type, styrke, natt - eller None."""
    gc.collect()
    for kjelde in (hent_yr, hent_open_meteo):
        try:
            d = kjelde()
            if d["temp"] is not None:
                return d
        except Exception as e:
            print("Klarte ikkje hente ver:", e)
        finally:
            gc.collect()
    return None
