#!/usr/bin/env python3
"""
Verstasjon med Enviro+ (Pimoroni) på Raspberry Pi.

Les temperatur, lufttrykk, luftfukt og svevestøv (PM2.5 og PM10), og lagrar
målingane i ei CSV-fil og/eller sender dei til Thingspeak.

To måtar å køyre programmet på:
    python3 verstasjon.py             -> måler kvar INTERVALL-sekund til du trykkjer Ctrl+C
    python3 verstasjon.py --ein-gong  -> tek éi måling og avsluttar (passar for crontab)

Sjå README.md for meir forklaring.
"""

# ==================================================================
#  INNSTILLINGAR - det er stort sett berre her du treng endre noko
# ==================================================================

BRUK_CSV = True          # Skriv målingane til CSV-fil?
BRUK_THINGSPEAK = True   # Send målingane til Thingspeak?
BRUK_SKJERM = True       # Vis temperatur og Wi-Fi-status på den vesle skjermen?
BRUK_PMS5003 = True      # Er svevestøvsensoren (PMS5003) kopla til?

INTERVALL = 60           # Sekund mellom kvar måling (gjeld berre når programmet går i løkke)

# Filnamn utan full sti blir lagra i same mappe som dette programmet
CSV_FIL = "verstasjon.csv"

THINGSPEAK_API_KEY = "DIN_WRITE_API_KEY"  # NB: Ikkje del denne med andre!

# Kva felt i Thingspeak-kanalen kvar verdi skal til.
# Fjern ei linje dersom du ikkje vil sende den verdien.
THINGSPEAK_FELT = {
    "temperatur": "field1",
    "trykk": "field2",
    "fuktighet": "field3",
    "pm25": "field4",
    "pm10": "field5",
}

# Temperatursensoren sit nær prosessoren (CPU) og blir varma opp av den.
# Høgare tal gir mindre korrigering. Juster ved å samanlikne med eit vanleg termometer.
KOMPENSASJONSFAKTOR = 2.25

# Kor mange sekund svevestøvsensoren får gå før første måling (vifta må kome i gang)
PMS_OPPVARMING = 30

# ==================================================================
#  Herifrå og ned treng du normalt ikkje endre noko
# ==================================================================

import argparse
import csv
import logging
import os
import subprocess
import sys
import time
from datetime import datetime

import requests  # For å sende data til Thingspeak

KOLONNAR = ["tidspunkt", "temperatur", "trykk", "fuktighet", "pm25", "pm10"]
THINGSPEAK_URL = "https://api.thingspeak.com/update"
MAPPE = os.path.dirname(os.path.abspath(__file__))  # Mappa dette programmet ligg i

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger("verstasjon")


# ---------- Oppstart av sensorar og skjerm ----------

def start_bme280():
    """Startar sensoren for temperatur, trykk og luftfukt."""
    try:
        from smbus2 import SMBus
    except ImportError:
        from smbus import SMBus
    from bme280 import BME280

    bme280 = BME280(i2c_dev=SMBus(1))
    bme280.get_temperature()  # Første avlesing er ofte feil, så me kastar den
    time.sleep(1)
    return bme280


def start_pms5003():
    """Startar svevestøvsensoren og ventar til han er klar."""
    from pms5003 import PMS5003

    pms5003 = PMS5003()
    log.info("Ventar %s sek. medan svevestøvsensoren varmar opp ...", PMS_OPPVARMING)
    time.sleep(PMS_OPPVARMING)
    return pms5003


def start_skjerm():
    """Startar LCD-skjermen. Returnerer (skjerm, font)."""
    from PIL import ImageFont
    from fonts.ttf import RobotoMedium

    try:
        import st7735  # Ny versjon av biblioteket
        skjerm = st7735.ST7735(port=0, cs=1, dc="GPIO9", backlight="GPIO12",
                               rotation=270, spi_speed_hz=10000000)
    except ImportError:
        import ST7735  # Eldre versjon av biblioteket
        skjerm = ST7735.ST7735(port=0, cs=1, dc=9, backlight=12,
                               rotation=270, spi_speed_hz=10000000)
    skjerm.begin()
    font = ImageFont.truetype(RobotoMedium, 16)
    return skjerm, font


