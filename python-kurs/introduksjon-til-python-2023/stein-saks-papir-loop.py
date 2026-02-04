# Bruk random.choice() til å velge et tilfeldig element fra en liste med stein, saks, papir.
# La brukeren velge stein, saks eller papir.
# Gi beskjed om brukeren vant, tapte eller det ble uavgjort.
# Utvidet oppgave: La spillet gå til best av 3, til en av spillerne har vunnet 3 ganger eller et annet suksesskriterie.

import random

antRunder = 1
poengsumSpiller = 0
poengsumMaskin = 0

valg = ["stein", "saks", "papir"]
# print(random.choice(valg)) # Test for å sjekke om random.choice virker

print(f"Runde {antRunder}:")
maskinvalg = random.choice(valg)
brukervalg = input("stein, saks eller papir? \n")

while antRunder < 3:
    if brukervalg == "stein" and maskinvalg == "saks":
        print("Du vant.")
        poengsumSpiller = poengsumSpiller + 1
    elif brukervalg == "saks" and maskinvalg == "papir":
        print("Du vant.")
        poengsumSpiller = poengsumSpiller + 1
    elif brukervalg == "papir" and maskinvalg == "stein":
        print("Du vant.")
        poengsumSpiller = poengsumSpiller + 1
    elif brukervalg == maskinvalg:
        print("Uavgjort.")
    else:
        print(f"Du tapte.")
        poengsumMaskin = poengsumMaskin + 1

    print(f"Du valgte {brukervalg} og maskinen valgte {maskinvalg}")

    antRunder = antRunder + 1
    
    print(f"\nRunde {antRunder}:")
    maskinvalg = random.choice(valg)
    brukervalg = input("stein, saks eller papir? \n")

print(f"\nTotal score:\n Spiller: {poengsumSpiller} \n Maskin: {poengsumMaskin}")