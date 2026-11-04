# Del 1: Set opp Arduino og mål temperatur

I denne delen skal du:

1. installere Arduino IDE (programvara du skriv Arduino-kode i)
2. installere støtte for kortet **Arduino MKR NB 1500**
3. installere biblioteka som trengst for temperatursensoren **DS18B20**
4. kople opp sensoren på eit breadboard
5. lese av temperaturen og sjå målingane på skjermen

Når du er ferdig med denne delen, har du ein fungerande temperaturmålar.

---

## Utstyrsliste

| Ting | Tal | Kommentar |
|---|---|---|
| Arduino MKR NB 1500 | 1 | Antenna og SIM-kortet treng du ikkje no. |
| Micro-USB-kabel | 1 | Han må kunne overføre data. Somme kablar kan berre lade, og då finn ikkje PC-en kortet. |
| DS18B20, vasstett probe | 1 | Metallhylse med kabel og tre leidningar. |
| Motstand 4,7 kΩ | 1 | Fargekode: gul, fiolett, raud (+ gull). |
| Breadboard | 1 | |
| Koplingsleidningar (hann-hann) | 3–5 | |

---

## Steg 1: Installer Arduino IDE

Arduino IDE er gratis og finst for både Mac og Windows. Vi brukar **versjon 2** (2.x).

> **Skulemaskin?** Treng du administratorrettar for å installere, må du kanskje bruke skulen sitt programvaresenter (t.d. Firmaportal/Company Portal på Windows eller Self Service på Mac). Spør læraren.

### Windows

1. Gå til <https://www.arduino.cc/en/software>.
2. Under **Arduino IDE 2.x**, vel **Windows – Win 10 and newer, 64 bits** (installasjonsfil, `.exe`).
3. Du blir spurd om du vil gi ei gåve. Trykk **Just Download**.
4. Opne fila du lasta ned (ligg vanlegvis i *Nedlastingar*).
5. Godta lisensen, og vel *Anyone who uses this computer* eller *Only for me*. Begge fungerer.
6. Trykk **Install**, og deretter **Finish**. Arduino IDE startar.
7. Første gong IDE-en startar, kan Windows spørje om du vil installere **drivarar** (*Arduino USB Driver*, *Adafruit Industries LLC Ports* e.l.). Trykk **Installer** / **Ja** på alle. Utan desse finn ikkje Windows kortet.
8. Windows-brannmuren kan spørje om tilgang for Arduino IDE. Trykk **Tillat**.

### Mac

1. Gå til <https://www.arduino.cc/en/software>.
2. Under **Arduino IDE 2.x**, vel rett versjon for maskina di:
   - **macOS Apple Silicon** om Mac-en har M1, M2, M3 eller nyare brikke
   - **macOS Intel** om Mac-en er eldre
   - Usikker? Trykk på eple-menyen  → **Om denne maskinen**. Står det *Brikke: Apple M…*, er det Apple Silicon.
3. Trykk **Just Download**.
4. Opne `.dmg`-fila, og dra **Arduino IDE** over i **Programmer** (Applications).
5. Start Arduino IDE frå Programmer-mappa eller Launchpad.
6. Får du meldinga *«Arduino IDE» er lasta ned frå Internett. Er du sikker på at du vil opne det?*, trykk **Opne**.
7. Mac treng ingen ekstra drivarar. Men første gong du koplar til kortet, kan macOS spørje **«Tillat at tilbehør koplar til?»**. Trykk **Tillat**.

---

## Steg 2: Installer støtte for MKR-kortet (board-pakke)

Arduino IDE har ikkje støtte for alle korttypar frå start. MKR NB 1500 brukar ein ARM-prosessor (SAMD21), så vi må installere pakken for denne.

Dette steget er likt på Mac og Windows.

