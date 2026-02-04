# https://lawsie.github.io/guizero/textbox/

from guizero import App, Text, PushButton, TextBox
import random

tilfeldigTal = random.randint(1,101)
antallForsok = 0

def riktigSvar():
    app.bg = "green"
    innlestTal.bg = "white"
    startBeskjed.bg = "white"
    button.bg = "white"

def feilSvar():
    app.bg = "red"
    innlestTal.bg = "white"
    startBeskjed.bg = "white"
    button.bg = "white"

def gjett():
    gjettaTal = int(innlestTal.value)
    global antallForsok
    antallForsok += 1
    if gjettaTal < tilfeldigTal:
        resultat.value = "Du gjetta for lågt."
        feilSvar()
    elif gjettaTal > tilfeldigTal:
        resultat.value = "Du gjetta for høgt."
        feilSvar()
    elif gjettaTal == tilfeldigTal:
        resultat.value = "Riktig!"
        riktigSvar()
    else:
        resultat.value = "Du gjetta: " + str(gjettaTal) + ", men dette var feil."

    resultat.value += "\nDu har brukt " + str(antallForsok) + " forsøk."

'''
def startPaaNytt():
    global tilfeldigTal = random.randint(1,101)
    innlestTal.bg = "white"
    startBeskjed.bg = "white"
    button.bg = "white"
    resultat._text = ""
'''

# Set opp GUI-en (brukergrensesnittet)
app = App(title="Gjettespel")
startBeskjed = Text(app, text="Gjett på eit tal mellom 1-100!")
innlestTal = TextBox(app, width="fill")
innlestTal.focus()
button = PushButton(app, text="Gjett!", command=gjett)
resultat = Text(app, text="")
resultat.text_size = 34
# button = PushButton(app, text="Start på ny!", command=startPaaNytt)

innlestTal.bg = "white"
startBeskjed.bg = "white"
button.bg = "white"

app.display()