# Eksempel på en funksjon som tar inn to tall som argument og returnerer summen av disse:
def addisjon(tall1, tall2):
    return tall1 + tall2

print(addisjon(1, 2))
print(addisjon(3, 4))

resultatet = addisjon(5, 6)
print(resultatet)

# Skriv kode selv for subtraksjon, multiplikasjon og divisjon
def subtraksjon(tall1, tall2):
    return tall1 - tall2

print(subtraksjon(1, 2))

def multiplikasjon(tall1, tall2):
    return tall1 * tall2

print(multiplikasjon(1, 2))

def divisjon(tall1, tall2):
    return tall1 / tall2

def siHei(innlestNavn):
    print(f"Hei {innlestNavn}!")

# print(siHei("Jo Bjørnar"))

navn = input("Hva heter du?")
siHei(navn)

# Skriv en funksjon som tar inn en liste som argument og summerer alle tallene i listen

# Løsningsforslag:
def summer(listeFraBruker):
    summen = 0
    for tall in listeFraBruker:
        summen += tall
    return summen

liste = [1, 2, 3, 4, 5]
print(summer(liste))

print(sum(liste))