1. Kople MKR-kortet til PC-en med USB-kabelen. Den grøne lampa (ON) skal lyse.
2. I Arduino IDE: trykk på ikonet **Boards Manager** i menyen til venstre (ikonet ser ut som eit kretskort), eller vel **Tools → Board → Boards Manager…**
3. Skriv `MKR` i søkjefeltet.
4. Finn **Arduino SAMD Boards (32-bits ARM Cortex-M0+)** og trykk **INSTALL**.
5. Vent til installasjonen er ferdig. Det kan ta nokre minutt. Windows kan spørje om å installere drivarar igjen: trykk **Ja**.

> Arduino IDE oppdagar ofte kortet sjølv og spør om du vil installere pakken. Då kan du berre trykke **Yes**.

### Vel kort og port

1. Øvst i vindauget er det ein nedtrekksmeny der det står **Select Board**. Trykk på han.
2. Vel kortet ditt. Det står t.d. **Arduino MKR NB 1500** og under står porten:
   - Windows: `COM3`, `COM4` eller liknande
   - Mac: `/dev/cu.usbmodem1101` eller liknande
3. Står kortet ikkje i lista? Vel **Select other board and port…**, søk etter `MKR NB 1500`, og vel porten.

### Test at alt fungerer

Før vi koplar til sensoren, testar vi at PC-en og kortet snakkar saman.

1. Opne [`01-blink/01-blink.ino`](01-blink/01-blink.ino) (**File → Open…**), eller kopier koden inn i eit nytt vindauge (**File → New Sketch**).
2. Trykk **Upload** (pila →, øvst til venstre). Første gong tek det litt tid.
3. Når det står **Done uploading** nede til høgre, skal den gule lampa på kortet blinke.
4. Opne **Serial Monitor**: trykk forstørringsglaset øvst til høgre (eller `Ctrl + Shift + M` på Windows, `Cmd + Shift + M` på Mac).
5. Sjekk at farten nede til høgre i Serial Monitor er **9600 baud**. Du skal sjå *Blink nummer 1, 2, 3 …*

Fungerer det? Bra, då er programvara klar!

---

## Steg 3: Installer bibliotek for DS18B20

DS18B20 snakkar med Arduinoen ved hjelp av ein protokoll som heiter **1-Wire**. Det betyr at all data går gjennom éin leidning. Vi treng to bibliotek, altså ferdig kode som andre har skrive:

- **OneWire**: tek seg av sjølve kommunikasjonen på leidningen
- **DallasTemperature**: gjer det enkelt å be sensoren om temperaturen

Dette steget er likt på Mac og Windows.

1. Trykk på ikonet **Library Manager** i menyen til venstre (ser ut som bøker), eller vel **Tools → Manage Libraries…**
2. Søk etter `DallasTemperature`.
3. Finn **DallasTemperature** av *Miles Burton* og trykk **INSTALL**.
4. Du blir spurd om du vil installere avhengigheiter (*dependencies*), altså **OneWire**. Trykk **INSTALL ALL**.
5. Kontroller: søk etter `OneWire`. **OneWire** av *Paul Stoffregen* skal vere merka *INSTALLED*.

> Trykte du *Install without dependencies* ved eit uhell? Søk etter `OneWire` og installer han for hand.

---

## Steg 4: Kople opp sensoren

### Kva er ein pull-up-motstand?

Datalinja til DS18B20 må «haldast oppe» på 3,3 V når ingen sender noko. Sensoren sender data ved å trekkje linja ned til 0 V i korte augneblink. Motstanden mellom DATA og 3,3 V gjer at linja går tilbake til 3,3 V etterpå. Utan denne motstanden finn ikkje Arduinoen sensoren, eller han gir tilfeldige feilverdiar.

### Leidningane på proben

| Farge | Namn | Koplast til |
|---|---|---|
| Raud | VDD (straum) | **VCC** på MKR-kortet (3,3 V) |
| Svart | GND (jord) | **GND** på MKR-kortet |
| Gul (av og til kvit) | DATA | **Pinne 2** (merka `~2` eller `D2`) |

> **Fargane er ikkje alltid like.** Nokre probar har andre fargar. Sjekk databladet eller emballasjen dersom leidningane dine ikkje er raud/svart/gul.

