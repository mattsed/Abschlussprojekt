import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import json

# ---------------------------------------------------------------------
# Hilfsfunktion: Schnitt zweier Kreise (exakte Geometrie)
# ---------------------------------------------------------------------
def circle_intersection(centerA, rA, centerB, rB, pick_upper=True):
    """
    Liefert (x,y) für den Schnittpunkt der beiden Kreise.
    pick_upper=True wählt den 'oberen' Schnittpunkt (wenn es zwei gibt).
    Gibt None zurück, falls kein Schnitt möglich.
    """
    A = np.array(centerA, dtype=float)
    B = np.array(centerB, dtype=float)
    d = np.linalg.norm(B - A)
    if d > rA + rB or d < abs(rA - rB):
        # Keine oder zu große Überlappung
        return None

    # Formeln (klassische Kreisgeometrie)
    a = (rA**2 - rB**2 + d**2) / (2 * d)
    h = np.sqrt(max(rA**2 - a**2, 0.0))

    M = A + a * (B - A) / d  # Mittelpunkt der Schnittlinie
    # Senkrecht auf (B-A):
    dir_vec = (B - A) / d
    perp_vec = np.array([-dir_vec[1], dir_vec[0]])

    p_int_1 = M + h * perp_vec
    p_int_2 = M - h * perp_vec

    if pick_upper:
        return p_int_1 if p_int_1[1] > p_int_2[1] else p_int_2
    else:
        return p_int_1 if p_int_1[1] < p_int_2[1] else p_int_2

# ---------------------------------------------------------------------
# UI Titel
# ---------------------------------------------------------------------
st.set_page_config(layout="wide")
st.title("Mechanismus")

# ---------------------------------------------------------------------
# (A) Eingabe: Punkte c (fix), p2 (fix), p0, p1
# ---------------------------------------------------------------------

# Fixe Punkte c und p2 (z. B. vom Nutzer definierbar)
with st.sidebar:
    st.subheader("1) Punkteingabe")

    with st.expander("Mittelpunkt c"):
        cx = st.number_input("X-Koordinate", value=-30.0, step=0.5, key="cx", format="%.2f")
        cy = st.number_input("Y-Koordinate", value=0.0, step=0.5, key="cy", format="%.2f")
        c = (cx, cy)
    with st.expander("Fixpunkt p2"):
        p2x = st.number_input("X-Koordinate", value=0.0, step=0.5, key="p2x", format="%.2f")
        p2y = st.number_input("Y-Koordinate", value=0.0, step=0.5, key="p2y", format="%.2f")
        p2 = (p2x, p2y)
    with st.expander("Startpunkt p0"):
        p0x = st.number_input("X-Koordinate", value=-15.0, step=0.5, key="p0x", format="%.2f")
        p0y = st.number_input("Y-Koordinate", value=10.0, step=0.5, key="p0y", format="%.2f")
        p0_start = (p0x, p0y)
    with st.expander("Startpunkt p1"):
        p1x = st.number_input("X-Koordinate", value=-10.0, step=0.5, key="p1x", format="%.2f")
        p1y = st.number_input("Y-Koordinate", value=30.0, step=0.5, key="p1y", format="%.2f")
        p1_start = (p1x, p1y)

  


# ---------------------------------------------------------------------
# (B) Gliederlängen aus Anfangspositionen
# ---------------------------------------------------------------------
with st.sidebar:
    st.subheader("2) Gliederlängen (aus Startposition)")

    # 1) c -> p0
    L_c_p0 = np.linalg.norm(np.array(p0_start) - np.array(c))
    # 2) p0 -> p1
    L_p0_p1 = np.linalg.norm(np.array(p1_start) - np.array(p0_start))
    # 3) p1 -> p2
    L_p1_p2 = np.linalg.norm(np.array(p1_start) - np.array(p2))

    st.write(f"Länge c->p0 = {L_c_p0:.3f}")
    st.write(f"Länge p0->p1 = {L_p0_p1:.3f}")
    st.write(f"Länge p1->p2 = {L_p1_p2:.3f}")

# ---------------------------------------------------------------------
# (C) Coupler-Auswahl
# ---------------------------------------------------------------------
with st.sidebar:
    st.subheader("3) Coupler-Auswahl")
    coupler_options = ["p1", "p2"]
    coupler_choice = st.selectbox("Welcher Punkt soll der 'Coupler' sein? (p2 bleibt sonst fix)", coupler_options)
    # Wenn coupler_choice = "p1", dann wird p1 per Kreis-Schnitt bestimmt, p2 bleibt fix
    # Wenn coupler_choice = "p2", dann wird p2 per Kreis-Schnitt bestimmt, p1 bleibt fix

    # Um oben/unten Schnitt zu wählen
    pick_upper = st.checkbox("Oberen Schnittpunkt wählen?", value=True)

# ---------------------------------------------------------------------
# (D) Winkelsteuerung: p0 rotiert um c
# ---------------------------------------------------------------------
with st.sidebar:
    st.subheader("4) Animation/Steuerung")
    step_size = st.slider("Schrittweite (Grad pro Frame)", 1, 20, 5)
