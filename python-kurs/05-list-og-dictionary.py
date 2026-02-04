# Frittståande eksempel nr. 1:
# Lister i Python
verListe = [24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
print(f"Heile lista: \n{verListe}")
print(f"Lengden på verListe = {len(verListe)}")
print(f"Det første elementet er: {verListe[0]}")
print(f"Det andre elementet er: {verListe[1]}")
print(f"Det siste elementet er: {verListe[-1]}")
print(f"Det nest siste elementet er: {verListe[-2]}")

def summerListe(liste):
    summen = 0
    for element in liste:
        # summen += element # Dette er "hurtigmåten" å skrive linjen under på
        summen = summen + element
    return summen

print(f"Summen av alle elementene i lista med eigen funksjon er: {summerListe(verListe)}")
print(f"Summen av alle elementene i lista med innebygd funksjon er: {sum(verListe)}")
print(f"Gjennomsnittet av alle elementene i lista er: {summerListe(verListe)/len(verListe)}")

# Frittståande eksempel nr. 2:
# Lister og dictionaries kan kombinerast
versamling = [
    {
        "temperatur": 24,
        "luftfuktighet": 51,
        "lufttrykk": 1003,
        "partikkelkonsentrasjon": 9
    },
    {
        "temperatur": 22,
        "luftfuktighet": 53,
        "lufttrykk": 1002,
        "partikkelkonsentrasjon": 10
    },
    {
        "temperatur": 23,
        "luftfuktighet": 55,
        "lufttrykk": 1001,
        "partikkelkonsentrasjon": 33
    }
]

print(f"Versamling med originale data: \n{versamling}")

nyeData = { 
    "temperatur": 25,
    "luftfuktighet": 50,
    "lufttrykk": 999,
    "partikkelkonsentrasjon": 7
}

versamling.append(nyeData)

print(f"Versamling etter at nye data er lagt til: \n{versamling}")
print(f"\nFinare utskrift av versamling: ")
for dag in versamling:
    print(f"Temperatur: {dag['temperatur']}, Luftfuktighet: {dag['luftfuktighet']}, Lufttrykk: {dag['lufttrykk']}, Partikkelkonsentrasjon: {dag['partikkelkonsentrasjon']}")
    # print(f"\nPartikkelkonsentrasjon: {dag['partikkelkonsentrasjon']}")

print(f"\nDet første elementet i versamling er: \n{versamling[0]}")
print(f"Temperaturen som ligg i det første elementet i lista er: \n{versamling[0]['temperatur']}")