# Del 2: CSV-filer og tolking av data

I denne delen skal du lære:

- kva ei **CSV-fil** er, og korleis vi lagrar **tidspunkt** og **måledata** i ho
- å lese, rydde, visualisere og tolke over to år med ekte måledata frå **Nordnes Sjøbad** i Bergen
- å vurdere **kor pålitelege** dataa er

Vi brukar Python med biblioteka **Pandas** (tabellar og analyse) og **Matplotlib** (grafar), i Jupyter-notatbøker (`.ipynb`) i **VS Code**.

## Innhald

| Fil | Innhald |
|---|---|
| [`01-csv-og-tidskodar.ipynb`](01-csv-og-tidskodar.ipynb) | **Start her.** Kva er CSV, ISO 8601-tidspunkt, sommartid, skrive og lese CSV med `csv`-modulen og Pandas. |
| [`02-tolke-data.ipynb`](02-tolke-data.ipynb) | Analyse av badetemperaturar i fem nivå: bli kjent, rydde, visualisere, samanfatte og djupare analyse. |
| [`oppgaver.md`](oppgaver.md) | 15 oppgåver i tre nivå + opne utforskingsoppgåver. Løysingsforslag er gøymde under kvar oppgåve. |
| `data/nordnes-sjobad.csv` | Kopi av måledata frå Nordnes Sjøbad (21. mai 2024 – 4. november 2026). |
| `requirements.txt` | Liste over Python-bibliotek som trengst. |

---

## Oppsett: Python og VS Code

Du treng tre ting: **Python**, **VS Code** og nokre **bibliotek**. Gjer stega i rekkjefølgje.

### Steg 1: Installer Python

Har du Python frå før, kan du sjekke versjonen i ein terminal: `python --version` (Windows) eller `python3 --version` (Mac). Du treng versjon 3.10 eller nyare.

**Windows**

1. Gå til <https://www.python.org/downloads/> og trykk den gule knappen **Download Python 3.x.x**.
2. Opne fila du lasta ned.
3. **Viktig:** Kryss av for **Add python.exe to PATH** nedst i det første vindauget.
4. Trykk **Install Now**. Når det er ferdig, trykk **Close**.

> Alternativt kan du installere Python frå **Microsoft Store** (søk etter «Python 3.13» e.l.). Då blir PATH ordna automatisk.

**Mac**

1. Gå til <https://www.python.org/downloads/> og trykk **Download Python 3.x.x**.
2. Opne `.pkg`-fila og følg installasjonen (*Fortset* → *Godta* → *Installer*).
3. Når installasjonen er ferdig, opnar det seg ei mappe i Finder. Dobbeltklikk på **Install Certificates.command**. Det opnar ein terminal som køyrer litt og blir ferdig av seg sjølv.
   *(Utan dette steget kan du få feilen `CERTIFICATE_VERIFY_FAILED` når du prøver å lese data frå nettet. Finn du ikkje fila, ligg ho i* Programmer → Python 3.x*.)*

### Steg 2: Installer VS Code

1. Gå til <https://code.visualstudio.com/> og last ned for ditt operativsystem.
2. **Windows:** Opne installasjonsfila, godta lisensen og trykk *Neste* til han er ferdig. Det er lurt å krysse av for *Add "Open with Code" action to Windows Explorer*.
3. **Mac:** Opne `.zip`-fila (ho blir pakka ut automatisk) og dra **Visual Studio Code** over i **Programmer**.

### Steg 3: Installer utvidingar i VS Code

1. Start VS Code.
2. Trykk på ikonet **Extensions** i menyen til venstre (fire små firkantar), eller `Ctrl + Shift + X` (Windows) / `Cmd + Shift + X` (Mac).
3. Søk etter **Python** og installer utvidinga frå **Microsoft**.
4. Søk etter **Jupyter** og installer utvidinga frå **Microsoft**.

### Steg 4: Hent filene og opne mappa

1. Last ned filene frå GitHub: Gå til forsida av repositoryet, trykk den grøne knappen **Code** → **Download ZIP**, og pakk ut ZIP-fila. (Kan du Git, kan du heller klone repositoryet.)
2. I VS Code: **File → Open Folder…** og vel mappa `mkr/2-csv-og-dataanalyse`.
3. Trykk **Yes, I trust the authors** om VS Code spør.

> Opne alltid **mappa**, ikkje berre enkeltfila. Då finn notatboka datafila i `data/`.

