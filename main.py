import streamlit as st
import numpy as np
import json
import matplotlib.pyplot as plt
import time

st.title("Strandbeest-Mechanismus Simulation")

# -------------------------------
# (A) Eingabe der Gelenkpunkte
# -------------------------------
num_points = st.number_input("Anzahl Gelenkpunkte (ohne Mittelpunkt c):", 
                             min_value=1, value=4, step=1)

# Session State verwenden, um Werte beizubehalten
if "points" not in st.session_state:
    st.session_state["points"] = [(i * 10, 10.0) for i in range(num_points)]

# Eingabe der Punkte
points = []
for i in range(num_points):
    x_val = st.number_input(f"X-Koordinate für Punkt {i}", value=st.session_state["points"][i][0], key=f"px_{i}")
    y_val = st.number_input(f"Y-Koordinate für Punkt {i}", value=st.session_state["points"][i][1], key=f"py_{i}")
    points.append((x_val, y_val))

st.session_state["points"] = points

# -------------------------------
# (B) Automatischer Mittelpunkt c (fixiert)
# -------------------------------
c = (-30.0, 0.0)
c_index = len(points)
points.append(c)

st.write("**Automatisch hinzugefügter Mittelpunkt c:**", c)

# -------------------------------
# (C) Automatische Verbindungen (Glieder)
# -------------------------------
auto_links = [(c_index, 0)]  # Verbindung von c zu p0

# Automatische Verbindung aller Punkte mit dem vorherigen Punkt
for i in range(num_points - 1):
    auto_links.append((i, i + 1))

# -------------------------------
# (D) Speicherung in JSON
# -------------------------------
if st.button("Speichere Einstellungen in JSON"):
    data = {
        "points": points,
        "links": auto_links
    }
    with open("mechanism.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.success("Einstellungen gespeichert!")

# -------------------------------
# (E) Laden & Berechnung
# -------------------------------
if st.button("Lade Einstellungen aus JSON"):
    try:
        with open("mechanism.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        st.session_state["loaded_points"] = data["points"]
        st.session_state["loaded_links"] = data["links"]
        st.success("Daten erfolgreich geladen!")

    except FileNotFoundError:
        st.error("Die Datei 'mechanism.json' wurde nicht gefunden.")
    except KeyError as e:
        st.error(f"Fehlender Schlüssel in JSON: {e}")
    except Exception as e:
        st.error(f"Ein unbekannter Fehler ist aufgetreten: {e}")

# beenden falls keine Punkte geladen sind
if "loaded_points" not in st.session_state:
    st.stop()

loaded_points = st.session_state["loaded_points"]
loaded_links = st.session_state["loaded_links"]

# -------------------------------
# (F) Simulation der Bewegung
# -------------------------------
step_size = st.slider("Schrittweite des Winkels (Grad)", 1, 10, 2)

if "theta" not in st.session_state:
    st.session_state["theta"] = 0

# Knopf für Animation → Setzt `animation_running` in Session State
if st.button("Animation starten"):
    st.session_state["animation_running"] = not st.session_state.get("animation_running", False)

# Live-Update
plot_placeholder = st.empty()

while st.session_state.get("animation_running", False):
    st.session_state["theta"] += np.radians(step_size)

    fig, ax = plt.subplots()

    # p0 bewegt sich auf der Kreisbahn um c
    r_p0 = np.linalg.norm(np.array(loaded_points[0]) - np.array(c))
    p0_x = c[0] + r_p0 * np.cos(st.session_state["theta"])
    p0_y = c[1] + r_p0 * np.sin(st.session_state["theta"])
    loaded_points[0] = (p0_x, p0_y)

    # Punkte zeichnen
    xs = [p[0] for p in loaded_points]
    ys = [p[1] for p in loaded_points]
    ax.scatter(xs, ys, color='red')

    for idx, (px, py) in enumerate(loaded_points):
        ax.text(px + 0.3, py + 0.3, f"p{idx}", color='red')

    # Glieder zeichnen
    for (i, j) in loaded_links:
        ax.plot([loaded_points[i][0], loaded_points[j][0]],
                [loaded_points[i][1], loaded_points[j][1]], color='blue')

    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    ax.set_xlabel("X-Koordinate")
    ax.set_ylabel("Y-Koordinate")
    ax.set_title(f"Mechanismus - Winkel: {np.degrees(st.session_state['theta']):.1f}°")

    # **Live-Update über Streamlit**
    plot_placeholder.pyplot(fig)

    # **Verzögerung für Animation**
    time.sleep(0.1)
