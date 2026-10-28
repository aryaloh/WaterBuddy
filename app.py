"""
WaterBuddy - Your Daily Hydration Companion
FA-2: Developing and Deploying App Using Python (Streamlit)

Structure
---------
1. Configuration & constants
2. Pure logic functions (easy to test, no Streamlit calls)
3. Session-state helpers (init, add water, undo, reset)
4. UI components (mascot, bottle, sidebar, sections)
5. main()
"""

import random
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

# ----------------------------------------------------------------------------
# 1. CONFIGURATION & CONSTANTS
# ----------------------------------------------------------------------------
st.set_page_config(page_title="WaterBuddy", page_icon="💧", layout="centered")

# Age group -> (recommended daily goal in ml, friendly greeting)
AGE_GROUPS = {
    "6-12": (1600, "Hey champ! 🧒 Water keeps you energetic for school and play!"),
    "13-18": (2000, "Hi teen! 🧑 Stay sharp for studies and sports with water!"),
    "19-50": (2500, "Hello! 🧑‍💼 Hydration keeps your focus and energy up!"),
    "51-64": (2400, "Welcome! 🧓 Steady sips through the day keep you feeling great!"),
    "65+": (2000, "Hello! 👵 Little and often is the best way to stay hydrated!"),
}

QUICK_LOG_ML = 250          # the "+250 ml" button
CUP_ML = 240                # 1 US cup = 240 ml (used by the unit converter)
MIN_GOAL, MAX_GOAL = 500, 6000

HYDRATION_TIPS = [
    "Start your day with a glass of water before tea or coffee. ☀️",
    "Keep a bottle on your desk - you drink more when you can see it. 👀",
    "Feeling tired? Mild dehydration can cause fatigue. Try a glass of water! 😴",
    "Fruits like watermelon and cucumber also add to your hydration. 🍉",
    "Set a reminder to sip water every hour. ⏰",
    "Drink a glass of water before each meal. 🍽️",
    "Pale yellow urine is a good sign that you're well hydrated. 💛",
    "Add lemon or mint to make water more exciting. 🍋",
]


# ----------------------------------------------------------------------------
# 2. PURE LOGIC FUNCTIONS (Stage 5 - calculations)
# ----------------------------------------------------------------------------
def get_recommended_goal(age_group: str) -> int:
    """Return the standard daily goal (ml) for an age group."""
    return AGE_GROUPS[age_group][0]


def calculate_total(log: list) -> int:
    """Total intake so far (ml)."""
    return sum(entry["ml"] for entry in log)


def calculate_remaining(total: int, goal: int) -> int:
    """Water still needed to reach the goal (never negative)."""
    return max(goal - total, 0)


def calculate_percentage(total: int, goal: int) -> float:
    """Percentage of goal achieved (can exceed 100)."""
    if goal <= 0:
        return 0.0
    return round(total / goal * 100, 1)


def get_milestone(pct: float) -> int:
    """Highest milestone reached: 0, 25, 50, 75 or 100."""
    for m in (100, 75, 50, 25):
        if pct >= m:
            return m
    return 0


def get_message(pct: float) -> tuple:
    """Return (mascot emoji, motivational message) for the current progress."""
    if pct == 0:
        return "😴", "Let's get started! Take your first sip. 💧"
    elif pct < 25:
        return "🙂", "Nice start! Keep sipping through the day."
    elif pct < 50:
        return "😊", "Great! You reached 25%! Keep it flowing! 🌊"
    elif pct < 75:
        return "😄", "Great! You reached 50%! You're halfway there! 🎉"
    elif pct < 100:
        return "🤩", "Awesome! 75% done - the finish line is near! 🏁"
    elif pct == 100:
        return "🥳", "Goal achieved! You're a hydration hero! 🏆"
    else:
        return "🐬", "Wow, you've beaten your goal! Great job today! 🌟"


def ml_to_cups(ml: float) -> float:
    return round(ml / CUP_ML, 2)


def cups_to_ml(cups: float) -> int:
    return int(round(cups * CUP_ML))


