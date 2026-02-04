import random

antStein = 0
antSaks = 0
antPapir = 0

for i in range(1,100000,1):
    ord = random.choice(["stein","saks","papir"])
    if ord == "stein":
        antStein = antStein + 1
    if ord == "saks":
        antSaks = antSaks + 1
    if ord == "papir":
        antPapir = antPapir + 1

print("Stein: " + str(antStein))
print("Saks: " + str(antSaks))
print("Papir: " + str(antPapir))