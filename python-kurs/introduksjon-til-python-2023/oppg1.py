# Lag et gjettespill
import random

# Lagre det tilfeldige tallet i en variabel
tilfeldig = random.randint(1,101)
# print("Det tilfeldige tallet er " + str(tilfeldig))

antGjett = 0

# Be brukeren om å gjette på et tall (mellom 1-100)
gjett = int(input("Hvilket tall gjetter du på: "))

while gjett != tilfeldig: # Vi sjekker om de er ulike
    antGjett = antGjett + 1
    if gjett > tilfeldig:
        print("Du gjettet for høyt.")
    # if gjett < tilfeldig:
    else:
        print("Du gjettet for lavt.")

    # Be brukeren om å gjette på et tall (mellom 1-100)
    gjett = int(input("Hvilket tall gjetter du på: "))

# Gi beskjed om det brukeren gjettet på er større, mindre eller likt det tilfeldige
# print("Gratulerer! Du brukte " + str(antGjett) + " forsøk.")
print(f"Gratulerer! Du brukte {antGjett} forsøk.")