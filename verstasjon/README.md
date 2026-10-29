# Verstasjon med Raspberry Pi og Enviro+

`verstasjon.py` les av sensorane på eit **Pimoroni Enviro+**-kort som sit på ein Raspberry Pi. Målingane blir lagra i ei **CSV-fil** og/eller sende til **Thingspeak**, der du kan sjå dei som grafar på nettet.

| Måling        | Sensor  | Eining |
|---------------|---------|--------|
| Temperatur    | BME280  | °C     |
| Lufttrykk     | BME280  | hPa    |
| Luftfukt      | BME280  | %      |
| Svevestøv PM2.5 og PM10 | PMS5003 (ekstra, koplast til Enviro+) | µg/m³ |

## Kort om korleis programmet verkar

1. **Oppstart:** Programmet startar sensorane og skjermen. Om ein del ikkje vil starte (til dømes om svevestøvsensoren ikkje er kopla til), skriv programmet ei feilmelding og held fram utan den delen.
2. **Måling:** Sensorane blir lesne, og verdiane blir samla i ei *ordbok* (`dict`), til dømes `{"tidspunkt": "2026-10-29 12:00:00", "temperatur": 21.4, ...}`.
3. **Lagring:** Målinga blir skriven nedst i CSV-fila og/eller send til Thingspeak, alt etter kva du har slått på.
4. **Gjenta:** I løkkje-modus ventar programmet `INTERVALL` sekund og startar på nytt frå steg 2.

### Temperaturkorrigering

BME280-sensoren sit like ved prosessoren på Raspberry Pi-en, og han blir varma opp av den. Difor les programmet òg temperaturen til prosessoren og trekkjer frå litt:

```
korrigert = målt - (cpu_temp - målt) / KOMPENSASJONSFAKTOR
```

Samanlikn med eit vanleg termometer og juster `KOMPENSASJONSFAKTOR` til tala stemmer.

### Feilhandtering

Ein verstasjon skal kunne stå åleine i lang tid, så programmet er laga for å **ikkje krasje**:

- Ein sensor som ikkje svarar gir ei tom celle i CSV-fila i staden for at heile programmet stoppar.
- Svevestøvsensoren blir nullstilt og prøvd igjen opptil tre gonger om avlesinga feilar.
- Manglar du nettverk, blir det skrive ei feilmelding, men målinga blir likevel lagra i CSV-fila.
- CSV-fila blir opna og lukka for kvar måling, slik at ingenting går tapt om straumen går.

## Det du må gjere før du startar

### 1. Installer bibliotek

Bruk installasjonsskriptet til Pimoroni (det slår òg på I2C, SPI og serieporten):

```bash
git clone https://github.com/pimoroni/enviroplus-python
cd enviroplus-python
./install.sh
```

På nyare Raspberry Pi OS (Bookworm og nyare) blir biblioteka installerte i eit *virtuelt miljø*, normalt `~/.virtualenvs/pimoroni`. Då må du aktivere det før du køyrer programmet:

```bash
source ~/.virtualenvs/pimoroni/bin/activate
pip install requests   # om det ikkje er installert frå før
```

### 2. Opprett ein Thingspeak-kanal (berre om du vil bruke Thingspeak)

