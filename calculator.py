import calendar
from dataclasses import dataclass
from datetime import datetime

import pytz

# =========================
# Timezone Configuration
# =========================
SG_TZ = pytz.timezone("Asia/Singapore")


@dataclass(kw_only=True)
class Results:
    available_balance: float
    current_month_adb: float
    adb_increase_vs_last_month: float
    balance_as_of: int
    buffer: float
    num_days_in_current_month: int

    @property
    def remaining_days(self):
        return self.num_days_in_current_month - self.balance_as_of

    @property
    def last_month_adb(self):
        return self.current_month_adb - self.adb_increase_vs_last_month

    @property
    def current_month_min_adb(self):
        MIN_ADB_INCREMENT = 500
        return self.last_month_adb + MIN_ADB_INCREMENT

    @property
    def current_amount(self):
        return self.balance_as_of * self.current_month_adb

    @property
    def total_amount_needed(self):
        return self.num_days_in_current_month * self.current_month_min_adb

    @property
    def increase_if_no_withdrawals(self):
        return self.remaining_days * self.available_balance

    @property
    def projected_increase_before_adjustment(self):
        return self.current_amount + self.increase_if_no_withdrawals

    @property
    def projected_increase_before_adjustment_avg(self):
        return (
            self.projected_increase_before_adjustment_avg
            / self.num_days_in_current_month
        )

    @property
    def projected_increase_after_adjustment(self):
        return self.projected_increase_before_adjustment + self.adjustment

    @property
    def projected_adb_before_adjustment(self):
        return (
            self.projected_increase_before_adjustment / self.num_days_in_current_month
        )

    @property
    def projected_adb_after_adjustment(self):
        return self.projected_increase_after_adjustment / self.num_days_in_current_month

    @property
    def projected_adb_change_before_adjustment(self):
        return self.projected_adb_before_adjustment - self.last_month_adb

    @property
    def projected_adb_change_after_adjustment(self):
        return self.projected_adb_after_adjustment - self.last_month_adb

    @property
    def buffer_adb(self):
        return self.buffer * self.num_days_in_current_month

    @property
    def adjustment(self):
        return (
            self.total_amount_needed
            - self.projected_increase_before_adjustment
            + self.buffer_adb
        )

    @property
    def adjustment_daily(self):
        return self.adjustment / self.remaining_days

    @property
    def amount_to_add_or_remove_next_month(self):
        return (
            self.projected_adb_after_adjustment
            - self.available_balance
            + self.adjustment_daily
        )

    def __str__(self) -> str:
        return (
            "### TL;DR\n"
            f"##### Required Transfer (in/out): {self.adjustment_daily:,.2f}\n"
            f"Positive = Deposit; Negative = Withdraw\n\n"
            "### Detailed Metrics\n"
            f"- For One-Day Adjustment: ${self.adjustment:,.2f}\n"
            f"- Last Month ADB: {self.last_month_adb:,.2f},\n"
            f"- Current Month Average Daily Balance:\n"
            f"- * Current ADB (as of {self.balance_as_of}): {self.current_month_adb:,.2f}, Change: {self.adb_increase_vs_last_month}\n"
            f"- * Projected ADB before adjustment: {self.projected_adb_before_adjustment:,.2f}, Change: {self.projected_adb_change_before_adjustment:,.2f}\n"
            f"- * Projected ADB after adjustment: {self.projected_adb_after_adjustment:,.2f}, Change: {self.projected_adb_change_after_adjustment:,.2f}\n"
            f"- Progress: \n"
            f"{self.current_amount:,.2f}/{self.total_amount_needed:,.2f}\n"
            f"- Amount to add/remove on 1st next month: {self.amount_to_add_or_remove_next_month:,.2f}"
        )

    def plot_adb_projection(self):
        import plotly.graph_objects as go

        days_in_month = self.num_days_in_current_month

        x_common = [1, self.balance_as_of]
        y_common = [0, self.adb_increase_vs_last_month]

        fig = go.Figure()

        # Before adjustment
        y1 = self.projected_adb_change_before_adjustment
        fig.add_trace(
            go.Scatter(
                x=x_common + [days_in_month],
                y=y_common + [y1],
                mode="lines+markers",
                name="Before Adjustment",
            )
        )

        # After adjustment
        y2 = self.projected_adb_change_after_adjustment
        fig.add_trace(
            go.Scatter(
                x=x_common + [days_in_month],
                y=y_common + [y2],
                mode="lines+markers",
                name="After Adjustment",
            )
        )

        fig.update_layout(
            title="Monthly ADB Projection",
            xaxis_title="Day of Month",
            yaxis_title="ADB (SGD)",
            xaxis=dict(
                tickmode="linear",
                dtick=1,
                range=[1, days_in_month],
            ),
            legend_title="Scenario",
            hovermode="x unified",
            template="plotly_white",
        )

        return fig


class SaveBonusCalculator:
    @property
    def time_now(self):
        return datetime.now(SG_TZ)

    @property
    def num_days_in_current_month(self):
        return calendar.monthrange(self.time_now.year, self.time_now.month)[1]

    def calculate(
        self,
        available_balance: float,
        current_month_adb: float,
        adb_increase_vs_last_month: float,
        balance_as_of: float,
        buffer: float,
    ):
        return Results(
            available_balance=available_balance,
            current_month_adb=current_month_adb,
            adb_increase_vs_last_month=adb_increase_vs_last_month,
            balance_as_of=balance_as_of,
            buffer=buffer,
            num_days_in_current_month=self.num_days_in_current_month,
        )
