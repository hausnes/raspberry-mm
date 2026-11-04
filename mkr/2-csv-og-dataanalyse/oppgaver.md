# Oppgåver: Tolke data frå Nordnes Sjøbad

Lag ei ny notatbok (t.d. `mine-oppgaver.ipynb`) i same mappe som `data/`. Start med denne cella, som les og ryddar dataa på same måte som i [02-tolke-data.ipynb](02-tolke-data.ipynb):

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv("data/nordnes-sjobad.csv", na_values="-", parse_dates=["tid"], index_col="tid")

# Rydding: fjern duplikat og feilmålingar
data = data[~data.index.duplicated(keep="first")]
feil = (data["temperatur"] < -2) | (data.index.month.isin([6, 7, 8, 9]) & (data["temperatur"] < 5))
data.loc[feil, "temperatur"] = np.nan
```

Alle løysingsforslaga går ut frå at du har køyrt denne cella. Prøv sjølv før du opnar løysinga! Det finst ofte fleire rette måtar å løyse ei oppgåve på.

---

## Nivå 1: Grunnleggande

### Oppgåve 1: Kor stor er fila?

Skriv ut kor mange rader og kolonnar `data` har, og kva kolonnane heiter.

<details>
<summary>Løysingsforslag</summary>

```python
print("Rader:", len(data))
print("Kolonnar:", len(data.columns))
print("Kolonnenamn:", list(data.columns))

# Alternativt: data.shape gir (rader, kolonnar)
print(data.shape)
```

Merk at `tid` ikkje er ein kolonne lenger. Han er blitt *indeks*.

</details>

### Oppgåve 2: Badetemperatur på 17. mai

Kva var sjøtemperaturen og lufttemperaturen 17. mai 2025 klokka 12?

<details>
<summary>Løysingsforslag</summary>

```python
data.loc["2025-05-17 12"]
```

Fordi vi berre skriv timen, får vi alle målingar i timen 12:00–12:59. Vil du sjå heile dagen, skriv du `data.loc["2025-05-17"]`.

</details>

### Oppgåve 3: Gjennomsnitt

a) Kva var gjennomsnittleg sjøtemperatur for heile perioden?
b) Kva var gjennomsnittleg sjøtemperatur i 2025?
c) Kvifor er det ikkje rett å seie at svaret i a) er «gjennomsnittstemperaturen i sjøen på Nordnes»?

<details>
<summary>Løysingsforslag</summary>

```python
print("Heile perioden:", round(data["temperatur"].mean(), 1), "°C")
print("2025:", round(data.loc["2025", "temperatur"].mean(), 1), "°C")
```

c) Perioden startar i mai 2024 og sluttar i november 2026. Det er altså med *tre* somrar, men berre *to* vintrar. Gjennomsnittet blir derfor dregne opp. 2025 er det einaste heile året. I tillegg manglar det data i delar av perioden (t.d. august 2025).

</details>

### Oppgåve 4: Kaldast i sjøen

Når var sjøen kaldast, og kor kald var han? Hadde du fått same svar før ryddinga?

<details>
<summary>Løysingsforslag</summary>

```python
print(data["temperatur"].min(), "°C, den", data["temperatur"].idxmin())
```

Svaret er −0,1 °C den 5. januar 2025. Før ryddinga ville vi fått −50 °C, som var ein sensorfeil.

</details>

### Oppgåve 5: Desember

Lag ein graf som viser sjøtemperaturen og lufttemperaturen i desember 2025. Hugs tittel, aksetekst og forklaring (*legend*).

<details>
<summary>Løysingsforslag</summary>

```python
desember = data.loc["2025-12"]

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(desember.index, desember["lufttemperatur"], label="Luft", color="tab:orange")
ax.plot(desember.index, desember["temperatur"], label="Sjø", color="tab:blue")
ax.set_title("Desember 2025")
ax.set_ylabel("Temperatur (°C)")
ax.legend()
ax.grid(alpha=0.3)
plt.show()
```

Ein kortare variant: `data.loc["2025-12"].plot(title="Desember 2025", ylabel="°C")`

</details>

---

## Nivå 2: Middels

### Oppgåve 6: Kuldegrader

a) Kor mange timar var lufta under 0 °C?
b) I kva månader skjedde det?

<details>
<summary>Løysingsforslag</summary>

```python
kulde = data[data["lufttemperatur"] < 0]
print("Timar med kuldegrader:", len(kulde))

