# Del 3: Logg eigne målingar til CSV

No skal vi kombinere del 1 og del 2: Temperatursensoren skal måle over tid, og målingane skal lagrast i ei CSV-fil som du kan analysere med Pandas.

## Kan Arduinoen skrive ei CSV-fil direkte?

**Nei, ikkje til datamaskina.** Arduinoen har ikkje noko filsystem, og kan ikkje skrive filer på harddisken til PC-en. Det einaste han gjer når han er kopla til med USB, er å sende **tekst** over ein seriellport (det same som du ser i Serial Monitor). Noko på den andre sida må ta imot teksten og lagre han.

Vi har tre måtar å løyse dette på:

| | Spor A: Seriell → Python | Spor B: SD-kort | Spor C: Mobilnett |
|---|---|---|---|
| **Korleis** | Arduinoen sender tal over USB. Eit Python-skript på PC-en tek imot og skriv CSV-fila. | Arduinoen skriv sjølv CSV-fila til eit minnekort på eit **MKR MEM Shield**. | MKR NB 1500 sender målingane over mobilnettet (NB-IoT) til ei teneste på nettet. |
| **Ekstra utstyr** | Ingen | MKR MEM Shield + microSD-kort | SIM-kort med NB-IoT-abonnement + antenne |
| **Tidspunkt** | Frå klokka på PC-en (enkelt) | Arduinoen har inga ekte klokke. Vi lagrar sekund sidan start. | Kan hentast frå mobilnettet |
| **Treng PC heile tida?** | Ja | Nei, går på batteri | Nei |
| **Eigna til** | Forsøk i klasserommet | Målingar ute, i kjøleskap, over fleire døgn | Vidare prosjekt (ikkje med her) |

**Spor A er hovudsporet.** Spor B er ei utviding for dei som har MEM Shield.

> **Naudløysing utan Python:** I Arduino IDE kan du kopiere teksten frå Serial Monitor og lime han inn i ei tekstfil. Det fungerer for korte forsøk, men er tungvint og lett å gjere feil med.

---

## Spor A: Seriell → Python

```text
┌──────────────┐   USB-kabel    ┌─────────────────────┐        ┌────────────────┐
│   Arduino    │ ─────────────▶ │  logg_til_csv.py    │ ─────▶ │ maalingar.csv  │
│  "21.44"     │   tekst        │  legg til tidspunkt │        │ tid,temperatur │
└──────────────┘                └─────────────────────┘        └────────────────┘
```

### Steg 1: Last opp Arduino-koden

Koplinga er den same som i [del 1](../1-oppsett-og-maling/).

1. Opne [`arduino/01-csv-over-seriell/01-csv-over-seriell.ino`](arduino/01-csv-over-seriell/01-csv-over-seriell.ino) i Arduino IDE.
2. Endre gjerne `INTERVALL_MS` (kor ofte det blir målt). Standard er kvart 5. sekund.
3. Trykk **Upload**.
4. Opne Serial Monitor og sjekk at det kjem tal, t.d. `21.44`.
5. **Lukk Serial Monitor.** Berre eitt program kan bruke porten om gongen, og no skal Python ta over.

Legg merke til at Arduinoen berre sender **talet**, ikkje tidspunktet. Det er Python-skriptet som legg til tidspunktet, fordi PC-en har ei klokke som er rett.

### Steg 2: Set opp Python i VS Code