> **Viktig: Bruk VCC, ikkje 5V.** MKR-korta tolererer berre 3,3 V på pinnane. Koplar du pull-up-motstanden til **5V**-pinnen, kan kortet bli øydelagt over tid.

### Koplingsskjema

```text
                MKR NB 1500
             ┌───────────────┐
             │           VCC ●─────────┬──────────── Raud (VDD)
             │               │         │
             │               │        ┌┴┐
             │               │        │ │ 4,7 kΩ
             │               │        │ │ (gul-fiolett-raud)
             │               │        └┬┘
             │               │         │
             │            ~2 ●─────────┴──────────── Gul (DATA)
             │               │
             │           GND ●────────────────────── Svart (GND)
             └───────────────┘
```

### Slik gjer du det på breadboardet

Eit breadboard har rader med fem hol som er kopla saman under plasten. Alt som står i same rad (same nummer på same side av midtkanalen) er kopla saman.

1. Ta USB-kabelen ut av kortet medan du koplar.
2. MKR-kortet har hol (hunn-kontaktar) på oversida av pinnerekkjene. Det enklaste er å la kortet liggje ved sida av breadboardet og stikke koplingsleidningane rett ned i hola på kortet. (Du kan òg setje kortet i breadboardet over midtkanalen, men då blir det trongt.)
3. Stikk dei tre leidningane frå proben inn i tre **ulike rader** på breadboardet, t.d. rad 20, 22 og 24.
4. Set motstanden mellom raden med **raud** leidning og raden med **gul** leidning. (Motstandar har ingen pluss og minus, så det spelar inga rolle kva veg han står.)
5. Bruk koplingsleidningar:
   - frå **VCC** på kortet til raden med **raud** leidning
   - frå **GND** på kortet til raden med **svart** leidning
   - frå **pinne 2** på kortet til raden med **gul** leidning
6. Be ein medelev sjekke koplinga før du koplar til USB-kabelen igjen.

> Tips: Leidningane på proben kan vere tynne og mjuke, og glir lett ut av breadboardet. Viss dei gjer det, kan du lodde på stive leidningar, eller bruke ein skrueterminal.

---

## Steg 5: Les av temperaturen

1. Opne [`02-temperatur/02-temperatur.ino`](02-temperatur/02-temperatur.ino) i Arduino IDE.
2. Trykk **Upload**.
3. Opne **Serial Monitor** (9600 baud). Du skal sjå noko slikt:

   ```text
   Fann 1 sensor(ar).
   Temperatur: 22.31 °C
   Temperatur: 22.31 °C
   Temperatur: 22.38 °C
   ```

4. Hald rundt metallhylsa med handa. Stig temperaturen?

### Sjå målingane som graf

Lukk Serial Monitor, og opne **Tools → Serial Plotter**. Serial Plotter teiknar tala som ein graf medan du måler. For at plottaren skal skjøne kva som er tal, er det lurt å endre utskrifta i `loop()` til:

```cpp
Serial.print("Temperatur:");
Serial.println(temperatur);
```

### Korleis fungerer koden?

```cpp
#include <OneWire.h>              // hent inn biblioteka
#include <DallasTemperature.h>

const int SENSOR_PINNE = 2;       // den gule leidningen sit i pinne 2

OneWire oneWire(SENSOR_PINNE);
DallasTemperature sensorar(&oneWire);
```

- `sensorar.begin()` i `setup()` startar kommunikasjonen og leitar etter sensorar.
- `sensorar.requestTemperatures()` ber sensoren om å gjere ei måling. Dette tek ca. 0,75 sekund.
- `sensorar.getTempCByIndex(0)` hentar målinga frå sensor nummer 0 (den første) i grader celsius.

Du kan faktisk kople fleire DS18B20 på same pinne. Då hentar du dei med indeks 0, 1, 2 osv.

---

## Feilsøking

