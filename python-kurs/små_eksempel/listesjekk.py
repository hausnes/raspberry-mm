def finnOrd(setning):
        funne = 0
        setning = setning.lower()
        for ord in listeInteresser:
            if ord in setning:
                funne += 1

        if funne>0:
            return True
        else:
            return False

listeInteresser = ["ski","telemark","helg","tof","epler"]

# Hovuddelen av programmet
interesse = "tof" # Latar som om dette er input frå brukar
if finnOrd(interesse):
    print("Ja, eg og likar", interesse.lower())
else:
    print("Eg er ikkje interessert i å snakke med deg.")