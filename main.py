import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import json

# ---------------------------------------------------------------
# (A) Hilfsklasse: Punkt
# ---------------------------------------------------------------
class Point:
    """ Klasse für einen Punkt mit Koordinaten. """
    def __init__(self, x, y, name=""):
        self.x = x
        self.y = y
        self.name = name

    def position(self):
        """ Gibt die aktuelle Position als Tupel zurück """
        return (self.x, self.y)

    def move_to(self, x, y):
        """ Setzt den Punkt auf neue Koordinaten """
        self.x = x
        self.y = y

# ---------------------------------------------------------------
# (B) Hilfsklasse: Link (Verbindungsstück mit fixer Länge)
# ---------------------------------------------------------------
class Link:
    """ Verbindet zwei Punkte mit fixer Länge """
    def __init__(self, point1, point2):
        self.p1 = point1
        self.p2 = point2
        self.length = np.linalg.norm(np.array(self.p2.position()) - np.array(self.p1.position()))

    def enforce_length(self):
        """ Erzwingt die konstante Länge des Links """
        vec = np.array(self.p2.position()) - np.array(self.p1.position())
        if np.linalg.norm(vec) == 0:
            return
        unit_vec = vec / np.linalg.norm(vec)
        new_pos = np.array(self.p1.position()) + self.length * unit_vec
        self.p2.move_to(*new_pos)

# ---------------------------------------------------------------
# (C) Hauptklasse: Mechanismus
# ---------------------------------------------------------------
class Mechanism:
    """ Klasse für den Mechanismus mit Punkten, Links und Animation """
    def __init__(self, c, p0, p1, p2):
        self.c = c  # Fixpunkt
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.links = [
            Link(c, p0),  # c -> p0
            Link(p0, p1),  # p0 -> p1
            Link(p1, p2)   # p1 -> p2
        ]
        self.theta = 0.0

    def update_mechanism(self, step_size, coupler="p1"):
        """ Aktualisiert p0 durch Rotation um c und berechnet Coupler-Position """
        self.theta += np.radians(step_size)

        # (1) p0 bewegt sich auf einer Kreisbahn um c
        r = self.links[0].length  # Radius von c->p0 bleibt konstant
        new_p0_x = self.c.x + r * np.cos(self.theta)
        new_p0_y = self.c.y + r * np.sin(self.theta)
        self.p0.move_to(new_p0_x, new_p0_y)

        # (2) Berechne den Coupler (entweder p1 oder p2)
        if coupler == "p1":
            # p1 muss sich auf einer Bahn bewegen -> Fixiere p2
            self.p1.move_to(*circle_intersection(self.p0.position(), self.links[1].length,
                                                 self.p2.position(), self.links[2].length))
        else:
            # p2 muss sich auf einer Bahn bewegen -> Fixiere p1
            self.p2.move_to(*circle_intersection(self.p1.position(), self.links[2].length,
                                                 self.p0.position(), self.links[1].length))

        # (3) Erzwinge alle Längenbeschränkungen
        for link in self.links:
            link.enforce_length()

# ---------------------------------------------------------------
# (D) Hilfsfunktion: Schnitt zweier Kreise (Coupler-Berechnung)
# ---------------------------------------------------------------
def circle_intersection(centerA, rA, centerB, rB, pick_upper=True):
    """ Berechnet den Schnittpunkt zweier Kreise """
    A = np.array(centerA, dtype=float)
    B = np.array(centerB, dtype=float)
    d = np.linalg.norm(B - A)
    if d > rA + rB or d < abs(rA - rB):
        return None

    a = (rA**2 - rB**2 + d**2) / (2 * d)
    h = np.sqrt(max(rA**2 - a**2, 0.0))
    M = A + a * (B - A) / d
    dir_vec = (B - A) / d
    perp_vec = np.array([-dir_vec[1], dir_vec[0]])

    p_int_1 = M + h * perp_vec
    p_int_2 = M - h * perp_vec

    return p_int_1 if pick_upper else p_int_2

# ---------------------------------------------------------------------
# UI Titel
# ---------------------------------------------------------------------
st.title("Fixe Gliederlängen: p0 rotiert um c, Coupler auf gekrümmter Bahn")

# ---------------------------------------------------------------------
# (A) Eingabe: Punkte c (fix), p2 (fix), p0, p1
# ---------------------------------------------------------------------
st.subheader("1) Punkteingabe")

# Fixe Punkte c und p2 (z. B. vom Nutzer definierbar)
cx = st.number_input("c.x (fix)", value=-30.0)
cy = st.number_input("c.y (fix)", value=0.0)
c = (cx, cy)

p2x = st.number_input("p2.x (fix)", value=0.0)
p2y = st.number_input("p2.y (fix)", value=0.0)
p2 = (p2x, p2y)

# Bewegliche Punkte p0, p1 (Anfangskoordinaten)
p0x = st.number_input("p0.x (Start)", value=-15.0)
p0y = st.number_input("p0.y (Start)", value=10.0)
p0_start = (p0x, p0y)

p1x = st.number_input("p1.x (Start)", value=-10.0)
p1y = st.number_input("p1.y (Start)", value=30.0)
p1_start = (p1x, p1y)

# ---------------------------------------------------------------------
# (B) Gliederlängen aus Anfangspositionen
# ---------------------------------------------------------------------
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
st.subheader("4) Animation/Steuerung")
step_size = st.slider("Schrittweite (Grad pro Frame)", 1, 20, 5)
if "theta" not in st.session_state:
    st.session_state.theta = 0.0
if "running" not in st.session_state:
    st.session_state.running = False

if st.button("Animation starten/stoppen"):
    st.session_state.running = not st.session_state.running

# ---------------------------------------------------------------------
# (E) JSON Speichern/Laden (optional)
# ---------------------------------------------------------------------
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
    mechanism.update_mechanism(step_size, coupler_choice)

    fig, ax = plt.subplots()
    points = [c, p0, p1, p2]
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    
    ax.scatter(xs, ys, color="red")
    for p in points:
        ax.text(p.x + 0.3, p.y + 0.3, p.name, color="red")

    for link in mechanism.links:
        ax.plot([link.p1.x, link.p2.x], [link.p1.y, link.p2.y], color="blue", lw=2)
        
    ax.set_aspect("equal")
    ax.set_xlim(-60, 60)
    ax.set_ylim(-30, 60)
    plot_placeholder.pyplot(fig)

    time.sleep(0.1)