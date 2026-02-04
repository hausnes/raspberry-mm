# Bruk random.choice() til å velge et tilfeldig element fra en liste med stein, saks, papir.
# La brukeren velge stein, saks eller papir.
# Gi beskjed om brukeren vant, tapte eller det ble uavgjort.
# Utvidet oppgave: La spillet gå til best av 3, til en av spillerne har vunnet 3 ganger eller et annet suksesskriterie.

import random

valg = ["stein", "saks", "papir"]
# print(random.choice(valg)) # Test for å sjekke om random.choice virker

maskinvalg = random.choice(valg)
brukervalg = input("stein, saks eller papir? \n")

if brukervalg == "stein" and maskinvalg == "saks":
    print("Du vant.")
elif brukervalg == "saks" and maskinvalg == "papir":
    print("Du vant.")
elif brukervalg == "papir" and maskinvalg == "stein":
    print("Du vant.")
elif brukervalg == maskinvalg:
    print("Uavgjort.")
else:
    print(f"Du tapte.")

print(f"Du valgte {brukervalg} og maskinen valgte {maskinvalg}")