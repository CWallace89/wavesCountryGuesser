import streamlit as st
import unicodedata
from difflib import get_close_matches

st.set_page_config(page_title="Waves Country Game", page_icon="🌊", layout="centered")

# ---------- Data ----------
A = ["Afghanistan","Albania","Algeria","Andorra","Angola","Antigua and Barbuda","Argentina","Armenia","Australia","Austria","Azerbaijan"]
B = ["Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei","Bulgaria","Burkina Faso","Burundi"]
C = ["Cabo Verde","Cambodia","Cameroon","Canada","Central African Republic","Chad","Chile","China","Colombia","Comoros","Congo","Costa Rica","Côte d’Ivoire","Croatia","Cuba","Cyprus","Czechia"]
D = ["Democratic Republic of the Congo","Denmark","Djibouti","Dominica","Dominican Republic"]
E = ["Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Eswatini","Ethiopia"]
F = ["Fiji","Finland","France"]
G = ["Gabon","Gambia","Georgia","Germany","Ghana","Greece","Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana"]
H = ["Haiti","Honduras","Hungary","Holy See"]
I = ["Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy"]
J = ["Jamaica","Japan","Jordan"]
K = ["Kazakhstan","Kenya","Kiribati","Kuwait","Kyrgyzstan"]
L = ["Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg"]
M = ["Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia","Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique","Myanmar"]
N = ["Namibia","Nauru","Nepal","Netherlands","New Zealand","Nicaragua","Niger","Nigeria","North Korea","North Macedonia","Norway"]
O = ["Oman"]
P = ["Pakistan","Palau","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","State of Palestine"]
Q = ["Qatar"]
R = ["Romania","Russia","Rwanda"]
S = ["Saint Kitts and Nevis","Saint Lucia","Saint Vincent and the Grenadines","Samoa","San Marino","São Tomé and Príncipe","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Korea","South Sudan","Spain","Sri Lanka","Sudan","Suriname","Sweden","Switzerland","Syria"]
T = ["Tajikistan","Tanzania","Thailand","Timor-Leste","Togo","Tonga","Trinidad and Tobago","Tunisia","Türkiye","Turkmenistan","Tuvalu"]
U = ["Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","Uruguay","Uzbekistan"]
V = ["Vanuatu","Venezuela","Vietnam"]
W, X = [], []
Y = ["Yemen"]
Z = ["Zambia","Zimbabwe"]

COUNTRIES_BY_LETTER = {k: v for k, v in zip(
    list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    [A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z]
)}

ALIASES = {
    "burma":"Myanmar","cape verde":"Cabo Verde","ivory coast":"Côte d’Ivoire","swaziland":"Eswatini",
    "czech republic":"Czechia","east timor":"Timor-Leste","macedonia":"North Macedonia",
    "lao pdr":"Laos","lao people s democratic republic":"Laos",
    "republic of the congo":"Congo","congo brazzaville":"Congo",
    "dr congo":"Democratic Republic of the Congo","drc":"Democratic Republic of the Congo","congo kinshasa":"Democratic Republic of the Congo",
    "saint kitts nevis":"Saint Kitts and Nevis","st kitts and nevis":"Saint Kitts and Nevis","st kitts":"Saint Kitts and Nevis",
    "st lucia":"Saint Lucia","saint vincent and grenadines":"Saint Vincent and the Grenadines","st vincent":"Saint Vincent and the Grenadines",
    "south korea":"South Korea","north korea":"North Korea","palestine":"State of Palestine",
    "sao tome and principe":"São Tomé and Príncipe","vietnam":"Vietnam","turkey":"Türkiye",
}