1. Lag ein gratis konto på [thingspeak.mathworks.com](https://thingspeak.mathworks.com).
2. Lag ein ny kanal med fem felt: *Temperatur, Trykk, Fuktighet, PM2.5, PM10* (i den rekkjefølgja).
3. Gå til fana **API Keys** og kopier **Write API Key**.

Thingspeak lagrar sjølv tidspunktet for kvar måling, så du treng ikkje sende det.

> Gratisversjonen av Thingspeak tek berre imot éi måling kvart 15. sekund.

### 3. Endre innstillingane

Opne `verstasjon.py`. Øvst finn du ein blokk med innstillingar. Det er normalt berre der du treng endre noko:

```python
BRUK_CSV = True          # Skriv målingane til CSV-fil?
BRUK_THINGSPEAK = True   # Send målingane til Thingspeak?
BRUK_SKJERM = True       # Vis temperatur og Wi-Fi-status på skjermen?
BRUK_PMS5003 = True      # Er svevestøvsensoren kopla til?

INTERVALL = 60           # Sekund mellom kvar måling
CSV_FIL = "verstasjon.csv"
THINGSPEAK_API_KEY = "DIN_WRITE_API_KEY"   # Lim inn nøkkelen din her
```

Set `True` eller `False` for å slå ting av og på. **Ikkje del API-nøkkelen din**, for då kan andre skrive til kanalen din.

## Køyre programmet

Det finst to måtar. Vel den som passar best.

### A) Løkkje: programmet går til du stoppar det

```bash
python3 verstasjon.py
```

Programmet måler kvar `INTERVALL` sekund. Trykk **Ctrl+C** for å stoppe. Dette passar når du vil sjå målingane direkte i terminalen.

### B) Éi måling om gongen, styrt av crontab

```bash
python3 verstasjon.py --ein-gong
```

Programmet tek éi måling og avsluttar. Saman med `crontab` kan Raspberry Pi-en køyre programmet automatisk, til dømes kvart 5. minutt. Det er robust, for sjølv om noko skulle krasje, blir programmet starta på nytt ved neste måling.

Opne crontab med `crontab -e` og legg til ei linje nedst:

```bash
# Kvart 5. minutt (tilpass stiane til der du har lagt filene)
*/5 * * * * /home/pi/.virtualenvs/pimoroni/bin/python /home/pi/verstasjon/verstasjon.py --ein-gong >> /home/pi/verstasjon/logg.txt 2>&1
```

- Bruk **full sti** både til Python og til programmet, for crontab veit ikkje kva mappe du står i.
- `>> logg.txt 2>&1` lagrar alt programmet skriv (òg feilmeldingar) i ei loggfil. Sjekk denne fila om noko ikkje verkar.
- Har du ikkje virtuelt miljø, byt ut `/home/pi/.virtualenvs/pimoroni/bin/python` med `/usr/bin/python3`.
- Kvar køyring tek rundt 30 sekund, sidan svevestøvsensoren må varme opp (`PMS_OPPVARMING`). Ikkje køyr oftare enn kvart minutt.

Vil du heller at løkkja (A) skal starte automatisk når Pi-en startar, kan du bruke:

```bash
@reboot sleep 60 && /home/pi/.virtualenvs/pimoroni/bin/python /home/pi/verstasjon/verstasjon.py >> /home/pi/verstasjon/logg.txt 2>&1
```

Ikkje bruk A og B samstundes, for dei vil då slåst om sensorane.

## CSV-fila

Fila blir laga automatisk med overskrifter første gong. Kvar måling blir ei ny linje:

```
tidspunkt,temperatur,trykk,fuktighet,pm25,pm10
2026-10-29 12:00:00,21.43,1003.12,41.8,3,5
2026-10-29 12:05:00,21.51,1003.08,41.5,2,4
```

Fila kan opnast i Excel eller lesast inn med Pandas: `pd.read_csv("verstasjon.csv", parse_dates=["tidspunkt"])`. Sjå mappa `tolking` for døme.

## Feilsøking

| Problem | Mogleg løysing |
|---------|----------------|
| `ModuleNotFoundError` | Biblioteka er ikkje installerte, eller du har ikkje aktivert det virtuelle miljøet. |
| `Klarte ikkje starte PMS5003` | Sjekk kabelen. Har du ikkje sensoren, set `BRUK_PMS5003 = False`. |
| `Thingspeak avviste målinga` | Feil API-nøkkel, eller mindre enn 15 sekund sidan førre sending. |
| `Fekk ikkje kontakt med Thingspeak` | Pi-en manglar nettverk. Målinga er likevel lagra i CSV-fila. |
| Temperaturen er for høg | Juster `KOMPENSASJONSFAKTOR`, eller flytt Enviro+ vekk frå Pi-en med ein kabel. |
| Crontab gjer ingenting | Sjekk `logg.txt`, og at du har brukt full sti overalt. |

## Idear til vidare arbeid

- Legg til fleire sensorar Enviro+ har, til dømes lys (`ltr559`) eller gass (`enviroplus.gas`). Du må då leggje til ei ny kolonne i `KOLONNAR`, lese verdien i `les_sensorar()` og eventuelt eit nytt felt i `THINGSPEAK_FELT`.
- Mellomlagre målingar som ikkje kom fram til Thingspeak (til dømes i ei liste), og send dei når nettverket er tilbake.
- La skjermen vise andre verdiar, eller byte mellom dei.
- Rekn ut middel, maks og min for kvart døgn frå CSV-fila.
