# Importerer pandas for å jobbe med CSV-fila og matplotlib for å teikne grafar
import pandas as pd # Installer pandas ved å bruke kommandoen "pip install pandas" i terminalen
import matplotlib.pyplot as plt # Installer matplotlib ved å bruke kommandoen "pip install matplotlib" i terminalen

# Les inn data
data = pd.read_csv('data.csv', sep=',', header=0) # header=0 betyr at første rad er kolonnenamn

print(data.describe()) # Skriv ut statistikk om data

# Lagre data i variablar vha pandas
tid = data['tidspunkt'] 
temperatur = data['temperatur']
luftfuktighet = data['luftfuktighet']
lufttrykk = data['lufttrykk']
partikkelkonsentrasjon = data['partikkelkonsentrasjon']

# Plot temperatur
plt.plot(tid, partikkelkonsentrasjon)
plt.xlabel('Tid')
plt.ylabel('PM2.5')
plt.title('Partikkelkonsentrasjon i lufta')
plt.xticks(rotation=90) # rotate labels on the x-axis
plt.savefig('07-visualisering-plot.png') # save figure as png
plt.show()