''' 
    Opprett en liste som skal holde på følgende data:
    - Tidspunkt for avlesing (datetime)
    - Temperatur (float)
    - Luftfuktighet (float)
    - Lufttrykk (float)
    - Partikkelkonsentrasjon (float)

    Programmet skal kjøre frem til det blir avsluttet av brukeren.

    Lag en løkke som hvert 5. sekund våkner og skriver tilfeldige verdier til listen.
    Tidspunkt skal være nåværende tidspunkt for avlesing.

    Når programmet blir avsluttet skal listen skrives til en fil med navn "data.csv". 
'''

import random
from datetime import datetime
from time import sleep

print("NB: Trykk på ctrl + c for å avslutte programmet,\n dette vil skrive dataene til filen data.csv")

data = [] # Opprett en tom liste som skal holde på dataene

try: 
    while True: # Kjør denne løkken helt til brukeren avslutter programmet
        data.append({
            "tidspunkt": datetime.now(),
            "temperatur": random.uniform(-10, 30),
            "luftfuktighet": random.uniform(0, 100),
            "lufttrykk": random.uniform(900, 1100),
            "partikkelkonsentrasjon": random.uniform(0, 1000)
        })
        print(data[-1]) # Skriv ut siste element i listen
        sleep(5)
except KeyboardInterrupt: # Trykk på ctrl + c for å kjøre denne delen av koden og dermed avslutte programmet
    pass

    # if input("Avslutt? (j/n): ").lower() == "j":
    #     break

# Løkken over er ferdig å kjøre, skriv data til fil
with open("data.csv", "w") as fil: # NB: w = write - og dette vil overskrive filen hvis den eksisterer fra før, bruk "a" for å legge til på slutten av filen
    fil.write("tidspunkt,temperatur,luftfuktighet,lufttrykk,partikkelkonsentrasjon\n")
    for rad in data:
        fil.write(f"{rad['tidspunkt']},{rad['temperatur']},{rad['luftfuktighet']},{rad['lufttrykk']},{rad['partikkelkonsentrasjon']}\n")