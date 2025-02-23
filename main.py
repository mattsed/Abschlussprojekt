import streamlit as st
import numpy as np
import json
import matplotlib.pyplot as plt

st.title("Mechanismus-Definition und Berechnung (mit automatischem Mittelpunkt c)")

# -------------------------------
# (A) EINGABE DER PUNKTE
# -------------------------------
num_points = st.number_input("Anzahl Gelenkpunkte (ohne Mittelpunkt c):", 
                             min_value=1, value=2, step=1)

points = []
for i in range(num_points):
    x_val = st.number_input(f"X-Koordinate für Punkt {i}", value=0.0, key=f"px_{i}")
    y_val = st.number_input(f"Y-Koordinate für Punkt {i}", value=0.0, key=f"py_{i}")
    points.append((x_val, y_val))

st.write("**Definierte (Benutzer-)Gelenkpunkte:**", points)

# -------------------------------
# (B) AUTOMATISCHER PUNKT c
# -------------------------------
# Beispiel: c = (-30, 0)
# Du kannst natürlich jeden anderen Wert nehmen.
c = (-30.0, 0.0)

# Hänge diesen Punkt c ans Ende der Liste an
c_index = len(points)  # Index des neuen Punkts
points.append(c)       # jetzt ist points = [p0, p1, ..., p_{n-1}, c]

st.write("**Automatisch hinzugefügter Mittelpunkt c:**", c)

# -------------------------------
# (C) AUTOMATISCHE GLIEDER
# -------------------------------
# Hier entscheidest du, wie die Verbindungen gesetzt werden sollen.
# Beispiel: Wir verbinden c mit dem (ersten) Punkt p1 (Index 1).
# Du könntest stattdessen p2 o.ä. nehmen, je nach Bedarf.
auto_links = []
# Verbinde alle Punkte nacheinander: p0 -> p1 -> p2 -> ...
for i in range(num_points - 1):  # Bis num_points-1, weil wir mit i+1 verbinden
    auto_links.append((i, i + 1))  # Verbindung von p[i] zu p[i+1]

# Verbinde Mittelpunkt c mit p1 (falls vorhanden)
if num_points >= 1:
    auto_links.append((c_index, 0))  # Mittelpunkt c -> p1

# -------------------------------
# (D) SPEICHERN IN JSON
# -------------------------------
if st.button("Speichere Einstellungen in JSON"):
    # Du kannst natürlich auch die "normalen" links mit abspeichern,
    # falls du eine UI für weitere Glieder hast.
    # Hier speichern wir nur die auto_links.
    data = {
        "points": points,      # Liste von (x,y)-Tupeln
        "links": auto_links    # automatisch erzeugte Liste
    }
    with open("mechanism.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.success("Einstellungen (inkl. Mittelpunkt c) in 'mechanism.json' gespeichert!")

# -------------------------------
# (E) LADEN AUS JSON UND BERECHNUNG
# -------------------------------
if st.button("Lade Einstellungen aus JSON und führe Berechnung durch"):
    try:
        with open("mechanism.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        loaded_points = data["points"]
        loaded_links  = data["links"]
        
        st.write("**Geladene Punkte:**", loaded_points)
        st.write("**Geladene Glieder:**", loaded_links)

        # 1) Erzeuge den Vektor x = [x0, y0, x1, y1, x2, y2, ..., xc, yc]
        x_list = []
        for (px, py) in loaded_points:
            x_list.extend([px, py])
        x = np.array(x_list, dtype=float)

        n = len(loaded_points)  # Anzahl Punkte
        m = len(loaded_links)   # Anzahl Glieder

        # 2) Baue A-Matrix (2m x 2n)
        A = np.zeros((2*m, 2*n))
        for row_index, (i, j) in enumerate(loaded_links):
            # X-Differenz
            A[2*row_index,   2*i]   = 1
            A[2*row_index,   2*j]   = -1
            # Y-Differenz
            A[2*row_index+1, 2*i+1] = 1
            A[2*row_index+1, 2*j+1] = -1

        # 3) Differenzen berechnen
        l_hat = A @ x
        L = l_hat.reshape(m, 2)
        lengths = np.linalg.norm(L, axis=1)
        
        st.write("**Ermittelte Gliederlängen (Ist):**", lengths)

        # OPTIONAL: Zeichnen zur Veranschaulichung
        fig, ax = plt.subplots()
        # Zeichne alle Punkte
        xs = [p[0] for p in loaded_points]
        ys = [p[1] for p in loaded_points]
        ax.scatter(xs, ys, color='red')
        
        # Beschrifte die Punkte
        for idx, (px, py) in enumerate(loaded_points):
            ax.text(px+0.3, py+0.3, f"p{idx}", color='red')

        # Zeichne die Glieder
        for (i, j) in loaded_links:
            x_coords = [loaded_points[i][0], loaded_points[j][0]]
            y_coords = [loaded_points[i][1], loaded_points[j][1]]
            ax.plot(x_coords, y_coords, color='blue')
        
        # Zeichne einen Kreis um c, falls gewünscht
        # Beispiel: Radius = Abstand c -> p1
        # (Achtung: hier c ist der letzte Punkt in loaded_points)
        if num_points >= 2:
            # c_index ist len(loaded_points)-1
            c_idx = len(loaded_points) 
        
        c_idx = len(loaded_points)
        st.write(f"Index c_idx = {c_idx}")
    
    except FileNotFoundError:
        st.error("Die Datei 'mechanism.json' wurde nicht gefunden.")
    except KeyError as e:
        st.error(f"Fehlender Schlüssel in JSON: {e}")
    except Exception as e:
        st.error(f"Ein unbekannter Fehler ist aufgetreten: {e}")