### Steg 5: Lag eit Python-miljø og installer bibliotek

Vi lagar eit eige *virtuelt miljø* (`.venv`) for prosjektet. Det er ei mappe med Python og bibliotek som berre høyrer til dette prosjektet.

1. Opne `01-csv-og-tidskodar.ipynb`.
2. Trykk **Select Kernel** øvst til høgre i notatboka.
3. Vel **Python Environments…** → **+ Create Python Environment** → **Venv**.
4. Vel Python-versjonen du installerte i steg 1.
5. Når VS Code spør om avhengigheiter (*dependencies*), kryss av for **requirements.txt** og trykk **OK**.
6. Vent til installasjonen er ferdig (sjå nede til høgre). Det kan ta eit par minutt.

Køyr første kodecelle med `Shift + Enter`. Fungerer det, er du klar!

<details>
<summary>Alternativ: Installer bibliotek frå terminalen</summary>

Opne ein terminal i VS Code (**Terminal → New Terminal**) og skriv:

**Windows:**

```bash
python -m pip install pandas matplotlib ipykernel pyserial
```

**Mac:**

```bash
python3 -m pip install pandas matplotlib ipykernel pyserial
```

Vel deretter denne Python-versjonen under **Select Kernel** i notatboka.

</details>

### Feilsøking

| Problem | Løysing |
|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | Notatboka brukar ein annan Python enn den du installerte biblioteka i. Trykk på kernel-namnet øvst til høgre og vel `.venv`. |
| `FileNotFoundError: data/nordnes-sjobad.csv` | Du har opna feil mappe. Bruk **File → Open Folder…** og vel `2-csv-og-dataanalyse`. |
| `'python' is not recognized` (Windows) | Python er ikkje lagt til i PATH. Installer Python på nytt og kryss av for **Add python.exe to PATH**. |
| `CERTIFICATE_VERIFY_FAILED` (Mac) | Køyr **Install Certificates.command** (sjå steg 1). |
| VS Code vil installere `ipykernel` | Trykk **Install**. Det trengst for å køyre notatbøker. |

---

## Om datasettet

Nordnes Sjøbad har ein sensor som måler sjø- og lufttemperatur. Målingane blir lagra kvar time i [hausnes/nordnes-sjobad](https://github.com/hausnes/nordnes-sjobad/blob/data/temperatur.csv).

| Kolonne | Innhald |
|---|---|
| `tid` | Tidspunkt for målinga, norsk tid (`ÅÅÅÅ-MM-DD TT:MM:SS`) |
| `temperatur` | Sjøtemperatur (°C) |
| `lufttemperatur` | Lufttemperatur (°C) |

### Ting å vere merksam på i data

Datasettet er godt eigna til å øve seg, fordi det har dei vanlegaste problema med ekte måledata:

- **Manglande verdiar er skrivne som `-`** (663 rader for sjø), og nokre gonger som `NaN`. Les ein fila utan `na_values="-"`, blir temperaturkolonnane tekst. Dette er første «aha» i notatbok 2.
- **Feilmålingar:** Fire målingar på **−50 °C** (7. juli 2025) og 28 målingar på **nøyaktig 0,0 °C** midt i hetebølgja i juli 2025. Dei trekkjer snittet for juli 2025 ned frå 20,0 °C til 18,3 °C.
- **Duplikat:** Fem rader har same tidspunkt som ei anna rad. Ein av dei kjem av overgangen til vintertid 26. oktober 2025.
- **Sommartid:** Kl. 02:00 manglar 30. mars 2025 og finst to gonger 26. oktober 2025.
- **Hol:** Eit hol på 14 dagar i august 2025 (berre ca. 290 av 744 timar har data).
- **Ujamn start:** Første døgnet (21.–22. mai 2024) har ujamne intervall, og luftsensoren starta først 22. mai 2024.
- **Brå hopp:** 21. november 2025 hoppar sjøtemperaturen fram og tilbake med opptil 4,6 °C per time (oppgåve 13).
- **Høge lufttemperaturar:** Over 30 °C i mai 2024 og juli 2025. Kan tyde på direkte sol på luftsensoren, og kan samanliknast med data frå met.no.

---

**Førre del:** [Del 1: Set opp Arduino og mål temperatur](../1-oppsett-og-maling/)
**Neste del:** [Del 3: Logg eigne målingar til CSV](../3-logging-til-csv/)