# ---------- Helpers ----------
def normalize(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    clean = "".join(ch for ch in s if ch.isalnum() or ch.isspace())
    return " ".join(clean.split())

def canonicalize(guess: str) -> str:
    g = normalize(guess)
    if g in ALIASES:
        return ALIASES[g]
    return " ".join(w.capitalize() for w in g.split())

def close_match(guess: str, remaining: set[str], cutoff=0.84) -> str | None:
    names = list(remaining)
    norm_map = {n: normalize(n) for n in names}
    matches = get_close_matches(normalize(guess), list(norm_map.values()), n=1, cutoff=cutoff)
    if matches:
        for orig, normed in norm_map.items():
            if normed == matches[0]:
                return orig
    return None

# ---------- State init ----------
if "letters" not in st.session_state:
    st.session_state.letters = [l for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if COUNTRIES_BY_LETTER[l]]
    st.session_state.idx = 0
    st.session_state.remaining = set(COUNTRIES_BY_LETTER[st.session_state.letters[0]])
    st.session_state.correct = []
    st.session_state.total_score = 0
    st.session_state.per_letter_scores = {}
    st.session_state.reveal = None           # holds last reveal dict
    st.session_state.phase = "play"          # "play" or "reveal"

def start_letter(idx: int):
    st.session_state.idx = idx
    letter = st.session_state.letters[idx]
    st.session_state.remaining = set(COUNTRIES_BY_LETTER[letter])
    st.session_state.correct = []
    st.session_state.reveal = None
    st.session_state.phase = "play"

def finish_letter():
    letter = st.session_state.letters[st.session_state.idx]
    target = len(COUNTRIES_BY_LETTER[letter])
    got = sorted(st.session_state.correct)
    missed = sorted(st.session_state.remaining)
    score = len(got)
    st.session_state.per_letter_scores[letter] = score
    st.session_state.total_score += score
    st.session_state.reveal = dict(letter=letter, score=score, total=target, got=got, missed=missed)
    st.session_state.phase = "reveal"

# ---------- UI ----------
st.title("🌊 Waves Country Game")
letter = st.session_state.letters[st.session_state.idx]
target_count = len(COUNTRIES_BY_LETTER[letter])

st.subheader(f"Letter: **{letter}**")
st.write(f"You need to guess **{target_count}** countries that start with **{letter}**.")

# Input form (so button presses are one clear event)
with st.form(key=f"form_{st.session_state.idx}"):
    guess = st.text_input("Enter a country (or type Pass)", value="", key=f"guess_{st.session_state.idx}")
    cols = st.columns([1,1,3])
    with cols[0]:
        submitted = st.form_submit_button("Submit")
    with cols[1]:
        passed = st.form_submit_button("Pass")
    # cols[2] is spacer

feedback = st.empty()

if st.session_state.phase == "play":
    if submitted and guess.strip():
        if normalize(guess) in ("pass", "skip"):
            finish_letter()
            st.rerun()
        else:
            canon = canonicalize(guess)
            if canon in st.session_state.remaining:
                st.session_state.correct.append(canon)
                st.session_state.remaining.remove(canon)
                feedback.success(f"✅ Correct: **{canon}**")
            else:
                maybe = close_match(guess, st.session_state.remaining)
                if maybe:
                    feedback.warning(f"🤏 Close! Did you mean **{maybe}**?")
                else:
                    feedback.error(f"❌ Not on the list for **{letter}**.")
            # auto-finish if done
            if not st.session_state.remaining:
                finish_letter()
                st.rerun()
    elif passed:
        finish_letter()
        st.rerun()

# Reveal panel + advance
if st.session_state.phase == "reveal" and st.session_state.reveal:
    r = st.session_state.reveal
    with st.expander(f"Results for {r['letter']}", expanded=True):
        st.write(f"Score: **{r['score']} / {r['total']}**")
        if r["got"]:
            st.write("You got:")
            st.write(", ".join(r["got"]))
        if r["missed"]:
            st.write("Missed:")
            st.write(", ".join(r["missed"]))

    # Next or Game Over
    if st.session_state.idx + 1 < len(st.session_state.letters):
        if st.button("➡️ Next Letter", key=f"next_{st.session_state.idx}"):
            start_letter(st.session_state.idx + 1)
            st.rerun()
    else:
        st.subheader("🏁 Game Over")
        possible_total = sum(len(COUNTRIES_BY_LETTER[l]) for l in st.session_state.letters)
        st.write(f"Your total score: **{st.session_state.total_score} / {possible_total}**")
        if st.button("🔁 Play Again"):
            for k in ("letters","idx","remaining","correct","total_score","per_letter_scores","reveal","phase"):
                del st.session_state[k]
            st.rerun()

# Progress sidebar (now shows whatever has been scored)
with st.sidebar:
    st.markdown("### Progress")
    for l in st.session_state.letters:
        if l in st.session_state.per_letter_scores:
            s = st.session_state.per_letter_scores[l]
            st.write(f"{l}: {s}/{len(COUNTRIES_BY_LETTER[l])}")