if "theta" not in st.session_state:
    st.session_state.theta = 0.0
if "running" not in st.session_state:
    st.session_state.running = False
with st.sidebar:
    if st.button("Animation starten/stoppen"):
        st.session_state.running = not st.session_state.running

# ---------------------------------------------------------------------
# (E) JSON Speichern/Laden (optional)
# ---------------------------------------------------------------------
with st.sidebar:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Speichere Einstellungen in JSON"):
            data = {
                "c": c,
                "p2": p2,
                "p0_start": p0_start,
                "p1_start": p1_start,
                "L_c_p0": L_c_p0,
                "L_p0_p1": L_p0_p1,
                "L_p1_p2": L_p1_p2,
                "coupler_choice": coupler_choice,
                "pick_upper": pick_upper,
                "step_size": step_size,
                "theta": st.session_state.theta
            }
            with open("mechanism.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            st.success("Einstellungen gespeichert: mechanism.json")

    with col2:
        if st.button("Lade Einstellungen aus JSON"):
            try:
                with open("mechanism.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Lade die Werte in Session State
                st.session_state.theta = data["theta"]
                st.session_state.running = False
                # Keine automatische UI-Updates für Input-Felder in Streamlit,
                # man könnte st.experimental_rerun() aufrufen oder 
                # einen Trick mit st.session_state[...] Key-Bindings machen.
                st.success("Einstellungen geladen! (UI-Eingaben evtl. neu setzen)")
            except FileNotFoundError:
                st.error("mechanism.json nicht gefunden.")
            except Exception as e:
                st.error(f"Fehler beim Laden: {e}")

# ---------------------------------------------------------------------
# (F) Animation: exakte Kreis-Schnitt-Berechnung
# ---------------------------------------------------------------------

plot_placeholder = st.empty()

while st.session_state.running:
    st.session_state.theta += np.radians(step_size)
    theta = st.session_state.theta

    # 1) p0(t): rotiert um c
    p0x_t = c[0] + L_c_p0 * np.cos(theta)
    p0y_t = c[1] + L_c_p0 * np.sin(theta)
    p0_t = np.array([p0x_t, p0y_t])

    if coupler_choice == "p1":
        # -> p2 fix
        # p1 = Schnitt Kreis A (Mitte p0_t, Radius L_p0_p1)
        #              Kreis B (Mitte p2,   Radius L_p1_p2)
        p1_sol = circle_intersection(p0_t, L_p0_p1, p2, L_p1_p2, pick_upper=pick_upper)
        if p1_sol is None:
            # kein Schnitt -> Abbruch oder Überspringen
            p1_sol = np.array([-999, -999])  # Dummy
        p1_t = p1_sol
        p2_t = np.array(p2)  # fix
    else:
        # coupler_choice == "p2" -> p1 fix
        # p2 = Schnitt Kreis A (Mitte p1_start, Radius L_p1_p2)
        #              Kreis B (Mitte p0_t,     Radius L_p0_p1)
        # Achtung: Hier "p1_start" fix. (Du könntest auch "p1_start" = p1, 
        # falls p1 anfangs fix sein soll.)
        p1_t = np.array(p1_start)  # fix
        p2_sol = circle_intersection(p0_t, L_p0_p1, p1_t, L_p1_p2, pick_upper=pick_upper)
        if p2_sol is None:
            p2_sol = np.array([-999, -999])
        p2_t = p2_sol

    # Plot
    fig, ax = plt.subplots()
    # c, p0_t, p1_t, p2_t
    ax.scatter([c[0]], [c[1]], color="green")
    ax.text(c[0]+0.2, c[1], "c", color="green")

    ax.scatter([p0_t[0]], [p0_t[1]], color="red")
    ax.text(p0_t[0]+0.2, p0_t[1], "p0", color="red")

    ax.scatter([p1_t[0]], [p1_t[1]], color="red")
    ax.text(p1_t[0]+0.2, p1_t[1], "p1", color="red")

    ax.scatter([p2_t[0]], [p2_t[1]], color="red")
    ax.text(p2_t[0]+0.2, p2_t[1], "p2", color="red")

    # Verbindungen
    # c->p0
    ax.plot([c[0], p0_t[0]], [c[1], p0_t[1]], color="blue", lw=2)
    # p0->p1
    ax.plot([p0_t[0], p1_t[0]], [p0_t[1], p1_t[1]], color="blue", lw=2)
    # p1->p2
    ax.plot([p1_t[0], p2_t[0]], [p1_t[1], p2_t[1]], color="blue", lw=2)

    # Ggf. Kontrollkreise einzeichnen (optional)
    # Kreis um c
    circ_c = plt.Circle(c, L_c_p0, fill=False, color="gray", ls="--")
    ax.add_patch(circ_c)

    # Achsen
    ax.set_aspect("equal", "box")
    ax.set_xlim(-60, 60)
    ax.set_ylim(-30, 60)
    ax.set_title(f"Winkel: {np.degrees(theta):.1f}°, Coupler: {coupler_choice}")
    plot_placeholder.pyplot(fig)

    time.sleep(0.1)