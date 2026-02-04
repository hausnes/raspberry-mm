# Bruk random.choice() til å velge et tilfeldig element fra en liste med stein, saks, papir.
# La brukeren velge stein, saks eller papir.
# Gi beskjed om brukeren vant, tapte eller det ble uavgjort.
# Utvidet oppgave: La spillet gå til best av 3, til en av spillerne har vunnet 3 ganger eller et annet suksesskriterie.

import random

antVinnSpelar = 0
antallRundar = 0
fleireRundar = "j" # Brukes for å sjekke om me skal ut av spille-loopen eller ikkje

while fleireRundar == "j": # Så lenge brukaren svarar at hen vil spele ein runde til, så..
    antallRundar += 1

    valgMaskin = random.choice(["stein","saks","papir"])
    valgBruker = input("\nSkriv inn 'stein', 'saks' eller 'papir': ")
    
    print(f"Maskin valgte {valgMaskin} og du valgte {valgBruker}")
    
    if valgMaskin == valgBruker:
        print("Uavgjort, så kjedeleg...")
    elif valgMaskin == "stein" and valgBruker == "saks":
        print("Datamaskin vinner.")
    elif valgMaskin == "papir" and valgBruker == "stein":
        print("Datamaskin vinner.")
    elif valgMaskin == "saks" and valgBruker == "papir":
        print("Datamaskin vinner.")
    else:
        print("Du vant!")
        antVinnSpelar += 1

    print("\nLyst til å spele ein runde til? (j/n):")
    fleireRundar = input("").lower()

# Spelet er ferdig. Oppsummerer:
print(f"\nSpelaren vant {antVinnSpelar} av {antallRundar} rundar.")