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
H = ["Haiti","Honduras","Hungary"]
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
V = ["Vanuatu","Vatican","Venezuela","Vietnam"]
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
    "holy see":"Vatican",
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

# ---------- State ----------
if "letters" not in st.session_state:
    st.session_state.letters = [l for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if COUNTRIES_BY_LETTER[l]]
    st.session_state.current_letter = st.session_state.letters[0]
    st.session_state.correct_by_letter = {l: [] for l in st.session_state.letters}
    st.session_state.remaining_by_letter = {l: set(COUNTRIES_BY_LETTER[l]) for l in st.session_state.letters}
    st.session_state.phase_by_letter = {l: "play" for l in st.session_state.letters}  # "play" or "reveal"
    st.session_state.reveal_by_letter = {l: None for l in st.session_state.letters}
    st.session_state.per_letter_scores = {l: None for l in st.session_state.letters}  # None until finished
    # completion_type: "perfect" (all guessed), "gaveup" (clicked Give up), or None
    st.session_state.completion_type = {l: None for l in st.session_state.letters}

def finish_letter(letter: str):
    """Finalize a letter and show reveal (called by auto-finish or Give up)."""
    target = len(COUNTRIES_BY_LETTER[letter])
    got = sorted(st.session_state.correct_by_letter[letter])
    missed = sorted(st.session_state.remaining_by_letter[letter])
    score = len(got)
    st.session_state.per_letter_scores[letter] = score
    st.session_state.reveal_by_letter[letter] = dict(letter=letter, score=score, total=target, got=got, missed=missed)
    st.session_state.phase_by_letter[letter] = "reveal"

def unfinished_letters():
    return [l for l, s in st.session_state.per_letter_scores.items() if s is None]

def set_current_letter(ltr: str):
    st.session_state.current_letter = ltr

