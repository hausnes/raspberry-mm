import csv
from pathlib import Path

# Fila ligg i mappa over denne. Path(__file__).parent er mappa programmet ligg i,
# så programmet finn fila same kvar du køyrer det frå.
filsti = Path(__file__).parent.parent / "utestasjon-bones.csv"

data = []

with open(filsti, encoding="utf-8") as fil:
    filinnhaldet = csv.reader(fil, delimiter=",")
    overskrifter = next(filinnhaldet)  # Første rad er overskriftene
    for rad in filinnhaldet:
        data.append(rad)  # Kvar rad er ei liste med tekst, til dømes ['2022-11-15 18:59:55', '25.9', ...]

print("Overskrifter:", overskrifter)
print("Tal på rader:", len(data))
print("Første rad:", data[0])
print("Temperatur i første rad:", data[0][1])  # data[rad][kolonne]