# Tel kor mange timar i kvar månad (år og månad)
kulde.groupby([kulde.index.year, kulde.index.month]).size()
```

</details>

### Oppgåve 7: Største døgnvariasjon

Kva dag i 2025 var det størst skilnad mellom høgaste og lågaste lufttemperatur i løpet av døgnet? Kor stor var skilnaden?

<details>
<summary>Løysingsforslag</summary>

```python
luft_2025 = data.loc["2025", "lufttemperatur"]
dogn_maks = luft_2025.resample("D").max()
dogn_min = luft_2025.resample("D").min()
variasjon = dogn_maks - dogn_min

print("Dag:", variasjon.idxmax().date())
print("Skilnad:", round(variasjon.max(), 1), "°C")
```

Tips: Sjå på dagen med `data.loc["ÅÅÅÅ-MM-DD"].plot()`, der du set inn datoen du fann. Kva trur du skjedde? Sjekk gjerne vêret same dag på <https://seklima.met.no>.

</details>

### Oppgåve 8: Sjøen varmare enn lufta

I kor mange prosent av timane var sjøen varmare enn lufta?

<details>
<summary>Løysingsforslag</summary>

```python
begge = data.dropna()   # berre rader der vi har begge målingane
varmare = begge["temperatur"] > begge["lufttemperatur"]
prosent = varmare.sum() / len(begge) * 100
print(f"Sjøen var varmare enn lufta {prosent:.0f} % av timane")
```

Når vi summerer `True`/`False`, tel `True` som 1 og `False` som 0. Derfor gir `varmare.sum()` talet på timar der sjøen var varmast.

Eit kortare alternativ: `varmare.mean() * 100`.

</details>

### Oppgåve 9: Sommaren kjem

Finn den første dagen kvart år då **døgnsnittet** i sjøen var minst 15 °C.

<details>
<summary>Løysingsforslag</summary>

```python
dogn = data["temperatur"].resample("D").mean()
varme_dagar = dogn[dogn >= 15]

# Første varme dag i kvart år
for ar in [2024, 2025, 2026]:
    print(ar, varme_dagar.loc[str(ar)].index.min().date())
```

Alternativ med `groupby`:

```python
varme_dagar.groupby(varme_dagar.index.year).apply(lambda x: x.index.min().date())
```

Merk: For 2024 er svaret den første dagen med målingar, fordi sjøen allereie var over 15 °C då målingane starta.

</details>

### Oppgåve 10: To histogram

Lag eit histogram for sjøtemperaturen og eit for lufttemperaturen i same figur. Kva fortel figuren om skilnaden mellom luft og sjø?

<details>
<summary>Løysingsforslag</summary>

```python
fig, ax = plt.subplots(figsize=(10, 4))
botter = range(-9, 32)
ax.hist(data["lufttemperatur"], bins=botter, alpha=0.6, label="Luft", color="tab:orange")
ax.hist(data["temperatur"], bins=botter, alpha=0.6, label="Sjø", color="tab:blue")
ax.set_title("Fordeling av temperaturar")
ax.set_xlabel("Temperatur (°C)")
ax.set_ylabel("Tal på timar")
ax.legend()
plt.show()
```

`alpha=0.6` gjer stolpane delvis gjennomsiktige, slik at vi ser begge. Lufta har ei mykje breiare fordeling: ho blir både kaldare og varmare enn sjøen. Sjøtemperaturen er meir «samla».

</details>

### Oppgåve 11: Vekesnitt

Rekn ut gjennomsnittleg sjøtemperatur for kvar veke i 2026, og vis det som ein graf. Kva veke var varmast?

<details>
<summary>Løysingsforslag</summary>

```python
veke = data.loc["2026", "temperatur"].resample("W").mean()

