# Eksempel på en løkke som går gjennom en liste med navn og skriver ut hvert navn:
navn = ["Per", "Pål", "Espen"]
for enkeltnavn in navn:
    print(enkeltnavn)

# Eksempel på en løkke som skriver ut tallene fra 1 til 10:
for tall in range(1, 11, 1):
    print(tall)

# Eksempel på en while-løkke som skriver ut et tilfeldig tall mellom 1 og 10 helt til det tilfeldige tallet er 5:
import random
tilfeldig = random.randint(1, 10)
while tilfeldig != 5:
    print(tilfeldig)
    tilfeldig = random.randint(1, 10)
print("Ferdig!")

# Skriv et program som skriver ut alle tallene fra 1 til 20 som er delelig med 3 og 5
# Løsningsforslag:
for tall in range(1, 20):
    if tall % 3 == 0 and tall % 5 == 0:
        print(tall)