# ----------------------------------------------------------------------------
# 3. SESSION-STATE HELPERS (Stage 4 - data storage)
# ----------------------------------------------------------------------------
def init_state() -> None:
    """Create all session_state keys once per session."""
    defaults = {
        "age_group": "19-50",
        "goal": get_recommended_goal("19-50"),
        "log": [],                # list of {"time": str, "ml": int}
        "last_milestone": 0,
        "celebrated": False,
        "tip": random.choice(HYDRATION_TIPS),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def on_age_change() -> None:
    """When age group changes, auto-suggest that group's goal."""
    st.session_state.goal = get_recommended_goal(st.session_state.age_group)


def add_water(ml: int) -> None:
    """Log water and trigger milestone feedback if a new one is reached."""
    if ml <= 0:
        return
    st.session_state.log.append({"time": datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%I:%M %p"), "ml": int(ml)})

    pct = calculate_percentage(calculate_total(st.session_state.log), st.session_state.goal)
    milestone = get_milestone(pct)
    if milestone > st.session_state.last_milestone:
        st.session_state.last_milestone = milestone
        st.toast(get_message(pct)[1], icon="🎉")
        if milestone >= 100 and not st.session_state.celebrated:
            st.session_state.celebrated = True
            st.balloons()


def undo_last() -> None:
    if st.session_state.log:
        st.session_state.log.pop()
        pct = calculate_percentage(calculate_total(st.session_state.log), st.session_state.goal)
        st.session_state.last_milestone = get_milestone(pct)
        if pct < 100:
            st.session_state.celebrated = False


def reset_day() -> None:
    """Start fresh for a new day."""
    st.session_state.log = []
    st.session_state.last_milestone = 0
    st.session_state.celebrated = False
    st.session_state.tip = random.choice(HYDRATION_TIPS)


# ----------------------------------------------------------------------------
# 4. UI COMPONENTS (Stage 6 - interface)
# ----------------------------------------------------------------------------
def apply_theme(dark: bool) -> None:
    """Calm aqua/blue theme with an optional dark mode."""
    bg, text, card = ("#0b1f33", "#e6f6ff", "#12304d") if dark else ("#eaf8ff", "#0a3d62", "#ffffff")
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {bg}; color: {text}; }}
        h1, h2, h3, p, label, span, div {{ color: {text}; }}
        .wb-card {{ background:{card}; border-radius:18px; padding:16px 20px;
                    box-shadow:0 2px 10px rgba(0,0,0,.12); margin-bottom:12px; }}
        .wb-title {{ font-size:2.6rem; font-weight:800; text-align:center; color:#0288d1; }}
        .wb-sub {{ text-align:center; font-size:1.15rem; margin-bottom:10px; }}
        .wb-msg {{ font-size:1.4rem; font-weight:600; text-align:center; }}
        .wb-mascot {{ font-size:5rem; text-align:center; line-height:1.1; }}
        .stButton > button {{ font-size:1.1rem; font-weight:700; border-radius:12px;
                              background:#29b6f6; color:white; border:none; }}
        .stButton > button:hover {{ background:#0288d1; color:white; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_bottle(pct: float) -> str:
    """Animated water bottle: the fill level follows the percentage."""
    fill = min(max(pct, 0), 100)
    return f"""
    <div style="display:flex;justify-content:center;">
      <div style="width:90px;height:34px;background:#90a4ae;border-radius:8px 8px 0 0;margin:0 auto;"></div>
    </div>
    <div style="display:flex;justify-content:center;">
      <div style="position:relative;width:150px;height:240px;border:5px solid #0288d1;
                  border-radius:30px 30px 40px 40px;overflow:hidden;background:rgba(255,255,255,.35);">
        <div style="position:absolute;bottom:0;left:0;width:100%;height:{fill}%;
                    background:linear-gradient(180deg,#4fc3f7,#0277bd);
                    transition:height 1s ease;"></div>
        <div style="position:absolute;top:50%;width:100%;text-align:center;
                    font-size:1.8rem;font-weight:800;color:#fff;
                    text-shadow:0 0 5px #01579b;transform:translateY(-50%);">{pct:.0f}%</div>
      </div>
    </div>
    """


def section_header() -> None:
    st.markdown('<div class="wb-title">💧 WaterBuddy</div>', unsafe_allow_html=True)
    st.markdown('<div class="wb-sub">Your Daily Hydration Companion</div>', unsafe_allow_html=True)


def section_age_and_goal() -> None:
    """Age selector + auto-suggested goal with manual adjustment."""
    st.subheader("1️⃣ About You")
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Select your age group", list(AGE_GROUPS.keys()),
                     key="age_group", on_change=on_age_change)
    with col2:
        st.number_input("Daily goal (ml) - adjust if needed", min_value=MIN_GOAL,
                        max_value=MAX_GOAL, step=50, key="goal")

    st.info(AGE_GROUPS[st.session_state.age_group][1])

    # Optional: standard target vs user-set goal side by side
    std = get_recommended_goal(st.session_state.age_group)
    c1, c2 = st.columns(2)
    c1.metric("Standard target", f"{std} ml")
    c2.metric("Your goal", f"{st.session_state.goal} ml", delta=f"{st.session_state.goal - std} ml")


def section_logging() -> None:
    """+250 ml button, custom input, undo & reset."""
    st.subheader("2️⃣ Log Your Water")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(f"➕ +{QUICK_LOG_ML} ml", use_container_width=True):
            add_water(QUICK_LOG_ML)
    with col2:
        c_in, c_btn = st.columns([2, 1])
        custom = c_in.number_input("Custom amount (ml)", min_value=0, max_value=2000,
                                   step=50, value=0, label_visibility="collapsed",
                                   key="custom_ml")
        if c_btn.button("Add", use_container_width=True):
            if custom > 0:
                add_water(custom)
            else:
                st.warning("Enter an amount above 0 ml.")

    b1, b2 = st.columns(2)
    if b1.button("↩️ Undo last", use_container_width=True):
        undo_last()
    if b2.button("🔄 Reset day", use_container_width=True):
        reset_day()


def section_progress() -> None:
    """Live calculations, bottle, progress bar and mascot message."""
    st.subheader("3️⃣ Your Progress")
    goal = st.session_state.goal
    total = calculate_total(st.session_state.log)
    remaining = calculate_remaining(total, goal)
    pct = calculate_percentage(total, goal)
    mascot, message = get_message(pct)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total intake", f"{total} ml")
    m2.metric("Remaining", f"{remaining} ml")
    m3.metric("Achieved", f"{pct:.0f}%")

    st.progress(min(pct / 100, 1.0))

    col_bottle, col_mascot = st.columns(2)
    with col_bottle:
        st.markdown(render_bottle(pct), unsafe_allow_html=True)
    with col_mascot:
        st.markdown(f'<div class="wb-mascot">{mascot}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="wb-msg">{message}</div>', unsafe_allow_html=True)


def section_summary() -> None:
    """History table, chart and end-of-day summary."""
    log = st.session_state.log
    if not log:
        return
    st.subheader("4️⃣ Today's Log")
    st.dataframe([{"Time": e["time"], "Amount (ml)": e["ml"]} for e in log],
                 use_container_width=True, hide_index=True)

    running, total = [], 0
    for e in log:
        total += e["ml"]
        running.append(total)
    st.line_chart({"Cumulative intake (ml)": running})

    if calculate_percentage(calculate_total(log), st.session_state.goal) >= 100:
        st.success(f"🏆 End-of-day summary: {len(log)} drinks, {calculate_total(log)} ml "
                   f"- goal complete! Great job today!")


def sidebar() -> bool:
    """Sidebar: theme toggle, daily tip, unit converter."""
    with st.sidebar:
        st.header("⚙️ Settings")
        dark = st.toggle("🌙 Dark mode", value=False)

        st.header("💡 Daily Tip")
        st.write(st.session_state.tip)
        if st.button("New tip"):
            st.session_state.tip = random.choice(HYDRATION_TIPS)
            st.rerun()

        st.header("🔁 Unit Converter")
        mode = st.radio("Convert", ["cups → ml", "ml → cups"], horizontal=True)
        if mode == "cups → ml":
            cups = st.number_input("Cups", min_value=0.0, value=1.0, step=0.5)
            st.write(f"**{cups} cups = {cups_to_ml(cups)} ml**")
        else:
            ml = st.number_input("Millilitres", min_value=0, value=250, step=50)
            st.write(f"**{ml} ml = {ml_to_cups(ml)} cups**")
        st.caption("1 cup = 240 ml")
    return dark


# ----------------------------------------------------------------------------
# 5. MAIN
# ----------------------------------------------------------------------------
def main() -> None:
    init_state()
    dark = sidebar()
    apply_theme(dark)
    section_header()
    section_age_and_goal()
    section_logging()
    section_progress()
    section_summary()
    st.caption("WaterBuddy • No personal data is stored - everything lives only in your browser session.")


if __name__ == "__main__":
    main()
