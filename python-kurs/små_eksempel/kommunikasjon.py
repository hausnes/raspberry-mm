import time

navn = input("Kva heiter du? ")
time.sleep(1)
print("Hei, " + navn + ".")

interesse = input("Kva er du interessert i? ")

if interesse == "Telemarkski" or interesse == "telemarkski":
    print("Å, eg og likar telemark.")
    oppfolging = input("Går du topptur? ")
    if "JA" in oppfolging.upper():
        print("Me blir bestevennar.")
    else:
        print("Hald deg vekke frå meg.")
else:
    print("Usj, deg gidd eg ikkje snakke med.")

# Handterer at brukaren skriv ein kombinasjon av store og små bokstavar
if interesse.upper() == "MAT":
    print("Å, eg og likar mat.")
else:
    print("Alle likar mat.")

# Handterer at inputen INNEHELD eit visst ord
if "MAT" in interesse.upper():
    print("......Å, eg og likar mat.")
else:
    print("......Alle likar mat.")