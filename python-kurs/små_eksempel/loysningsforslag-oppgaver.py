# 1.2
tallEin = 5
tallTo = 10
resultat = tallEin * tallTo
print(tallEin,"ganger",tallTo,"er",resultat)

# 1.2: Meir avansert løysing
tallInnlest1 = int(input("Tall 1: "))
tallInnlest2 = int(input("Tall 2: "))
resultat = tallInnlest1 * tallInnlest2
print(tallInnlest1,"ganger",tallInnlest2,"er",resultat)

# 1.3: Be gjerne om input frå brukaren, slik at det blir generert ei e-postadresse
fornavn = "jo"
mellomnavn = "bjornar"
etternavn = "hausnes"
domene = "gmail.com"
epost = fornavn + "." + mellomnavn + "." + etternavn + "@" + domene
print(epost)

# 1.3: Alternativ 2, variant
navn = "Jo Bjornar"
print(navn.lower()) # Denne gjer alt i 'navn' om til små bokstavar
print(navn.lower().replace(" ","")) # Denne fjernar mellomrom i navn, i tillegg til å gjere om til små bokstavar

# 1.5
gate = "Kongens Gate"
husnr = 432
oppgang = "b"
adresse = gate + " " + str(husnr) + oppgang
print(adresse)
print("Adressen er",gate,husnr,oppgang)
print("Gaten er " + gate + ", husnummeret er " + str(husnr) + ", oppgang " + oppgang + ".")

# 1.6
prisMatDrikke = 850
studentRabatt = 0.25
tips = 0.10
sumMiddag = prisMatDrikke + (prisMatDrikke * tips) - (prisMatDrikke * studentRabatt)
print("Middagen, inkl. drikke, kostar:",sumMiddag,"kroner.")

antPersoner = int(input("Kor mange personar skal dele på rekninga? "))
prisPerPerson = sumMiddag / antPersoner
print("Kvar person i ditt følge på",antPersoner,"personar, skal betale:",round(prisPerPerson,2),"kroner.")

# 2.1 ("Gjettespel")
import random

hemmeligTall = random.randint(0,100) # Hent et tilfeldig tall

gjettet = 0 # Initier variabelen for gjettet tall
antGjett = 0 # Initier counter for antall forsøk

while gjettet != hemmeligTall:
    
    gjettet = int(input('Gjett det hemmelige tallet (1-100): ')) # Ta inn et gjett fra bruker
    antGjett += 1 # Øk antall forsøk med 1 for hver runde
    
    ### Skriv din kode under denne linjen ###
    if gjettet>hemmeligTall:
        print('Du gjetta for høgt. Forsøk igjen.')
    else:
        print('Du gjetta for lågt. Forsøk igjen.')
    
    ### Skriv din kode over denne linjen ###

print('Du gjettet riktig! Det hemmelige tallet var', hemmeligTall, '. Du brukte', antGjett, 'forsøk.')

# 2.2 (Krav til input innan to gitte intervall)
print("Gi a og b, begge heltall i intervall <40,50> eller <70,90>:" )
a = int(input("Verdi for a: "))
b = int(input("Verdi for b: "))
  
if ((a >= 70 and a <= 90) or (a >= 40 and a <= 50)) and ((b >= 70 and b <= 90) or (b >= 40 and b <= 50)):
    print("Tallene er begge innenfor gyldige intervall.")
else:
    print("Minst ett av tallene er utenfor et gyldig intervall.")

# 2.3 (Reiser)
rute1_by_sjo = 150
rute2_sjo_fjell = 250
rute3_fjell_by = 50

alder = int(input("Kor gamal er du? "))
rabattGitt = 1 # Det me gangar med, 1 gjer ingen rabatt, 0 gjer gratisbillett
if alder >= 0 and alder <= 2:
    rabattGitt = 0
elif alder > 2 and alder <= 16:
    rabattGitt = 0.5
elif alder >= 65:
    rabattGitt = 0.3
else:
    rabattGitt = 1

print("Din alder:",alder,", med rabattkode:",rabattGitt," (0 = ingen betaling, 0.5 = 50%, 1 = ingen rabatt")

endelegPris = 0
reiseRute = int(input("Spesifiser med eit tal kva type reise du ynskjer:\n1: By - Sjø\n2: Sjø - Fjell\n3: Fjell - By\n"))
if reiseRute == 1:
    endelegPris = rute1_by_sjo * rabattGitt
    print("Standardpris:",rute1_by_sjo,", din pris:",endelegPris)
elif reiseRute == 2:
    endelegPris = rute2_sjo_fjell * rabattGitt
    print("Standardpris:",rute2_sjo_fjell,", din pris:",endelegPris)
elif reiseRute == 3:
    endelegPris = rute3_fjell_by * rabattGitt
    print("Standardpris:",rute3_fjell_by,", din pris:",endelegPris)
else:
    print("Feil i input, du må skrive eit tal mellom 1-3. Utrekninga kunne ikkje bli gjennomført.")

print("Endeleg pris for deg med alder",alder,"og rutevalg",reiseRute,"er",endelegPris)

# 2.4 (Partall eller ei)
antPar = 0 # Initierer antall partall-counter
forsok = 0 # Initierer counter for antall forsøk
ny = 'J' # Initierer kontrollstruktur for ny input

while ny.upper() == 'J':
    
    tall = int(input('Skriv et tall mellom 1-1000:' )) # Ta inn et tall fra bruker
    forsok += 1
    ### Skriv din kode under denne linjen ###
    if (tall%2) == 1: # %2 gjer enten ein rest på 1 for oddetall, eller ikkje
        print("Oddetall")
    else:
        print("Partall")
        antPar += 1
    
    ### Skriv din kode over denne linjen ###
        
    ny = str(input('Vil du skrive inn et nytt tall? (J/N): ')) # Sjekker om programmet skal avsluttes eller startes på nytt
    
print('Du skrev inn ', forsok, 'tall, og', antPar, 'av dem var partall.') # Beskjed til bruker om antall forsøk og antall partall

# 2.5 (Stein, saks, papir. Sjå eigne filer. Filene heiter stein-saks-papir-v1 og -v2. )