ax = veke.plot(marker="o", title="Vekesnitt, sjøtemperatur 2026", ylabel="°C")
plt.show()

print("Varmaste veke slutta", veke.idxmax().date(), "med", round(veke.max(), 1), "°C")
```

`resample("W")` lagar veker som sluttar på sundag. Datoen i indeksen er derfor siste dag i veka.

</details>

---

## Nivå 3: Avansert

### Oppgåve 12: Sommardøgn og vinterdøgn

Lag ein figur som viser den gjennomsnittlege lufttemperaturen gjennom døgnet (time for time) for **sommar** (juni–august) og **vinter** (desember–februar). Kva er skilnaden på døgnvariasjonen?

<details>
<summary>Løysingsforslag</summary>

```python
sommar = data[data.index.month.isin([6, 7, 8])]
vinter = data[data.index.month.isin([12, 1, 2])]

sommar_time = sommar.groupby(sommar.index.hour)["lufttemperatur"].mean()
vinter_time = vinter.groupby(vinter.index.hour)["lufttemperatur"].mean()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(sommar_time.index, sommar_time, marker="o", label="Sommar (jun–aug)", color="tab:orange")
ax.plot(vinter_time.index, vinter_time, marker="o", label="Vinter (des–feb)", color="tab:blue")
ax.set_title("Lufttemperatur gjennom døgnet")
ax.set_xlabel("Klokkeslett (time)")
ax.set_ylabel("Temperatur (°C)")
ax.set_xticks(range(0, 24, 2))
ax.legend()
ax.grid(alpha=0.3)
plt.show()

print("Døgnvariasjon sommar:", round(sommar_time.max() - sommar_time.min(), 1), "°C")
print("Døgnvariasjon vinter:", round(vinter_time.max() - vinter_time.min(), 1), "°C")
```

Om sommaren er døgnvariasjonen mykje større. Sola står høgt og lenge på himmelen og varmar mykje på dagtid. Om vinteren er det lite sol i Bergen, og temperaturen blir meir styrt av kva luft som kjem inn frå havet.

</details>

### Oppgåve 13: Brå endringar

a) Finn dei fem største endringane i sjøtemperatur frå éi måling til den neste (etter rydding).
b) Sjå nærare på den største. Teikn ein graf av døgnet det skjedde. Trur du endringa er ekte, eller er det ein målefeil? Grunngi svaret.

<details>
<summary>Løysingsforslag</summary>

```python
endring = data["temperatur"].diff()
endring.abs().sort_values(ascending=False).head(5)
```

Den største er 21. november 2025, med rundt 4,6 °C endring på éin time.

```python
data.loc["2025-11-20":"2025-11-22"].plot(title="20.–22. november 2025", ylabel="°C", marker=".")
plt.show()
```

Grafen viser at sjøtemperaturen hoppar fram og tilbake mellom ca. 3,5 °C og 8,5 °C fleire gonger i løpet av nokre timar, medan lufta held seg rundt 0 °C.

Her finst det ikkje eitt fasitsvar. Moglege forklaringar:

- **Ekte:** Etter kalde dagar med nedbør kan det liggje eit tynt lag med kaldt (ferskare) vatn på overflata, over varmare sjøvatn. Bølgjer og tidevatn kan flytte sensoren opp og ned mellom laga.
- **Målefeil:** Sensoren kan ha hatt dårleg kontakt eller vore delvis over vatn. Men sjøtemperaturen er heile tida mykje høgare enn lufttemperaturen, så sensoren har neppe berre målt lufta.

Det at verdiane hoppar så mykje att og fram, er uvanleg for sjøtemperatur, som elles endrar seg roleg. Korleis kunne du funne ut meir? Sjå på tidevatnet (<https://www.kartverket.no/til-sjos/se-havniva>) og vêret (<https://seklima.met.no>) same døgn, og spør gjerne dei som driv sjøbadet kvar sensoren heng.

</details>

### Oppgåve 14: Ein eigen ryddefunksjon

Lag ein funksjon `les_og_rydd(filnamn)` som les ei CSV-fil, fjernar duplikat og feilmålingar, og returnerer ein ferdig rydda DataFrame. Funksjonen skal òg skrive ut kor mange rader som vart endra. Du får bruk for ein slik funksjon i del 3!

<details>
<summary>Løysingsforslag</summary>

```python
def les_og_rydd(filnamn):
    data = pd.read_csv(filnamn, na_values="-", parse_dates=["tid"], index_col="tid")

    for_duplikat = len(data)
    data = data[~data.index.duplicated(keep="first")]
    print("Fjerna duplikat:", for_duplikat - len(data))

    umogleg = data["temperatur"] < -2
    urealistisk = data.index.month.isin([6, 7, 8, 9]) & (data["temperatur"] < 5)
    feil = umogleg | urealistisk
    data.loc[feil, "temperatur"] = np.nan
    print("Feilmålingar sette til NaN:", feil.sum())

    return data


