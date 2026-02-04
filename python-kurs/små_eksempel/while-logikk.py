brukerHarSvartRiktig = False

while brukerHarSvartRiktig == False:
    valg = input("Skriv 'ja' for å gå videre:\n" )
    # Alternativ 1:
    '''
    if valg.upper() == "JA":
        brukerHarSvartRiktig = True
    else:
        brukerHarSvartRiktig = False
    '''
    # Alternativ 2:
    if "JA" in valg.upper():
        brukerHarSvartRiktig = True
    else:
        brukerHarSvartRiktig = False