1. Opne mappa `mkr/3-logging-til-csv` i VS Code (**File → Open Folder…**).
2. Lag eit virtuelt miljø med biblioteka i `requirements.txt` på same måte som i [del 2](../2-csv-og-dataanalyse/#steg-5-lag-eit-python-miljø-og-installer-bibliotek): opne `analyser-eigne-data.ipynb`, trykk **Select Kernel → Python Environments… → Create Python Environment → Venv**, og kryss av for `requirements.txt`.

   Den viktigaste nye pakken er **pyserial**, som lèt Python lese frå seriellporten.

### Steg 3: Start loggen

1. Opne [`python/logg_til_csv.py`](python/logg_til_csv.py).
2. Sjekk at Python-versjonen nede til høgre i VS Code er `.venv`. Er han ikkje det, trykk på han og vel `.venv`.
3. Trykk ▷ (**Run Python File**) øvst til høgre.
4. I terminalen nedst skal du sjå:

   ```text
   Loggar frå /dev/cu.usbmodem1101 til maalingar.csv. Stopp med Ctrl + C.
   2026-11-10 09:15:03 ['21.44']
   2026-11-10 09:15:08 ['21.50']
   ```

5. Gjennomfør forsøket ditt.
6. Stopp loggen ved å klikke i terminalen og trykke `Ctrl + C`.

Fila `maalingar.csv` ligg no i mappa `3-logging-til-csv`. Opne ho i VS Code og sjå på innhaldet. Startar du skriptet på nytt, blir nye målingar lagt til **på slutten** av same fil. Vil du starte på nytt, endrar du `FILNAMN` øvst i skriptet, eller slettar/flyttar den gamle fila.

### Korleis fungerer skriptet?

Dei viktigaste linjene:

```python
arduino = serial.Serial(port, 9600)                   # opne seriellporten
linje = arduino.readline().decode("utf-8").strip()    # les éi linje: "21.44"
tid = datetime.now().strftime("%Y-%m-%d %H:%M:%S")    # tidspunkt frå PC-en
skrivar.writerow([tid, linje])                        # skriv "2026-11-10 09:15:03,21.44"
```

Resten av skriptet finn Arduinoen automatisk, hoppar over meldingar som startar med `#`, og handterer feil.

### Fleire sensorar eller verdiar

Vil du logge fleire verdiar (t.d. to sensorar), sender Arduinoen dei med komma imellom:

```cpp
Serial.print(temperatur1, 2);
Serial.print(",");
Serial.println(temperatur2, 2);
```

og du endrar `KOLONNAR` i Python-skriptet:

```python
KOLONNAR = ["temperatur_inne", "temperatur_ute"]
```

### Feilsøking, spor A

| Problem | Løysing |
|---|---|
| `Fann ikkje noko Arduino-kort` | Sjekk USB-kabelen. Skriptet skriv ut ei liste over portar: kopier rett port inn i `PORT = "..."` øvst i skriptet. |
| `Problem med seriellporten: ... Access denied / Resource busy` | Serial Monitor (eller eit anna skript) brukar porten. Lukk det. |
| `ModuleNotFoundError: No module named 'serial'` | pyserial er ikkje installert i miljøet du brukar. Vel `.venv`, eller køyr `pip install pyserial` i terminalen. |
| Det kjem ingen målingar | Trykk RESET på Arduinoen éin gong. Sjekk at `BAUD` i skriptet er lik `Serial.begin(...)`. |
| Rare linjer blir hoppa over | Arduinoen sender noko anna enn eitt tal per linje. Sjekk utskrifta i Serial Monitor. |

---

## Spor B: SD-kort med MKR MEM Shield

Med eit **MKR MEM Shield** kan Arduinoen lagre målingane sjølv, utan PC. Då kan du til dømes setje loggaren i kjøleskapet, ute på verandaen eller i sjøen over natta.

### Utstyr

- MKR MEM Shield
- microSD-kort, helst 32 GB eller mindre
- Straum utan PC: USB-powerbank eller LiPo-batteri (3,7 V, JST-plugg) kopla til batterikontakten på MKR-kortet

> **Powerbank-felle:** Mange powerbankar skrur seg av når straumtrekket er lite, og Arduinoen trekkjer svært lite. Test at powerbanken held seg på i minst ein time før du set i gang eit langt forsøk.

### Steg 1: Formater SD-kortet (FAT32)

SD-biblioteket les berre kort som er formaterte som **FAT16** eller **FAT32**. Nye kort er som regel ferdig formaterte, men det er lurt å gjere det sjølv. *Alt på kortet blir sletta.*

**Windows**

1. Set kortet i PC-en (eventuelt med adapter).
2. Opne **Filutforskar**, høgreklikk på minnekortet og vel **Formater…**
3. Vel filsystem **FAT32** og trykk **Start**.

(Kort større enn 32 GB kan ikkje formaterast som FAT32 i Windows sitt eige verktøy. Bruk eit mindre kort, eller *SD Card Formatter* frå <https://www.sdcard.org>.)

**Mac**

1. Set kortet i Mac-en.
2. Opne **Diskverktøy** (*Programmer → Verktøy*).
3. Vel minnekortet i lista til venstre, og trykk **Slett**.
4. Vel format **MS-DOS (FAT)** og skjema **Master Boot Record**. Trykk **Slett**.

### Steg 2: Set saman maskinvara

1. Set microSD-kortet i holdaren på MEM Shield.
2. Plugg MKR NB 1500 oppå MEM Shield, slik at pinnenamna på kortet stemmer med pinnenamna på shieldet. Pinnane går gjennom, så du koplar sensoren til akkurat som før.
3. Kople sensoren som i del 1 (DATA på **pinne 2**). Pinne 4 blir brukt av SD-kortet, så den kan du ikkje bruke til sensoren.

### Steg 3: Installer SD-biblioteket

I Arduino IDE: **Library Manager** → søk etter `SD` → installer **SD** av *Arduino* (er det merka *INSTALLED*, er det allereie klart).

### Steg 4: Last opp og test

1. Opne [`arduino/02-sd-kort/02-sd-kort.ino`](arduino/02-sd-kort/02-sd-kort.ino) og trykk **Upload**.
2. Opne Serial Monitor. Du skal sjå `Loggar til LOGG00.CSV` og deretter målingar.
3. Den gule lampa blinkar kort kvar gong ei måling blir lagra. Blinkar ho **fort heile tida**, fann ikkje Arduinoen SD-kortet.

Kvar gong Arduinoen startar (straum på eller RESET), lagar han ei **ny fil**: `LOGG00.CSV`, `LOGG01.CSV` osv.

### Steg 5: Gjennomfør målinga

1. **Skriv ned klokkeslettet** når du koplar til straumen. Du treng det for å finne ut når målingane vart gjort.
2. La loggaren stå så lenge forsøket varer.
3. Ta ut straumen, ta ut SD-kortet og set det i PC-en.
4. Kopier CSV-fila inn i mappa `3-logging-til-csv`.

Fila ser slik ut:

```text
sekund,temperatur
0,21.81
10,21.81
20,21.75
```

### Kvifor «sekund sidan start» og ikkje klokkeslett?

Arduinoen veit ikkje kva klokka er. Funksjonen `millis()` tel berre millisekund sidan kortet starta. Derfor lagrar vi sekund, og reknar om i Python etterpå:

```python
sd["tid"] = pd.Timestamp("2026-11-10 08:00:00") + pd.to_timedelta(sd["sekund"], unit="s")
```

Dette er gjort ferdig i [`analyser-eigne-data.ipynb`](analyser-eigne-data.ipynb).

<details>
<summary>For dei spesielt interesserte: Ekte klokkeslett på Arduinoen</summary>

- **Innebygd klokke (RTC):** MKR-korta har ei innebygd sanntidsklokke som kan brukast med biblioteket **RTCZero**. Men ho må stillast kvar gong kortet får straum, og nullstillast når straumen går. Ho er nyttig om du stiller ho frå mobilnettet (sjå under).
- **Klokke frå mobilnettet:** MKR NB 1500 kan hente rett tid frå mobilnettet med biblioteket **MKRNB** (`nbAccess.getTime()`). Det krev eit aktivt SIM-kort med NB-IoT/LTE-M, antenne og dekning, og helst eit LiPo-batteri, sidan modemet trekkjer mykje straum.
- **Ekstern RTC-modul** (t.d. DS3231) med eige knappebatteri held tida sjølv når Arduinoen er utan straum.

</details>

### Feilsøking, spor B

| Problem | Løysing |
|---|---|
| `Fann ikkje SD-kortet` / lampa blinkar fort | Sit kortet heilt inne? Er det formatert som FAT32? Prøv eit anna (mindre) kort. |
| Fila er tom eller manglar | Kortet vart teke ut medan Arduinoen skreiv. Ta alltid ut straumen før du tek ut kortet. |
| Berre éi måling i fila | Arduinoen startar på nytt heile tida, t.d. på grunn av dårleg straum. Prøv USB frå PC. |
| Det blir mange LOGG-filer | Kvar oppstart gir ny fil. Sjekk kva for ei fil som har flest linjer. |

---

## Analyser dataa dine

Opne [`analyser-eigne-data.ipynb`](analyser-eigne-data.ipynb). Notatboka viser korleis du:

- les fila frå spor A eller spor B
- fjernar DS18B20-feilverdiane **−127** og **85**
- lagar grafar og reknar ut endring per minutt
- vurderer usikkerheit og støy

Før du har eigne data, kan du prøve notatboka med dei **simulerte** filene i `eksempeldata/`.

Bruk òg teknikkane frå [del 2](../2-csv-og-dataanalyse/02-tolke-data.ipynb): `resample`, `rolling`, `describe`, `idxmax` og så vidare.

---

## Forslag til forsøk

Vel eit forsøk, lag ei **hypotese** (kva trur du vil skje?), mål, analyser og presenter funna.

| Forsøk | Spor | Spørsmål du kan undersøkje |
|---|---|---|
| **Avkjøling av varmt vatn** | A | Kjølner vatnet fortare med eller utan lokk? I ein keramikkopp eller ein termos? Passar målingane med Newtons avkjølingslov? |
| **Kalibrering** | A | Kva viser sensoren i isvatn (0 °C)? Kor stort er avviket? Mål med fleire sensorar samtidig og samanlikn. |
| **Klasserommet gjennom ein skuledag** | A eller B | Kor mykje stig temperaturen når klassen er der? Kva skjer når vindauget blir opna? |
| **Kjøleskap eller frysar** | B | Kor stabil er temperaturen? Kva skjer når døra blir opna? Kor lang tid tek det før temperaturen er tilbake? |
| **Ute over eit døgn** | B | Når på døgnet er det kaldast og varmast? Samanlikn med <https://seklima.met.no>. |
| **Sjøtemperatur** | B | Kan du lage din eigen versjon av Nordnes Sjøbad? (Proben er vasstett, men Arduinoen og SD-kortet må vernast mot vatn!) |

### Spørsmål til refleksjon

1. Kor nøyaktige er målingane dine? Kva er dei viktigaste kjeldene til usikkerheit?
2. Korleis kunne du redusert usikkerheita? Prøv det!
3. Kunne valet av måleintervall (kor ofte du måler) påverka resultatet?
4. Er det noko i dataa dine som ser rart ut? Kan du forklare det?
5. Korleis kunne loggaren blitt forbetra eller utvida? (Fleire sensorar? Skjerm? Sende data over mobilnettet?)

---

**Førre del:** [Del 2: CSV-filer og tolking av data](../2-csv-og-dataanalyse/)
