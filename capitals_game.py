# app.py
import streamlit as st
import unicodedata
import random
import time
from difflib import get_close_matches

st.set_page_config(page_title="Capitals Quiz", page_icon="🧭")

# =========================================================
# Data: Country | Capital | Continent
# (compact list; add/remove items as you like)
# =========================================================
RAW = """
Afghanistan|Kabul|Asia
Albania|Tirana|Europe
Algeria|Algiers|Africa
Andorra|Andorra la Vella|Europe
Angola|Luanda|Africa
Antigua and Barbuda|Saint John's|North America
Argentina|Buenos Aires|South America
Armenia|Yerevan|Asia
Australia|Canberra|Oceania
Austria|Vienna|Europe
Azerbaijan|Baku|Asia
Bahamas|Nassau|North America
Bahrain|Manama|Asia
Bangladesh|Dhaka|Asia
Barbados|Bridgetown|North America
Belarus|Minsk|Europe
Belgium|Brussels|Europe
Belize|Belmopan|North America
Benin|Porto-Novo|Africa
Bhutan|Thimphu|Asia
Bolivia|Sucre|South America
Bosnia and Herzegovina|Sarajevo|Europe
Botswana|Gaborone|Africa
Brazil|Brasília|South America
Brunei|Bandar Seri Begawan|Asia
Bulgaria|Sofia|Europe
Burkina Faso|Ouagadougou|Africa
Burundi|Gitega|Africa
Cabo Verde|Praia|Africa
Cambodia|Phnom Penh|Asia
Cameroon|Yaoundé|Africa
Canada|Ottawa|North America
Central African Republic|Bangui|Africa
Chad|N'Djamena|Africa
Chile|Santiago|South America
China|Beijing|Asia
Colombia|Bogotá|South America
Comoros|Moroni|Africa
Congo (Republic of the)|Brazzaville|Africa
Congo (Democratic Republic)|Kinshasa|Africa
Costa Rica|San José|North America
Côte d'Ivoire|Yamoussoukro|Africa
Croatia|Zagreb|Europe
Cuba|Havana|North America
Cyprus|Nicosia|Asia
Czechia|Prague|Europe
Denmark|Copenhagen|Europe
Djibouti|Djibouti|Africa
Dominica|Roseau|North America
Dominican Republic|Santo Domingo|North America
Ecuador|Quito|South America
Egypt|Cairo|Africa
El Salvador|San Salvador|North America
Equatorial Guinea|Malabo|Africa
Eritrea|Asmara|Africa
Estonia|Tallinn|Europe
Eswatini|Mbabane|Africa
Ethiopia|Addis Ababa|Africa
Fiji|Suva|Oceania
Finland|Helsinki|Europe
France|Paris|Europe
Gabon|Libreville|Africa
Gambia|Banjul|Africa
Georgia|Tbilisi|Asia
Germany|Berlin|Europe
Ghana|Accra|Africa
Greece|Athens|Europe
Grenada|St. George's|North America
Guatemala|Guatemala City|North America
Guinea|Conakry|Africa
Guinea-Bissau|Bissau|Africa
Guyana|Georgetown|South America
Haiti|Port-au-Prince|North America
Honduras|Tegucigalpa|North America
Hungary|Budapest|Europe
Iceland|Reykjavík|Europe
India|New Delhi|Asia
Indonesia|Jakarta|Asia
Iran|Tehran|Asia
Iraq|Baghdad|Asia
Ireland|Dublin|Europe
Israel|Jerusalem|Asia
Italy|Rome|Europe
Jamaica|Kingston|North America
Japan|Tokyo|Asia
Jordan|Amman|Asia
Kazakhstan|Astana|Asia
Kenya|Nairobi|Africa
Kiribati|Tarawa|Oceania
Kuwait|Kuwait City|Asia
Kyrgyzstan|Bishkek|Asia
Laos|Vientiane|Asia
Latvia|Riga|Europe
Lebanon|Beirut|Asia
Lesotho|Maseru|Africa
Liberia|Monrovia|Africa
Libya|Tripoli|Africa
Liechtenstein|Vaduz|Europe
Lithuania|Vilnius|Europe
Luxembourg|Luxembourg|Europe
Madagascar|Antananarivo|Africa
Malawi|Lilongwe|Africa
Malaysia|Kuala Lumpur|Asia
Maldives|Malé|Asia
Mali|Bamako|Africa
Malta|Valletta|Europe
Marshall Islands|Majuro|Oceania
Mauritania|Nouakchott|Africa
Mauritius|Port Louis|Africa
Mexico|Mexico City|North America
Micronesia|Palikir|Oceania
Moldova|Chișinău|Europe
Monaco|Monaco|Europe
Mongolia|Ulaanbaatar|Asia
Montenegro|Podgorica|Europe
Morocco|Rabat|Africa
Mozambique|Maputo|Africa
Myanmar|Naypyidaw|Asia
Namibia|Windhoek|Africa
Nauru|Yaren|Oceania
Nepal|Kathmandu|Asia
Netherlands|Amsterdam|Europe
New Zealand|Wellington|Oceania
Nicaragua|Managua|North America
Niger|Niamey|Africa
Nigeria|Abuja|Africa
North Korea|Pyongyang|Asia
North Macedonia|Skopje|Europe
Norway|Oslo|Europe
Oman|Muscat|Asia
Pakistan|Islamabad|Asia
Palau|Ngerulmud|Oceania
Panama|Panama City|North America
Papua New Guinea|Port Moresby|Oceania
Paraguay|Asunción|South America
Peru|Lima|South America
Philippines|Manila|Asia
Poland|Warsaw|Europe
Portugal|Lisbon|Europe
Qatar|Doha|Asia
Romania|Bucharest|Europe
Russia|Moscow|Europe
Rwanda|Kigali|Africa
Saint Kitts|Basseterre|North America
Saint Lucia|Castries|North America
Saint Vincent|Kingstown|North America
Samoa|Apia|Oceania
San Marino|San Marino|Europe
Sao Tome and Príncipe|Sao Tome|Africa
Saudi Arabia|Riyadh|Asia
Senegal|Dakar|Africa
Serbia|Belgrade|Europe
Seychelles|Victoria|Africa
Sierra Leone|Freetown|Africa
Singapore|Singapore|Asia
Slovakia|Bratislava|Europe
Slovenia|Ljubljana|Europe
Solomon Islands|Honiara|Oceania
Somalia|Mogadishu|Africa
South Africa|Pretoria|Africa
South Korea|Seoul|Asia
South Sudan|Juba|Africa
Spain|Madrid|Europe
Sri Lanka|Kotte|Asia
Sudan|Khartoum|Africa
Suriname|Paramaribo|South America
Sweden|Stockholm|Europe
Switzerland|Bern|Europe
Syria|Damascus|Asia
Tajikistan|Dushanbe|Asia
Tanzania|Dodoma|Africa
Thailand|Bangkok|Asia
Timor-Leste|Dili|Asia
Togo|Lomé|Africa
Tonga|Nuku'alofa|Oceania
Trinidad and Tobago|Port of Spain|North America
Tunisia|Tunis|Africa
Türkiye|Ankara|Asia
Turkmenistan|Ashgabat|Asia
Tuvalu|Funafuti|Oceania
Uganda|Kampala|Africa
Ukraine|Kyiv|Europe
United Arab Emirates|Abu Dhabi|Asia
United Kingdom|London|Europe
United States|Washington D.C|North America
Uruguay|Montevideo|South America
Uzbekistan|Tashkent|Asia
Vanuatu|Port Vila|Oceania
Venezuela|Caracas|South America
Vietnam|Hanoi|Asia
Yemen|Sana'a|Asia
Zambia|Lusaka|Africa
Zimbabwe|Harare|Africa
The Vatican|Vatican City|Europe
Palestine|Ramallah|Asia
"""

