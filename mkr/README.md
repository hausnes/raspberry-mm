# Temperaturmåling med Arduino MKR NB 1500

Eit opplegg i tre delar for **Teknologi og forskingslære 1**. Elevane set opp ein temperatursensor, lærer å tolke måledata frå CSV-filer, og loggar til slutt sine eigne målingar.

| Del | Innhald | Utstyr og programvare |
|---|---|---|
| [**Del 1: Set opp Arduino og mål temperatur**](1-oppsett-og-maling/) | Installere Arduino IDE (Mac og Windows), board-pakke og bibliotek. Kople DS18B20 med pull-up-motstand på breadboard. Lese av temperaturen. | Arduino MKR NB 1500, DS18B20 (vasstett probe), 4,7 kΩ motstand, breadboard. Arduino IDE 2. |
| [**Del 2: CSV-filer og tolking av data**](2-csv-og-dataanalyse/) | Kva er CSV, tidskodar (ISO 8601), skrive og lese CSV. Analyse av over to år med badetemperaturar frå Nordnes Sjøbad: frå enkle oppslag til rydding, døgnvariasjon og korrelasjon. 15 oppgåver med løysingsforslag. | VS Code, Python, Pandas, Matplotlib (Jupyter-notatbøker) |
| [**Del 3: Logg eigne målingar til CSV**](3-logging-til-csv/) | Spor A: Arduinoen sender målingar over USB, og eit Python-skript lagrar dei i CSV med tidspunkt. Spor B: Arduinoen lagrar sjølv på SD-kort (MKR MEM Shield). Analyse av eigne data og forslag til forsøk. | Som del 1 og 2, + pyserial. Spor B: MKR MEM Shield og microSD-kort. |

Del 1 kan brukast åleine. Del 2 kan òg brukast åleine (utan Arduino).

## Kopling til kompetansemål

Frå [læreplanen i teknologi og forskingslære 1](https://www.udir.no/lk20/tnf01-03/kompetansemaal-og-vurdering/kv975) (kompetansemåla finst berre på bokmål):

| Kompetansemål | Kvar i opplegget |
|---|---|
| utvikle og teste et produkt som inneholder en mikrokontroller, og vurdere muligheter for utvidelser og forbedringer | Del 1 og 3: temperaturloggaren. Refleksjonsspørsmål om utvidingar i del 3. |
| utforske og bruke analoge og digitale signaler fra sensorer og beskrive sensorenes ulike bruksområder | Del 1: DS18B20 som digital sensor (1-Wire), samanlikna med analoge sensorar. |
| designe og lage et produkt som produserer empiriske data og presentere funn fra eget datamateriale | Del 3: loggar til CSV, analyse og presentasjon av eigne forsøk. |
| analysere datamateriale fra forsøk og reflektere over og teste om usikkerheten kan reduseres | Del 2: rydding av feilmålingar og hol. Del 3: støy, kalibrering i isvatn, korleis redusere usikkerheit. |
| bruke kvantitativ metode i forsøk og vurdere påliteligheten til resultatene | Del 2: «Kor mykje kan vi stole på dataa?». Del 3: forsøksforslag med hypotese, måling og vurdering. |

## Om filene

- Arduino-skissene er testkompilerte for `arduino:samd:mkrnb1500` med biblioteka OneWire, DallasTemperature og SD.
- Notatbøkene er køyrde med Python 3.14, pandas 3.1 og matplotlib 3.11, og ligg med utdata slik at dei kan lesast direkte på GitHub. Dei er òg testa med pandas 2.3.
- `2-csv-og-dataanalyse/data/nordnes-sjobad.csv` er ein kopi av [hausnes/nordnes-sjobad](https://github.com/hausnes/nordnes-sjobad/blob/data/temperatur.csv) henta 4. november 2026.
- Filene i `3-logging-til-csv/eksempeldata/` er **simulerte**, ikkje ekte målingar.
