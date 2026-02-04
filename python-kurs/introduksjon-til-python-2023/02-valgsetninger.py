from time import sleep
import os

# def prikkprikkprikk():
#     print("...")
#     sleep(0.2)
#     os.system('cls')
#     print("")
#     sleep(0.2)
#     print("...")
#     sleep(0.2)
#     os.system('cls')
#     print("")
#     sleep(0.2)

navn = input("Hva heter du? ")
print(navn.lower())

# if navn == "Jo Bjørnar" or navn == "jo bjørnar":
# if navn.lower() == "jo bjørnar":
if "jo bjørnar" in navn.lower():
    # prikkprikkprikk()
    print("Stikk av.")
else:
    # prikkprikkprikk()
    print("Deg vil jeg snakke med..")
    print("Hei, " + navn)
    print("Hallaien, ", navn)
    print(f"God dag, {navn}")

    hobby = input("Hva liker du å drive med på fritiden? ")

    if "TELEMARK" in hobby.upper():
        print("Stilig, da reiser vi på topptur sammen.")
    else:
        print("Sorry, vi har ikke noe til felles.")