# ---------- UI: Global styles for two-line buttons ----------
st.markdown("""
<style>
/* Make all letter buttons two-line and uniform */
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {
    height: 3.5em !important;
    font-size: 1rem !important;
    line-height: 1.2em !important;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    white-space: pre-line !important;   /* render \\n as line breaks */
    text-align: center;
}

/* Completed variants */
div[data-testid="stButton"] button.completed {
    background-color: #34a85322 !important; /* soft green */
    color: #2e7d32 !important;
    border: 1px solid #34a85355 !important;
    opacity: 0.98 !important;
}
div[data-testid="stButton"] button.gaveup {
    background-color: #ffb74d33 !important; /* soft orange */
    color: #e65100 !important;
    border: 1px solid #ffb74d77 !important;
    opacity: 0.98 !important;
}

/* Optional: hover for active (unfinished) buttons */
div[data-testid="stButton"] button:not(.completed):not(.gaveup):not(:disabled):hover {
    box-shadow: 0 0 0 2px #1a73e8 inset !important;  /* subtle blue focus */
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.title("🌊 Waves Country Game")

# ---------- Letter Navigation: grid of buttons (green/orange for finished) ----------
st.markdown("**Choose a letter**")
letters = st.session_state.letters
cols_per_row = 9
rows = (len(letters) + cols_per_row - 1) // cols_per_row

for r in range(rows):
    cols = st.columns(cols_per_row)
    for c in range(cols_per_row):
        i = r * cols_per_row + c
        if i >= len(letters):
            continue
        ltr = letters[i]
        finalized = st.session_state.per_letter_scores[ltr] is not None
        live = (st.session_state.per_letter_scores[ltr]
                if finalized else len(st.session_state.correct_by_letter[ltr]))
        total = len(COUNTRIES_BY_LETTER[ltr])

        # Two-line label
        if finalized:
            comp_type = st.session_state.completion_type[ltr]
            if comp_type == "perfect":
                icon = "✅"
                css_class = "completed"
            else:
                icon = "🟠"
                css_class = "gaveup"
            label = f"{icon} {ltr}\n{live}/{total}"
            # Render a styled disabled button via HTML to apply class
            cols[c].markdown(
                f"""
                <button class="{css_class}" disabled
                    style="height:3.5em;width:100%;font-size:1rem;line-height:1.2em;
                           display:flex;flex-direction:column;justify-content:center;align-items:center;
                           white-space:pre-line;text-align:center;">
                    {label}
                </button>
                """,
                unsafe_allow_html=True
            )
        else:
            label = f"{ltr}\n{live}/{total}"
            if cols[c].button(label, key=f"nav_{ltr}", use_container_width=True):
                set_current_letter(ltr)

# If current letter is somehow finalized, auto-advance focus to first unfinished (or finish game)
if st.session_state.per_letter_scores.get(st.session_state.current_letter) is not None:
    u = unfinished_letters()
    if u:
        st.session_state.current_letter = u[0]
    else:
        st.subheader("🏁 Game Complete")
        possible_total = sum(len(COUNTRIES_BY_LETTER[l]) for l in st.session_state.letters)
        final_total = sum(st.session_state.per_letter_scores.values())
        st.write(f"Your final score: **{final_total} / {possible_total}**")
        if st.button("🔁 Play Again"):
            for key in ("letters","current_letter","correct_by_letter","remaining_by_letter",
                        "phase_by_letter","reveal_by_letter","per_letter_scores","completion_type"):
                del st.session_state[key]
            st.rerun()
        st.stop()

# ---------- Current Letter Panel ----------
letter = st.session_state.current_letter
target_count = len(COUNTRIES_BY_LETTER[letter])
remaining = st.session_state.remaining_by_letter[letter]
correct = st.session_state.correct_by_letter[letter]

st.subheader(f"Letter: **{letter}**")
st.write(f"You need to guess countries that start with **{letter}** — **{len(remaining)} remaining** out of **{target_count}**.")

# Input form
with st.form(key=f"form_{letter}"):
    guess = st.text_input("Enter a country (or type Pass/Skip)", value="", key=f"guess_{letter}")
    c1, c2, _ = st.columns([1,1,3])
    with c1:
        submitted = st.form_submit_button("Submit")
    with c2:
        gave_up = st.form_submit_button("Give up")

feedback = st.empty()

# Gameplay
if st.session_state.phase_by_letter[letter] == "play":
    if submitted and guess.strip():
        if normalize(guess) in ("pass", "skip"):
            st.session_state.completion_type[letter] = "gaveup"
            finish_letter(letter)
            st.rerun()
        else:
            canon = canonicalize(guess)
            if canon in remaining:
                correct.append(canon)
                remaining.remove(canon)
                feedback.success(f"✅ Correct: **{canon}**")

                # NEW: force a re-render so the top button grid shows the updated count immediately
                if remaining:           # only rerun if not auto-finishing
                    st.rerun()

            else:
                maybe = close_match(guess, remaining)
                if maybe:
                    feedback.warning(f"🤏 Close! Did you mean **{maybe}**?")
                else:
                    feedback.error(f"❌ Not on the list for **{letter}**.")

            # AUTO-FINISH if all guessed (mark as perfect)
            if not remaining:
                st.session_state.completion_type[letter] = "perfect"
                finish_letter(letter)
                st.rerun()

    elif gave_up:
        st.session_state.completion_type[letter] = "gaveup"
        finish_letter(letter)
        st.rerun()


# Live list of correct guesses
with st.expander("✅ Correct so far", expanded=True):
    if correct:
        st.write(", ".join(sorted(correct)))
    else:
        st.write("_None yet — keep going!_")

# Reveal panel for current letter
if st.session_state.phase_by_letter[letter] == "reveal" and st.session_state.reveal_by_letter[letter]:
    r = st.session_state.reveal_by_letter[letter]
    with st.expander(f"Results for {r['letter']}", expanded=True):
        st.write(f"Score: **{r['score']} / {r['total']}**")
        if r["got"]:
            st.write("You got:")
            st.write(", ".join(r["got"]))
        if r["missed"]:
            st.write("Missed:")
            st.write(", ".join(r["missed"]))

# ---------- Running total (includes unfinished letters) ----------
possible_total = sum(len(COUNTRIES_BY_LETTER[l]) for l in st.session_state.letters)
live_total = 0
for l in st.session_state.letters:
    finalized = st.session_state.per_letter_scores[l]
    if finalized is not None:
        live_total += finalized
    else:
        live_total += len(st.session_state.correct_by_letter[l])

final_cols = st.columns([2,1])
with final_cols[0]:
    finalized_count = sum(1 for s in st.session_state.per_letter_scores.values() if s is not None)
    st.markdown(
        f"**Correct Guesses:** {live_total} / {possible_total}    "
        f"·   Complete Letters: {finalized_count}/{len(st.session_state.letters)}"
    )
with final_cols[1]:
    st.markdown("Green ✅ = completed perfectly  \nOrange 🟠 = gave up")


# ---------- Sidebar: progress ----------
with st.sidebar:
    st.markdown("### Progress")
    for l in st.session_state.letters:
        live = (st.session_state.per_letter_scores[l]
                if st.session_state.per_letter_scores[l] is not None
                else len(st.session_state.correct_by_letter[l]))
        total = len(COUNTRIES_BY_LETTER[l])
        tag = st.session_state.completion_type[l]
        status = "✅" if tag == "perfect" else ("🟠" if tag == "gaveup" else "")
        st.write(f"{status} {l}: {live}/{total}")

    st.markdown("---")
    if st.button("🔁 Reset Game"):
        for key in ("letters","current_letter","correct_by_letter","remaining_by_letter",
                    "phase_by_letter","reveal_by_letter","per_letter_scores","completion_type"):
            del st.session_state[key]
        st.rerun()
