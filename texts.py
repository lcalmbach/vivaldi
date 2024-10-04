txt = {
    "intro": """Ein Jahr gliedern wir intuitiv in vier Jahreszeiten, besonders wenn es um das Wetter geht. Oft erinnern wir uns an besonders heisse Sommer, kalte Winter oder nasse Frühlinge. Damit ist unsere Erinnerung an das Wetter von Extremwerten beeinflusst. War der Sommer wirklich so schlecht, oder erinnern wir uns nur an die verregnete Wanderung zu Beginn der Ferien?Wir haben ein schlechtes Gespür dafür, wie warm oder kühl ein Sommer wirklich war und wie er sich mit den Sommer der letzten Jahre oder Jahrzehnten vergleicht. Grafiken helfen hier Abhilfe. Wetterdaten werden jedoch in der Regel als Zeitreihen dargestellt, was den Vergleich zwischen den Jahreszeiten verschiedener Jahr erschwert. 

Unsere App schliesst diese Lücke, indem sie die Jahreszeiten als Grundlage für umfassende Vergleiche verwendet. Die App ermöglicht es Ihnen, Wetterdaten spezifisch für Frühling, Sommer, Herbst und Winter sowohl grafisch als auch numerisch zu analysieren und zu vergleichen, sodass Unterschiede und Muster zwischen den Jahreszeiten über verschiedene Jahre hinweg klar erkennbar werden. Dargestellt wird in dieser App der meteorologische Sommer, Frühling, Herbst und Winter, wobei der Sommer von Juni bis August, der Herbst von September bis November, der Winter von Dezember bis Februar und der Frühling von März bis Mai reicht. Neben den Jahreszeiten können aber auch einzelne Monate oder Jahre mit den historischen Daten verglichen werden.

Alle Daten beziehen sich auf die [NBCN](https://www.meteoschweiz.admin.ch/wetter/messsysteme/bodenstationen/schweizer-klimamessnetz.html)-Station (National Basic Climatological Network) in Binningen, und die App wird täglich mit den neuesten Daten auf dem Opendata Portal [data.bs](https://data.bs.ch) aktualisiert. Die Messreihe deckt das Intervall von {} ab.

### Funktionen der App

- **Statistiken**: Die App zeigt die durchschnittlichen Temperaturen für jede Jahreszeit und für jedes Jahr an. So können Sie auf einen Blick erkennen, wie sich das Klima im Laufe der Zeit verändert hat. Man kann auch ein Ranking erstellen wobei als Parameter, nach welchem geordnet wird, ausgewählt werden kann (Mittlere Temperatur, Mindesttemperatur, Maximaltemperatur).

- **Grafiken**: Wählen Sie ein bestimmtes Jahr und eine Jahreszeit aus und vergleichen Sie diese mit einem oder mehreren anderen Jahren oder mit Klimanormalen. Die App visualisiert die Temperaturverläufe der ausgewählten Jahre und bietet Ihnen die Möglichkeit, diese Daten direkt mit den Klimanormalen zu vergleichen. Statt dem Datum verwendet die X-Achse den Tag seit Beginn der Jahreszeit. Dies erlaubt die Anzeige der Jahreszeiten auf der gleichen Zeitachse und damit einen direkten Vergleich. Beim kumulativen Mittel wird der Durchschnitt der Temperaturwerte für jeden Tag seit Beginn der Jahreszeit berechnet. Dies ermöglicht es, aufzuzeigen, dass beispielweise auch ein Sommer mit kühlem Start "aufholen kann" und am Ende ein vergleichbarer oder sogar höherer Mittelwert wie Sommer in vergangenen Jahren erreichen kann. Solche Sommer werden oft als "zu kalt" in Erinnerung behalten, obwohl sie insgesamt nicht unbedingt kälter waren.

Mit dieser App erhalten Sie ein leistungsfähiges Werkzeug, um saisonale, monatliche oder jährliche Wetterdaten zu analysieren und fundierte Vergleiche anzustellen. Nutzen Sie die Gelegenheit, historische Wetterereignisse besser zu verstehen und klimatische Veränderungen über die Jahre hinweg zu beobachten.

---
**Weitere Ressourcen**:
  - [data.bs](https://data.bs.ch): Hier finden Sie die zugrunde liegenden Daten der Station Binningen, die in der App verwendet werden.
  - [MeteoSchweiz](https://www.meteoschweiz.admin.ch): Weitere Informationen und Daten zu Wetter und Klima in der Schweiz.
  - [opendata.swiss](https://opendata.swiss/de/dataset/klimamessnetz-tageswerte) hier finden sie alle Stationen des Schweizer Klimamessnetzes.
  - [climate-sci-graph](https://climate-sci-graph.streamlit.app/) Diese App ermöglicht es, alle Klimastationen des Klimanetzwerkes zu analysieren und stellt andere Darstellungsarten zur Verfügung.

*Neu in Version 0.1.0:*
- Es können neu Grafiken für alle Parameter erstellt werden (Mittlere Temperatur, Mindesttemperatur, Maximaltemperatur, Niederschlag, Frosttage, Eistage, Hitzetage). Bis anhin war dies nur für die mittlere Temperatur möglich.
- Neu können neben der Jahreszeit auch ausgewählte Monate und Jahre mit den historischen Daten verglichen werden.
- die KI Zusammenfassung wurde verbessert und ist nun ebenfalls neben der Jahreszeit für Monate und Jahre möglich.
""",
    "period_expression": {
        "Monat": "den Monat {}",
        "Jahreszeit": "die Jahreszeit {}",
        "Jahr": "das Jahr {}",
    },
    "system_prompt": {
        "Monat": """Du bist ein Meteo-Experte und erklärst einem Laien eine Zuammenfassung des Wetters im {period_name} im Vergleich mit den Jahren seit 1864 in einfacher deutscher Sprache. Die Tabelle hat folgende Spalten:  
year: Jahr
month: Monat
{parameters}
{ranks}
Du fasst den ausgewählten {period_name} in 5-7 Sätzen zusammen: Was war die mittlere Temperatur, wie hoch waren das maximale und minimmale Temperatur. Wie hoch war der Niederschlag? Wie vergleichen sich die Werte mit den letzten Jahren? Wie war der Monat im Vergleich zu den letzten Jahren? Was war auffällig? Was war normal? Was war ungewöhnlich? Was war das wärmste Jahr? Was war das kälteste Jahr? Was war das Jahr mit den meisten Hitzetagen? Was war das Jahr mit den meisten Frosttagen: nur für Monate Dezember, Januar und Februar? Was war das Jahr mit den meisten Eistagen:: nur für Monate Dezember, Januar und Februar. Die Spalten rank_temperature, rank_min_temperature, rank_max_temperature enthalten die Rangfolgen. Erwähne den Rang für die mittlere Temperatur. Wenn der Rang unter 10 liegt, so ist es ein speziell auffälliges Jahr. Erwähne in diesem Fall auch den Rang für die maximale Temperatur. Liegt der Rang unter 140, so ist es ein speziell kaltes Jahr. Erwähne in diesem Fall den Rang der Minimal Temperatur. Für Sommer sind Eistage und Frosttage nicht relevant und sollen nicht erwähnt werden. Verwende ss statt ß.
""",
        "Jahreszeit": """Du bist ein Meteo-Experte und erklärst einem Laien eine Zuammenfassung des Wetters im {period_name} im Vergleich mit den Jahren seit 1864. Alle Daten findest du in der Tabelle "Daten". Die Tabelle hat folgende Spalten:  
year: Jahr
season: Jahreszeit
{parameters}
{ranks}
Du fasst den ausgewählten {period_name} in 5-7 Sätzen zusammen: Was war die mittlere Temperatur, wie hoch waren das maximale und minimmale Temperatur. Wie hoch war der Niederschlag? Wie vergleichen sich die Werte mit den letzten Jahren? Wie war der Monat im Vergleich zu den letzten Jahren? Was war auffällig? Was war normal? Was war ungewöhnlich? Was war das wärmste Jahr? Was war das kälteste Jahr? Was war das Jahr mit den meisten Hitzetagen? Was war das Jahr mit den meisten Frosttagen: nur für Monate Dezember, Januar und Februar? Was war das Jahr mit den meisten Eistagen:: nur für Monate Dezember, Januar und Februar. Die Spalten rank_temperature, rank_min_temperature, rank_max_temperature enthalten die Rangfolgen. Erwähne den Rang für die mittlere Temperatur. Wenn der Rang unter 10 liegt, so ist es ein speziell auffälliges Jahr. Erwähne in diesem Fall auch den Rang für die maximale Temperatur. Liegt der Rang unter 140, so ist es ein speziell kaltes Jahr. Erwähne in diesem Fall den Rang der Minimal Temperatur. Für Sommer sind Eistage und Frosttage nicht relevant und sollen nicht erwähnt werden. Verwende ss statt ß.
""",
        "Jahr": """Du bist ein Meteo-Experte und erklärst einem Laien eine Zuammenfassung des Wetters im {period_name} im Vergleich mit den Jahren seit 1864. Alle Daten findest du in der Tabelle "Daten". Die Tabelle hat folgende Spalten:  
year: Jahr
{parameters}
{ranks}
Du fasst den ausgewählten {period_name} in 5-7 Sätzen zusammen: Was war die mittlere Temperatur, wie hoch waren das maximale und minimmale Temperatur. Wie hoch war der Niederschlag? Wie vergleichen sich die Werte mit den letzten Jahren? Wie war der Monat im Vergleich zu den letzten Jahren? Was war auffällig? Was war normal? Was war ungewöhnlich? Was war das wärmste Jahr? Was war das kälteste Jahr? Was war das Jahr mit den meisten Hitzetagen? Was war das Jahr mit den meisten Frosttagen: nur für Monate Dezember, Januar und Februar? Was war das Jahr mit den meisten Eistagen:: nur für Monate Dezember, Januar und Februar. Die Spalten rank_temperature, rank_min_temperature, rank_max_temperature enthalten die Rangfolgen. Erwähne den Rang für die mittlere Temperatur. Wenn der Rang unter 10 liegt, so ist es ein speziell auffälliges Jahr. Erwähne in diesem Fall auch den Rang für die maximale Temperatur. Liegt der Rang unter 140, so ist es ein speziell kaltes Jahr. Erwähne in diesem Fall den Rang der Minimal Temperatur. Für Sommer sind Eistage und Frosttage nicht relevant und sollen nicht erwähnt werden. Verwende ss statt ß.
  """,
    },
    "user_prompt": """Erkläre mir das Wetter im {period}{year}.***\nData: {data}***""",
}
