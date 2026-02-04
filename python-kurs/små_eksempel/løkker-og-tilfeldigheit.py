import random

# For-løkke
for x in range(0,11): # Det same som å skrive (0,11,1) der dette betyr start, slutt og kor store hopp 
    print("Runde",x,":")
    print(random.choice(["stein","saks","papir"]))
    print(random.randint(1,10))
    
# while-løkke:
lestInnVerdi = int(input("Kva tal skal eg telle ned frå? "))
while lestInnVerdi >= 0:
    print(lestInnVerdi)
    lestInnVerdi -= 1 # NB: Forsøk gjerne å fjerne denne. Kva skjer?