def prov_a_starte(namn, startfunksjon):
    """Køyrer startfunksjonen. Går det gale, loggar me feilen og returnerer None."""
    try:
        resultat = startfunksjon()
        log.info("%s er klar.", namn)
        return resultat
    except Exception as feil:
        log.error("Klarte ikkje starte %s: %s", namn, feil)
        return None


# ---------- Avlesing av sensorar ----------

def cpu_temperatur():
    with open("/sys/class/thermal/thermal_zone0/temp") as f:
        return int(f.read()) / 1000.0


def les_svevestov(pms5003):
    """Returnerer (pm25, pm10). Prøver opptil tre gonger før me gir opp."""
    from pms5003 import ReadTimeoutError, ChecksumMismatchError

    # Sensoren sender nye tal heile tida. Me tømer bufferen slik at me får
    # ferske tal og ikkje dei som har hopa seg opp sidan sist.
    serieport = getattr(pms5003, "_serial", None)
    if serieport is not None:
        serieport.reset_input_buffer()

    for forsok in range(3):
        try:
            data = pms5003.read()
            return data.pm_ug_per_m3(2.5), data.pm_ug_per_m3(10)
        except (ReadTimeoutError, ChecksumMismatchError) as feil:
            log.warning("Klarte ikkje lese PMS5003 (%s). Nullstiller og prøver igjen.", feil)
            pms5003.reset()
    return None, None