rydda = les_og_rydd("data/nordnes-sjobad.csv")
rydda.describe().round(1)
```

</details>

### Oppgåve 15: Ferske data

Les dei nyaste dataa direkte frå nettet:

```python
url = "https://raw.githubusercontent.com/hausnes/nordnes-sjobad/data/temperatur.csv"
```

a) Når var den siste målinga, og kva var temperaturane då?
b) Rekn ut gjennomsnittet for dei siste 7 døgna, og samanlikn med same veke i fjor.

<details>
<summary>Løysingsforslag</summary>

```python
url = "https://raw.githubusercontent.com/hausnes/nordnes-sjobad/data/temperatur.csv"
ferske = pd.read_csv(url, na_values="-", parse_dates=["tid"], index_col="tid")

print("Siste måling:")
print(ferske.tail(1))

slutt = ferske.index.max()
start = slutt - pd.Timedelta(days=7)
print("Siste 7 døgn:")
print(ferske.loc[start:slutt].mean().round(1))

# Same periode eitt år tidlegare
start_ifjor = start - pd.DateOffset(years=1)
slutt_ifjor = slutt - pd.DateOffset(years=1)
print("Same veke i fjor:")
print(ferske.loc[start_ifjor:slutt_ifjor].mean().round(1))
```

Hugs å rydde dataa òg her, t.d. med funksjonen frå oppgåve 14.

</details>

---

## Utforsk sjølv

Desse oppgåvene har ikkje eitt rett svar. Skriv ned kva du gjorde, kva du fann, og kor sikker du er på svaret.

1. **Eige spørsmål:** Formuler eit spørsmål du lurer på om badetemperaturen på Nordnes, og prøv å svare på det med dataa. Døme: *Kva er den beste tida på døgnet for å bade?* eller *Kor mange dagar i året er sjøen under 5 °C?*
2. **Er det kaldare i helgane?** Grupper dataa på vekedag (`data.index.dayofweek`, der 0 er måndag). Finn du ein skilnad? Er det ein *ekte* samanheng? Kva lærer dette oss om korrelasjon og årsak?
3. **Samanlikn med offisielle data:** Last ned lufttemperatur for Bergen (Florida) frå <https://seklima.met.no> for same periode. Les fila inn med Pandas og samanlikn med lufttemperaturen frå Nordnes. Er luftsensoren på Nordnes påverka av sola?
4. **Presenter funn:** Vel tre funn frå dataa som du synest er interessante. Lag éin god figur for kvart funn, og skriv to–tre setningar om kva figuren viser og kor sikker du er på tolkinga.