| Problem | Moglege løysingar |
|---|---|
| Kortet dukkar ikkje opp under **Select Board** | Prøv ein annan USB-kabel (mange kablar kan berre lade). Prøv ein annan USB-port. På Windows: installer drivarane på nytt ved å installere board-pakken på nytt. |
| Opplastinga feilar, eller porten forsvinn | **Dobbeltklikk raskt på RESET-knappen** på kortet. Den gule lampa pulserer sakte. Kortet er no i opplastingsmodus. Vel porten på nytt (han kan ha fått nytt namn) og trykk **Upload**. |
| Serial Monitor viser rare teikn | Farten i Serial Monitor må vere den same som i `Serial.begin(...)` (9600). |
| Serial Monitor viser ingenting | Trykk RESET éin gong. Sjekk at rett port er vald. |
| `Fann 0 sensor(ar)` og *Feil: Fekk ikkje kontakt* | Sjekk koplinga. Står leidningane i rett rad? Er motstanden på plass? Er DATA kopla til pinne 2? |
| Temperaturen er **-127** | Arduinoen får ikkje svar frå sensoren. Same som over. |
| Temperaturen er **85** | 85 °C er verdien sensoren har rett etter oppstart, før han har målt noko. Oftast er det dårleg kontakt på straumen (raud/svart). |
| `OneWire.h: No such file or directory` | Biblioteket er ikkje installert. Gå tilbake til steg 3. |
| `Error: Port busy` eller *Access denied* | Eit anna program brukar porten. Lukk andre Arduino-vindauge og Python-skript som les frå kortet. |

---

## Litt om sensoren

| Eigenskap | Verdi |
|---|---|
| Måleområde | −55 °C til +125 °C |
| Nøyaktigheit | ±0,5 °C mellom −10 °C og +85 °C |
| Oppløysing | 0,0625 °C (12 bit) |
| Tid per måling | ca. 750 ms |
| Spenning | 3,0–5,5 V |

Legg merke til skilnaden på *oppløysing* og *nøyaktigheit*: Sensoren kan vise endringar på 0,06 °C, men den målte verdien kan likevel vere opptil 0,5 °C feil. Dette kjem vi tilbake til når vi skal vurdere kor pålitelege måledata er.

DS18B20 er ein **digital** sensor: han måler temperaturen sjølv og sender svaret som eit tal. Ein **analog** temperatursensor (som TMP36) gir i staden ei spenning som Arduinoen må rekne om til temperatur.

---

## Oppgåver

1. Endre koden slik at temperaturen blir målt kvart 5. sekund.
2. Kor raskt reagerer sensoren? Flytt proben frå romtemperatur til eit glas med kaldt vatn. Kor lang tid tek det før målinga er stabil?
3. Få den innebygde lampa (`LED_BUILTIN`) til å lyse når temperaturen er over 25 °C.
4. Skriv ut temperaturen i fahrenheit òg. (Tips: `sensorar.getTempFByIndex(0)`)
5. **Kalibrering:** Lag isvatn (mykje is, lite vatn, rør godt). Det skal halde 0,0 °C. Kva viser sensoren din? Samanlikn med dei andre gruppene. Er skilnaden innanfor ±0,5 °C?
6. Forklar med eigne ord kvifor vi treng pull-up-motstanden.

<details>
<summary>Løysingsforslag oppgåve 1, 3 og 4</summary>

**Oppgåve 1:** Endre konstanten øvst:

```cpp
const int VENTETID_MS = 5000;
```

**Oppgåve 3:** Legg til `pinMode(LED_BUILTIN, OUTPUT);` i `setup()`, og dette i `loop()` etter at temperaturen er lesen:

```cpp
if (temperatur > 25) {
  digitalWrite(LED_BUILTIN, HIGH);
} else {
  digitalWrite(LED_BUILTIN, LOW);
}
```

**Oppgåve 4:**

```cpp
float fahrenheit = sensorar.getTempFByIndex(0);
Serial.print(" (");
Serial.print(fahrenheit);
Serial.println(" °F)");
```

Alternativt kan du rekne det ut sjølv: `float fahrenheit = temperatur * 9.0 / 5.0 + 32;`

</details>

---

**Neste del:** [Del 2: CSV-filer og tolking av data](../2-csv-og-dataanalyse/)