CONTINENTS = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania"]

def parse_raw(raw: str):
    rows, seen = [], set()
    for line in raw.strip().splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 3:
            continue
        key = tuple(parts)
        if key in seen:
            continue
        seen.add(key)
        rows.append(tuple(parts))  # (country, capital, continent)
    return rows

DATA_ALL = parse_raw(RAW)

# -----------------------------
# Helpers
# -----------------------------
def normalize(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return "".join(ch for ch in s.lower().strip() if ch.isalnum() or ch.isspace())

def is_close_guess(guess: str, answer: str, cutoff: float = 0.8) -> bool:
    g, a = normalize(guess), normalize(answer)
    if g == a:
        return True
    return bool(get_close_matches(g, [a], n=1, cutoff=cutoff))

# -----------------------------
# Session State
# -----------------------------
ss = st.session_state
ss.setdefault("started", False)
ss.setdefault("mode", "Country → Capital")
ss.setdefault("locked_mode", None)
ss.setdefault("index", 0)
ss.setdefault("score", 0)
ss.setdefault("history", [])
ss.setdefault("order", [])             # list of indices into filtered rows
ss.setdefault("active_filter", ["Whole world"])
ss.setdefault("locked_filter", None)   # locked regions after start
ss.setdefault("shuffle", True)

# -----------------------------
# Sidebar (Setup + Score)
# -----------------------------
st.title("🧭 Capitals Quiz")
st.caption("Guess capitals or countries by region. Auto-advance on correct answers or give-ups (3s pause).")

with st.sidebar:
    st.header("Setup")

    # Continue option (if a game is in progress)
    if ss.started and ss.order:
        if st.button("▶️ Continue current game"):
            st.rerun()

    # Region selection (locked after start)
    if not ss.started:
        region = st.radio(
            "Play scope",
            ["Whole world", "By continent"],
            index=0 if ss.active_filter == ["Whole world"] else 1,
        )
        if region == "By continent":
            sel = st.multiselect(
                "Continents",
                CONTINENTS,
                default=(ss.active_filter if ss.active_filter != ["Whole world"] else ["Europe"]),
            )
            ss.active_filter = sel or ["Europe"]
        else:
            ss.active_filter = ["Whole world"]
    else:
        locked = ss.locked_filter or ss.active_filter
        st.caption("Regions locked for this game:")
        st.write(", ".join(locked if isinstance(locked, list) else [locked]))

    # Mode (locked after start)
    if not ss.started:
        ss.mode = st.radio(
            "Mode",
            ["Country → Capital", "Capital → Country"],
            index=0 if ss.mode == "Country → Capital" else 1,
        )
    else:
        st.radio(
            "Mode",
            ["Country → Capital", "Capital → Country"],
            index=0 if (ss.locked_mode or ss.mode) == "Country → Capital" else 1,
            disabled=True,
        )
        st.caption(f"Mode locked: **{ss.locked_mode or ss.mode}**")

    # Shuffle toggle (only for new games)
    if not ss.started:
        ss.shuffle = st.toggle("Shuffle order on new game", value=ss.shuffle)
    else:
        st.toggle("Shuffle order on new game", value=ss.shuffle, disabled=True)

    st.markdown("---")

    # ---- Score / Counters (works during game) ----
    st.subheader("Score")
    # Determine total questions planned (if order exists, use it; else compute prospective)
    if ss.started and ss.order:
        total = len(ss.order)
        asked_completed = min(ss.index, total)           # completed questions
        current_q = min(ss.index + 1, total)             # current question number (1-based)
        st.write(f"Score: **{ss.score}**")
        st.write(f"Asked: **{asked_completed}** / {total}")
        st.write(f"Current: **{current_q}** / {total}")
    else:
        planned_total = len(DATA_ALL) if ss.active_filter == ["Whole world"] else len(
            [r for r in DATA_ALL if r[2] in set(ss.active_filter)]
        )
        st.write(f"Planned questions: **{planned_total}** (when you start)")

    st.markdown("---")
    if st.button("🔁 Reset game", type="secondary"):
        for k in ["started","locked_mode","index","score","history","order","locked_filter"]:
            ss.pop(k, None)
        st.rerun()

st.write("---")

# -----------------------------
# Filtering + Order
# -----------------------------
def filtered_rows(active_filter):
    if active_filter == ["Whole world"]:
        return DATA_ALL
    allowed = set(active_filter)
    return [r for r in DATA_ALL if r[2] in allowed]

def ensure_order_built():
    if ss.order:
        return
    ss.locked_filter = ss.active_filter
    rows = filtered_rows(ss.locked_filter)
    idx = list(range(len(rows)))
    if ss.shuffle:
        random.shuffle(idx)
    ss.order = idx
    ss.index = 0
    ss.score = 0
    ss.history = []

# -----------------------------
# Game flow
# -----------------------------
if not ss.started:
    st.info("Choose mode and region(s), then click **Start new game**.")
    if st.button("🚀 Start new game", type="primary"):
        ensure_order_built()
        ss.started = True
        ss.locked_mode = ss.mode
        st.rerun()
else:
    rows = filtered_rows(ss.locked_filter or ss.active_filter)
    if not rows:
        st.warning("No countries found for that selection.")
    elif ss.index >= len(ss.order):
        st.success(f"All done! Final score: **{ss.score} / {len(ss.order)}**")
        with st.expander("Review answers"):
            for q, g, ok, ans in ss.history:
                icon = "✅" if ok else "❌"
                st.write(f"{icon} **{q}** → {g} → **{ans}**")
    else:
        country, capital, continent = rows[ss.order[ss.index]]
        mode = ss.locked_mode or ss.mode
        if mode == "Country → Capital":
            prompt = f"({continent}) What's the capital of **{country}**?"
            correct = capital
        else:
            prompt = f"({continent}) **{capital}** is the capital of which country?"
            correct = country

        st.subheader(f"Question {ss.index + 1}")
        st.write(prompt)

        with st.form(key=f"q{ss.index}"):
            guess = st.text_input("Your answer:", "")
            submitted = st.form_submit_button("Submit")

        if submitted:
            if is_close_guess(guess, correct, cutoff=0.92):
                ss.score += 1
                ss.history.append((prompt, guess, True, correct))
                st.balloons()
                st.success(f"🎉 Correct! **{correct}**")
                st.toast("✅ Moving to next question...", icon="✅")
                time.sleep(3.0)
                ss.index += 1
                st.rerun()
            else:
                near = is_close_guess(guess, correct, cutoff=0.75)
                st.warning("So close!" if near else "Not quite, try again.")
                ss.history.append((prompt, guess, False, correct))

        if st.button("Give Up 🛑", type="secondary"):
            ss.history.append((prompt, "(gave up)", False, correct))
            st.error(f"❌ Gave up! The answer was **{correct}**")
            st.toast("❌ Moving on...", icon="❌")
            time.sleep(3.0)
            ss.index += 1
            st.rerun()

st.caption("Accent/typo tolerant. Use Reset to change mode or regions. Shuffle applies when starting a new game.")
