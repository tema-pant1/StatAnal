import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def asymetry(s):
    s = s.dropna()
    mu3 = ((s - s.mean())**3).mean()
    sigma = s.std(ddof=0)
    return mu3 / sigma ** 3

url = "https://www.pogodaiklimat.ru/history/07481.htm"
file_name_src = "weather.txt"
file_name_param = "param.txt"
fn_blowouts = "blowouts.txt"

weather = pd.read_html(url)[1]

weather.columns = weather.iloc[0]
weather.index =  weather.index + 1919
weather.columns.name = "Год"

weather = weather.iloc[1:, :-1]

weather = weather.apply(pd.to_numeric, errors = 'coerce')
weather = weather.replace(999.9, np.nan)

with open(file_name_src, 'w') as file:
    file.write(weather.to_string())

q = weather.quantile([0.25, 0.5, 0.75])
Q1 = q.iloc[0]
Q3 = q.iloc[2]
IQR = Q3 - Q1
sd = weather.std()
mean = weather.mean()

param = pd.DataFrame({
    'N' : weather.count(),
    'Min' : weather.min(),
    'Max' : weather.max(),
    'Mean' : mean,
    'Sd' : sd,
    'SEM' : weather.sem(),
    'Q1' : Q1,
    'Me' : q.iloc[1],
    'Q3' : Q3,
    'IQR' : IQR,
    'CV' : sd / mean * 100,
    'As' : weather.apply(asymetry)
})

with open(file_name_param, 'w') as file:
    file.write(param.to_string())

#Здесь рисуется блочная диаграмма
fig, ax = plt.subplots(figsize = (10, 6))
ax.boxplot([weather[c].dropna() for c in weather.columns], tick_labels = weather.columns)
ax.set_xlabel("Месяц", fontsize=14)
ax.set_ylabel("Температура,°C", fontsize=14)
fig.suptitle("Распределение температуры по месяцам", fontsize=16)
fig.savefig('plot.png')


raw = []
for m in weather.columns:
    mounth = weather[m]
    q1 = mounth.quantile(0.25)
    q3 = mounth.quantile(0.75)
    iqr = q3 - q1
    low = q1 - 1.5*iqr
    up = q3 + 1.5*iqr
    mask = (mounth < low) | (mounth > up)

    for i in mounth[mask].index:
        raw.append({"Год": i, "Месяц": m, "Температура": mounth[i]})

blowout = pd.DataFrame(raw, columns=["Год","Месяц","Температура"])
blowout.sort_values("Год", inplace = True)

with open(fn_blowouts, 'w') as file:
    file.write(blowout.to_string())

axes = weather.hist(column=weather.columns, 
             figsize=(16, 10), 
             layout = (3, 4), 
             bins=8, 
             grid=False, 
             edgecolor = 'black')

for raw in axes:
    for ax in raw:
        ax.set_xlabel("Температура,°C", fontsize=10)
        ax.set_ylabel("Количество, лет", fontsize=10)
        # медиана: заголовок оси совпадает с названием месяца
        med = weather[ax.get_title()].median()
        ax.axvline(med, color='red', linestyle='--', linewidth=2,
                   label=f"Me = {med:.1f}")
        ax.legend(fontsize=9)
        
fig = plt.gcf()
fig.suptitle("Распределение температуры по месяцам", fontsize=16)
plt.tight_layout(pad=2.6)
fig.savefig("histograms.png")

