# Utvalt del av gangetabellen
gangeTab = int(input("Kva gangetabell vil du skrive ut? "))
for x in range(0,11,1):
    tall = gangeTab * x
    # print(str(gangeTab) + " * " + str(x) + " = " + str(tall))
    print(f"{gangeTab} * {x} = {tall}")
    
# Større del av gangetabellen
for i in range(1,11,1):
    print("Gangetabell nr. " + str(i) + ":")
    for j in range(0,11,1):
        resultat = i * j
        print(str(i) + " * " + str(j) + " = " + str(resultat))

# for tall in range(0,101):
#     print(tall*tall)