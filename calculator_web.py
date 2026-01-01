import streamlit as st
from calculator import SaveBonusCalculator
from utils import caffeine

# =========================
# Streamlit UI
# =========================
st.set_page_config(
    page_title="OCBC Save Bonus Calculator",
    layout="centered",
)

st.title("OCBC Save Bonus Calculator")
st.caption("Singapore Time (SGT)–aware calculator for Save Bonus Calculation")
st.divider()
st.markdown(caffeine())
st.divider()

calculator = SaveBonusCalculator()

with st.form("calculator_form"):
    st.subheader("From OCBC's Website")

    available_balance = st.number_input(
        "Available Balance",
        min_value=0.0,
        step=100.0,
    )

    current_month_adb = st.number_input(
        "Current Month Average Daily Balance",
        step=100.0,
    )

    balance_as_of = st.number_input(
        "Balance as of",
        min_value=1,
        max_value=calculator.num_days_in_current_month,
        step=1,
        value=min(1, calculator.time_now.day - 1),
    )

    adb_increase_vs_last_month = st.number_input(
        "Average Daily Balance Increase vs. Last Month",
        step=100.0,
    )

    buffer = st.number_input(
        "Safety Buffer [OPTIONAL]",
        value=50.0,
        step=10.0,
    )

    submitted = st.form_submit_button("Calculate")

if submitted:
    result = calculator.calculate(
        available_balance=available_balance,
        current_month_adb=current_month_adb,
        adb_increase_vs_last_month=adb_increase_vs_last_month,
        balance_as_of=balance_as_of,
        buffer=buffer,
    )
    st.divider()

    st.subheader("Results")
    st.caption(
        "The projections below assume no additional inflows or outflows for the remainder of the month. "
        "Any account activity will materially impact the computed figures."
    )

    st.markdown(
        """
    **Operational Notes**
    - Daily transaction cutoff applies at **10:00 PM (SGT)**
    - No account movements are processed on **Sundays**
    """
    )

    st.markdown(result)

    st.subheader("ADB Projection")
    fig = result.plot_adb_projection()
    st.plotly_chart(fig, use_container_width=True)
