# NB: Dette eksempelet er ikkje ferdig.

def regnUt(): 
    try:
        global tall1
        tall1 = int(input("Tall 1: "))
    except ValueError:
        print("Feil input, du må skrive inn eit tal.")
        regnUt()
    
    try:
        global tall2
        tall2 = int(input("Tall 2: "))
    except ValueError:
        print("Feil input, du må skrive inn eit tal.")
        regnUt()

    summen = tall1 + tall2
    print(summen)

regnUt()