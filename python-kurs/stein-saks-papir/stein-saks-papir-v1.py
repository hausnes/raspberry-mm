# Bruk random.choice() til å velge et tilfeldig element fra en liste med stein, saks, papir.
# La brukeren velge stein, saks eller papir.
# Gi beskjed om brukeren vant, tapte eller det ble uavgjort.
# Utvidet oppgave: La spillet gå til best av 3, til en av spillerne har vunnet 3 ganger eller et annet suksesskriterie.

import random

valgMaskin = random.choice(["stein","saks","papir"])
valgBruker = input("Skriv inn 'stein', 'saks' eller 'papir': ")

print(f"Maskin valgte {valgMaskin} og du valgte {valgBruker}.")

if valgMaskin == valgBruker:
    print("Uavgjort.")
elif valgMaskin == "stein" and valgBruker == "saks":
    print("Datamaskin vinner.")
elif valgMaskin == "papir" and valgBruker == "stein":
    print("Datamaskin vinner.")
elif valgMaskin == "saks" and valgBruker == "papir":
    print("Datamaskin vinner.")
else:
    print("Du vant!")