def les_sensorar(bme280, pms5003):
    """Les alle sensorane og returnerer ei ordbok (dict) med målingane.
    Verdiar som ikkje kunne lesast blir None (tom celle i CSV-fila)."""
    maling = dict.fromkeys(KOLONNAR)
    maling["tidspunkt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if bme280 is not None:
        try:
            ra_temp = bme280.get_temperature()
            maling["temperatur"] = round(ra_temp - (cpu_temperatur() - ra_temp) / KOMPENSASJONSFAKTOR, 2)
            maling["trykk"] = round(bme280.get_pressure(), 2)
            maling["fuktighet"] = round(bme280.get_humidity(), 2)
        except Exception as feil:
            log.error("Feil ved lesing av BME280: %s", feil)

    if pms5003 is not None:
        try:
            maling["pm25"], maling["pm10"] = les_svevestov(pms5003)
        except Exception as feil:
            log.error("Feil ved lesing av PMS5003: %s", feil)

    return maling


# ---------- Lagring og visning ----------

def skriv_til_csv(maling):
    """Legg målinga til nedst i CSV-fila. Overskrifter blir laga om fila er ny."""
    filnamn = os.path.join(MAPPE, CSV_FIL)
    ny_fil = not os.path.exists(filnamn) or os.path.getsize(filnamn) == 0
    try:
        with open(filnamn, "a", newline="", encoding="utf-8") as f:  # "a" = append (legg til)
            skrivar = csv.DictWriter(f, fieldnames=KOLONNAR)
            if ny_fil:
                skrivar.writeheader()
            skrivar.writerow(maling)
        log.info("Lagra i %s", filnamn)
    except OSError as feil:
        log.error("Klarte ikkje skrive til %s: %s", filnamn, feil)


def send_til_thingspeak(maling):
    data = {"api_key": THINGSPEAK_API_KEY}
    for namn, felt in THINGSPEAK_FELT.items():
        if maling.get(namn) is not None:
            data[felt] = maling[namn]

    try:
        svar = requests.post(THINGSPEAK_URL, data=data, timeout=10)
    except requests.RequestException as feil:
        log.error("Fekk ikkje kontakt med Thingspeak: %s", feil)
        return

    # Thingspeak svarar med nummeret på den nye oppføringa, eller "0" om ho vart avvist
    if svar.status_code == 200 and svar.text.strip() != "0":
        log.info("Sendt til Thingspeak (oppføring nr. %s)", svar.text.strip())
    else:
        log.error("Thingspeak avviste målinga (status %s, svar '%s'). Sjekk API-nøkkelen, "
                  "og at det har gått minst 15 sek. sidan førre sending.",
                  svar.status_code, svar.text.strip())


def har_nettverk():
    try:
        return bool(subprocess.check_output(["hostname", "-I"]).strip())
    except (OSError, subprocess.CalledProcessError):
        return False


def vis_pa_skjerm(skjerm_og_font, maling):
    """Viser temperatur og Wi-Fi-status. Bakgrunnen er raud om me manglar nettverk."""
    from PIL import Image, ImageDraw

    skjerm, font = skjerm_og_font
    wifi = har_nettverk()
    temp = maling["temperatur"]
    tekst = (f"{temp:.1f} °C" if temp is not None else "-- °C")
    tekst += "\nWi-Fi: " + ("OK" if wifi else "manglar")
    bakgrunn = (0, 170, 170) if wifi else (85, 15, 15)

    bilete = Image.new("RGB", (skjerm.width, skjerm.height), bakgrunn)
    teikn = ImageDraw.Draw(bilete)
    venstre, topp, hogre, botn = teikn.multiline_textbbox((0, 0), tekst, font=font)
    x = (skjerm.width - (hogre - venstre)) / 2
    y = (skjerm.height - (botn - topp)) / 2
    teikn.multiline_text((x, y), tekst, font=font, fill=(255, 255, 255), align="center")
    skjerm.display(bilete)


# ---------- Hovudprogram ----------

def ta_maling(bme280, pms5003, skjerm):
    maling = les_sensorar(bme280, pms5003)
    log.info("Måling: %s", maling)

    if BRUK_CSV:
        skriv_til_csv(maling)
    if BRUK_THINGSPEAK:
        send_til_thingspeak(maling)
    if skjerm is not None:
        try:
            vis_pa_skjerm(skjerm, maling)
        except Exception as feil:
            log.error("Feil ved oppdatering av skjermen: %s", feil)


def main():
    parser = argparse.ArgumentParser(description="Verstasjon med Enviro+")
    parser.add_argument("--ein-gong", action="store_true",
                        help="ta éi måling og avslutt (for bruk med crontab)")
    args = parser.parse_args()

    # Åtvaringar om innstillingar som truleg er feil
    if not BRUK_CSV and not BRUK_THINGSPEAK:
        log.warning("Både CSV og Thingspeak er slått av. Målingane blir berre viste her.")
    if BRUK_THINGSPEAK and THINGSPEAK_API_KEY == "DIN_WRITE_API_KEY":
        log.warning("Du har ikkje lagt inn Thingspeak-nøkkelen din (THINGSPEAK_API_KEY).")
    if BRUK_THINGSPEAK and not args.ein_gong and INTERVALL < 15:
        log.warning("Thingspeak tek berre imot éi måling kvart 15. sekund. Auk INTERVALL.")

    bme280 = prov_a_starte("BME280", start_bme280)
    pms5003 = prov_a_starte("PMS5003", start_pms5003) if BRUK_PMS5003 else None
    skjerm = prov_a_starte("Skjermen", start_skjerm) if BRUK_SKJERM else None

    if bme280 is None and pms5003 is None:
        log.error("Ingen sensorar fungerer. Avsluttar.")
        sys.exit(1)

    if args.ein_gong:
        ta_maling(bme280, pms5003, skjerm)
        return

    log.info("Måler kvart %s. sekund. Trykk Ctrl+C for å avslutte.", INTERVALL)
    try:
        while True:
            neste_maling = time.monotonic() + INTERVALL
            try:
                ta_maling(bme280, pms5003, skjerm)
            except Exception:
                # Uventa feil skal ikkje stoppe verstasjonen. Me loggar og held fram.
                log.exception("Uventa feil. Prøver igjen ved neste måling.")
            time.sleep(max(0, neste_maling - time.monotonic()))
    except KeyboardInterrupt:
        log.info("Avsluttar. Ha det!")


if __name__ == "__main__":
    main()
