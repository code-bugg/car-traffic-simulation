"""
StatsPlotter
============
Generates a multi-panel matplotlib report from the statistics DataFrame.
"""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd

logger = logging.getLogger(__name__)

CHISINAU_BLUE  = "#003DA5"
CHISINAU_RED   = "#CC0000"
CHISINAU_GOLD  = "#F5A623"
CHISINAU_GREEN = "#2ECC71"
BG_COLOR       = "#F7F9FC"


class StatsPlotter:
    def __init__(self, output_dir: str = "data/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ── public ───────────────────────────────────────────────────────

    def plot_all(self, df: pd.DataFrame) -> None:
        """Generate the full dashboard and individual charts."""
        self._plot_dashboard(df)
        self._plot_mean_speed(df)
        self._plot_waiting_time(df)
        self._plot_vehicle_count(df)
        self._plot_emissions(df)
        logger.info("All charts saved.")

    # ── dashboard ────────────────────────────────────────────────────

    def _plot_dashboard(self, df: pd.DataFrame) -> None:
        fig = plt.figure(figsize=(16, 10), facecolor=BG_COLOR)
        fig.suptitle(
            "Chișinău Urban Traffic Simulation — Dashboard",
            fontsize=16, fontweight="bold", color=CHISINAU_BLUE, y=0.98
        )

        gs = gridspec.GridSpec(2, 3, figure=fig,
                               hspace=0.45, wspace=0.35,
                               left=0.07, right=0.97,
                               top=0.92, bottom=0.08)

        axes = [
            fig.add_subplot(gs[0, 0]),
            fig.add_subplot(gs[0, 1]),
            fig.add_subplot(gs[0, 2]),
            fig.add_subplot(gs[1, 0]),
            fig.add_subplot(gs[1, 1]),
            fig.add_subplot(gs[1, 2]),
        ]

        plots = [
            ("mean_speed",       "Mean Speed (m/s)",          CHISINAU_BLUE),
            ("mean_waiting_time","Mean Waiting Time (s)",      CHISINAU_RED),
            ("vehicle_count",    "Active Vehicles",            CHISINAU_GOLD),
            ("halting_vehicles", "Halting Vehicles",           CHISINAU_GREEN),
            ("mean_co2",         "Mean CO₂ Emission (mg/s)",   "#8E44AD"),
            ("mean_fuel",        "Mean Fuel Use (ml/s)",       "#E67E22"),
        ]

        for ax, (col, ylabel, color) in zip(axes, plots):
            if col not in df.columns:
                ax.set_visible(False)
                continue
            ax.set_facecolor(BG_COLOR)
            ax.plot(df["step"], df[col], color=color, linewidth=1.6)
            ax.fill_between(df["step"], df[col], alpha=0.12, color=color)
            ax.set_xlabel("Step", fontsize=8)
            ax.set_ylabel(ylabel, fontsize=8)
            ax.set_title(ylabel, fontsize=9, fontweight="bold", color="#333333")
            ax.tick_params(labelsize=7)
            ax.spines[["top", "right"]].set_visible(False)
            ax.grid(axis="y", linestyle="--", alpha=0.4)

        fig.savefig(self.output_dir / "dashboard.png", dpi=150)
        plt.close(fig)
        logger.info("Dashboard saved.")

    # ── individual charts ────────────────────────────────────────────

    def _simple_plot(self, df, col, ylabel, title, color, filename):
        fig, ax = plt.subplots(figsize=(9, 4), facecolor=BG_COLOR)
        ax.set_facecolor(BG_COLOR)
        ax.plot(df["step"], df[col], color=color, linewidth=2)
        ax.fill_between(df["step"], df[col], alpha=0.15, color=color)
        ax.set_xlabel("Simulation Step", fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(title, fontsize=12, fontweight="bold", color=CHISINAU_BLUE)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        fig.tight_layout()
        fig.savefig(self.output_dir / filename, dpi=150)
        plt.close(fig)

    def _plot_mean_speed(self, df):
        self._simple_plot(df, "mean_speed", "Speed (m/s)",
                          "Average Vehicle Speed — Chișinău",
                          CHISINAU_BLUE, "mean_speed.png")

    def _plot_waiting_time(self, df):
        self._simple_plot(df, "mean_waiting_time", "Waiting Time (s)",
                          "Average Waiting Time at Junctions — Chișinău",
                          CHISINAU_RED, "waiting_time.png")

    def _plot_vehicle_count(self, df):
        self._simple_plot(df, "vehicle_count", "Active Vehicles",
                          "Active Vehicle Count — Chișinău",
                          CHISINAU_GOLD, "vehicle_count.png")

    def _plot_emissions(self, df):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4),
                                        facecolor=BG_COLOR)
        for ax, col, label, color in [
            (ax1, "mean_co2",  "CO₂ (mg/s)",  "#8E44AD"),
            (ax2, "mean_fuel", "Fuel (ml/s)",  "#E67E22"),
        ]:
            ax.set_facecolor(BG_COLOR)
            if col in df.columns:
                ax.plot(df["step"], df[col], color=color, linewidth=2)
                ax.fill_between(df["step"], df[col], alpha=0.15, color=color)
            ax.set_xlabel("Simulation Step", fontsize=10)
            ax.set_ylabel(label, fontsize=10)
            ax.set_title(label, fontsize=11, fontweight="bold")
            ax.spines[["top","right"]].set_visible(False)
            ax.grid(axis="y", linestyle="--", alpha=0.4)

        fig.suptitle("Emissions & Fuel — Chișinău", fontsize=13,
                     fontweight="bold", color=CHISINAU_BLUE)
        fig.tight_layout()
        fig.savefig(self.output_dir / "emissions.png", dpi=150)
        plt.close(fig)
