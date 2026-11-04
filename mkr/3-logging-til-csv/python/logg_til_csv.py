"""
Les målingar frå Arduinoen over USB (seriellport) og lagre dei i ei CSV-fil.

Arduinoen sender éi linje per måling, til dømes "21.44".
Dette skriptet legg til tidspunktet frå datamaskina og skriv:

    tid,temperatur
    2026-11-10 09:15:03,21.44

Køyr skriptet i terminalen i VS Code:
    python logg_til_csv.py          (Windows)
    python3 logg_til_csv.py         (Mac)

Stopp loggen med Ctrl + C.

NB: Serial Monitor i Arduino IDE må vere lukka. Berre eitt program
kan bruke seriellporten om gongen.
"""

import csv
import os
from datetime import datetime

import serial                      # pip install pyserial
from serial.tools import list_ports

# ---- Innstillingar du kan endre ----
PORT = None                    # None = finn Arduinoen automatisk. Elles t.d. "COM3" eller "/dev/cu.usbmodem14101"
BAUD = 9600                    # må vere lik Serial.begin(...) i Arduino-koden
FILNAMN = "maalingar.csv"
KOLONNAR = ["temperatur"]      # namna på verdiane Arduinoen sender, i same rekkjefølgje
# ------------------------------------


def finn_arduino():
    """Gå gjennom alle seriellportar og returner den første som er eit Arduino-kort."""
    portar = list_ports.comports()
    for p in portar:
        if p.vid == 0x2341:  # 0x2341 er produsent-ID-en til Arduino
            return p.device

    print("Fann ikkje noko Arduino-kort. Desse portane finst:")
    for p in portar:
        print("  ", p.device, "-", p.description)
    return None


def main():
    port = PORT or finn_arduino()
    if port is None:
        print("Set PORT øvst i skriptet til rett port, og prøv igjen.")
        return

    # Skal vi skrive overskrift? Berre om fila ikkje finst frå før.
    ny_fil = not os.path.exists(FILNAMN)

    with serial.Serial(port, BAUD, timeout=10) as arduino, \
         open(FILNAMN, "a", newline="", encoding="utf-8") as fil:

        skrivar = csv.writer(fil)
        if ny_fil:
            skrivar.writerow(["tid"] + KOLONNAR)

        print(f"Loggar frå {port} til {FILNAMN}. Stopp med Ctrl + C.")

        while True:
            linje = arduino.readline().decode("utf-8", errors="ignore").strip()

            if linje == "":
                continue                    # timeout utan data
            if linje.startswith("#"):
                print("Arduino seier:", linje)
                continue                    # meldingar skal ikkje i fila

            verdiar = linje.split(",")
            if len(verdiar) != len(KOLONNAR):
                print("Hoppar over rar linje:", linje)
                continue

            tid = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            skrivar.writerow([tid] + verdiar)
            fil.flush()                     # skriv til disk med ein gong
            print(tid, verdiar)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nLogginga er stoppa.")
    except serial.SerialException as feil:
        print("Problem med seriellporten:", feil)
        print("Er Serial Monitor i Arduino IDE open? Lukk han og prøv igjen.")
