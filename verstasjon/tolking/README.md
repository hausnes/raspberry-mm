# Tolke verdata

I denne mappa ligg eksempel på korleis du kan lese, analysere og visualisere data frå verstasjonen med Python, Pandas og Matplotlib.

## Rekkjefølgje

| Fil | Innhald |
|---|---|
| `tolke-ute.ipynb` | **Start her.** Lese CSV-fil, velje ut kolonnar og rader, enkle plott, plotte éin dag, og det same med `csv`-biblioteket utan Pandas. |
| `tolke-v2.ipynb` | Tid som indeks, glidande gjennomsnitt, formatere tidsaksen og to y-aksar i same figur. |
| `meir-eksempel.ipynb` | Rydde i data, finne hol, døgnstatistikk med `resample`, døgnvariasjon med `groupby`, korrelasjon, histogram, samanlikne inne og ute, og lagre resultat. |
| `oppgaver.ipynb` | 13 oppgåver i tre nivå. |
| `losningsforslag.ipynb` | Løysingsforslag til oppgåvene. |
| `eks-befolkning/` | Same teknikkar brukte på befolkningstal (semikolonseparert fil frå SSB). |
| `eks-trond/trond.py` | Minimalt eksempel på å lese ei CSV-fil inn i ei liste med `csv`-biblioteket. |

## Datafiler

| Fil | Innhald |
|---|---|
| `utestasjon-bones.csv` | Verstasjon ute på Øvre Kråkenes, 15.11.–4.12.2022, måling ca. kvart 33. sekund. Kolonnar: `dato, temperatur, lufttrykk, luftfuktighet, pm25, pm10`. |
| `../øvre-kråkenes-188-inne-2022/v0-verstasjon.csv` | Stasjon inne i same hus, 7.11.–30.11.2022. Brukt i `meir-eksempel.ipynb`. |
| `data.csv` | **Simulerte** (tilfeldige) data, ikkje ekte målingar. Brukt i oppgåve 12. |
| `07-visualisering-plot.png` | Plott av `data.csv` der tidspunkta vart lesne som tekst. Legg merke til den uleselege x-aksen. Det er det som skjer om du gløymer `parse_dates`. |

### Ting å vere merksam på i dataa

- **Dei første 45 minutta** (15.11. kl. 19.00–19.45) stod utestasjonen inne og målte rundt 26 °C. Desse målingane bør fjernast før analyse (sjå `meir-eksempel.ipynb`).
- Det er **fleire hol** i dataa, det lengste på over 20 timar (26.11.). Døgnsnitt for døgn med hol er mindre til å stole på.
- **Luftfukta** ute er målt til rundt 36 % i snitt, som er altfor lågt. Sensoren blir varma opp av Raspberry Pi-en (sjå oppgåve 13).
- Lufttrykket ute er i snitt **1 hPa høgare** enn inne. Det tyder på ein liten kalibreringsforskjell mellom sensorane.

## Bruke data frå din eigen verstasjon

`verstasjon.py` lagar CSV-filer med andre kolonnenamn: `tidspunkt, temperatur, trykk, fuktighet, pm25, pm10`.

```python
data = pd.read_csv("verstasjon.csv", parse_dates=["tidspunkt"], index_col="tidspunkt")
```

## Det du treng

Python 3 med `pandas`, `matplotlib` og `jupyter`:

```bash
pip install pandas matplotlib jupyter
```

Notatbøkene kan òg opnast i VS Code (med Jupyter-utvidinga), Google Colab eller JupyterLite. Datafila må då lastast opp i same mappe som notatboka.
