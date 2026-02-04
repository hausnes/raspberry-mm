# Dette er den krypterte meldinga, som me skal forsøke å "knekke"
hemmeleg_melding = "xå pxmcøoc sc gscrsød døwzzodes åu psdes zlcoc åu gsøø, oddo." 

alphabet = "abcdefghijklmnopqrstuvwxyzæøå" # Me tek utgangspunkt i denne når me skal gjere forskyvinga
output = "" # Lagrar dei krypterte meldingane i denne

# Funksjon som dekrypterer ein bokstav, eller meir korrekt gjer ein forskyvning.
def decode(letter, secret):
    pos = alphabet.find(letter) # Kva posisjon har bokstaven i "alphabet", returnerer eit nummer
    newpos = (pos - secret) # Tek utg.pkt. i posisjonen bokstaven hadde, og forskyver lik mengde som "secret" (= grad av forskyvning)
    if newpos < 0: # Handterer dersom me kjem "utanfor" alfabetet, må då begynne på slutten. Altså, hoppar du eit hakk til venstre for a skal du ende opp på å.
        newpos = newpos + 29
    return alphabet[newpos] # returnerer den nye posisjonen

# Løkke som forsøker å dekryptere på like mange ulike måtar som det er teikn i "alphabet".
for j in range(1, len(alphabet), 1):
    print("Forskyvning: " + str(j))
    output = ""
    for character in hemmeleg_melding: # Løkke som går gjennom den hemmelege meldinga
        if character in alphabet: # Dersom teiknet me ser på ligg i "alphabet", dvs. den kuttar ut å dekryptere .-;, osv.
            tmp = decode(character,j) # Kallar på funksjonen "decode" for å gjennomføre sjølve forskyvinga
            output = output + tmp # Legg til den dekrypterte bokstaven me får frå funksjonen "decode" til output-stringen
        else: # Handterer spesialteikn, som ,. osv., altså: ikkje i "alphabet" - desse blir som før
            output = output + character
    print(output)
