import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

plt.style.use('dark_background')

BG_COLOR = '#1e1e1e'
PANEL_COLOR = '#2b2b2b'
TEXT_COLOR = '#e0e0e0'
GRID_COLOR = '#444444'
ACCENT1 = '#54a0ff'
ACCENT2 = '#ff9f43'
ACCENT3 = '#1dd1a1'

DAYS_IN_YEAR = 365
SIM_TRIALS = 5000

# ----------------------------------------------------------------------
# Exact probability
# ----------------------------------------------------------------------
def exact_probability_array(days_in_year=DAYS_IN_YEAR):
    i = np.arange(0, days_in_year)
    ratios = (days_in_year - i) / days_in_year
    p_no_match = np.concatenate(([1.0], np.cumprod(ratios)))
    return 1.0 - p_no_match

# ----------------------------------------------------------------------
# Monte Carlo simulation
# ----------------------------------------------------------------------
def simulate_probability(n, days_in_year=DAYS_IN_YEAR, trials=SIM_TRIALS, rng=None):
    if n <= 1:
        return 0.0
    if rng is None:
        rng = np.random.default_rng()
    draws = rng.integers(0, days_in_year, size=(trials, n))
    draws.sort(axis=1)
    has_match = (np.diff(draws, axis=1) == 0).any(axis=1)
    return has_match.mean()

rng = np.random.default_rng(seed=42)

ns = np.arange(0, DAYS_IN_YEAR + 1)
exact_curve = exact_probability_array(DAYS_IN_YEAR)

SIM_CURVE_STEP = 10
SIM_CURVE_TRIALS = 2000
sim_ns = np.arange(0, DAYS_IN_YEAR + 1, SIM_CURVE_STEP)
sim_curve = [simulate_probability(n, trials=SIM_CURVE_TRIALS, rng=rng) for n in sim_ns]

fig, ax = plt.subplots(figsize=(9.5, 7))
fig.patch.set_facecolor(BG_COLOR)
plt.subplots_adjust(bottom=0.22)
ax.set_facecolor(BG_COLOR)

ax.plot(ns, exact_curve, color=ACCENT1, lw=2, label='Exact probability (formula)')
ax.plot(sim_ns, sim_curve, 'o-', color=ACCENT2, lw=1, markersize=4, alpha=0.85,
        label=f'Monte Carlo simulation ({SIM_TRIALS:,} trials each)')

exact_marker, = ax.plot([], [], 'o', color=ACCENT3, markersize=10, zorder=6,
                        label='Exact P at chosen n')
sim_marker, = ax.plot([], [], 'o', color=ACCENT2, markersize=10, zorder=6,
                      markeredgecolor=TEXT_COLOR, markeredgewidth=1,
                      label=f'Live simulation at chosen n')

ax.set_xlabel('Number of people (n)', color=TEXT_COLOR)
ax.set_ylabel('P(at least one shared birthday)', color=TEXT_COLOR)
ax.set_title('The Birthday Paradox', color=TEXT_COLOR, fontsize=13)
ax.set_xlim(0, DAYS_IN_YEAR)
ax.set_ylim(0, 1.02)

leg = ax.legend(loc='lower right', facecolor=PANEL_COLOR, edgecolor=GRID_COLOR)
for txt in leg.get_texts():
    txt.set_color(TEXT_COLOR)

ax.grid(True, color=GRID_COLOR, alpha=0.4)
ax.tick_params(colors=TEXT_COLOR)
for spine in ax.spines.values():
    spine.set_color(GRID_COLOR)

info_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color=TEXT_COLOR,
                     fontsize=10, va='top', family='monospace')

fig.text(0.5, 0.02,
          'By the pigeonhole principle, 366 people GUARANTEE a shared birthday '
          '(367 if allowing for Feb 29) -- a separate, non-probabilistic result.',
          ha='center', va='bottom', color=TEXT_COLOR, fontsize=8.5, style='italic',
          wrap=True)

ax_slider = fig.add_axes([0.15, 0.10, 0.7, 0.05])
ax_slider.set_facecolor(PANEL_COLOR)
slider_n = Slider(ax_slider, 'n', valmin=0, valmax=DAYS_IN_YEAR, valinit=23, valstep=1,
                   color=ACCENT2, track_color=PANEL_COLOR, initcolor=None)
slider_n.label.set_color(TEXT_COLOR)
slider_n.valtext.set_color(TEXT_COLOR)
for spine in ax_slider.spines.values():
    spine.set_color(GRID_COLOR)

def update(val):
    n = int(round(slider_n.val))
    p_exact = exact_curve[n]
    p_sim = simulate_probability(n, trials=SIM_TRIALS, rng=rng)

    exact_marker.set_data([n], [p_exact])
    sim_marker.set_data([n], [p_sim])

    info_text.set_text(
        f'n = {n}\n'
        f'Exact P      = {p_exact:.15f}\n'
        f'Simulated P  = {p_sim:.15f}'
    )
    fig.canvas.draw_idle()

slider_n.on_changed(update)
update(slider_n.val)  # initial draw

def center_window(fig):
    try:
        manager = fig.canvas.manager
        backend = plt.get_backend().lower()
        window = manager.window

        if 'tk' in backend:
            window.update_idletasks()
            width = window.winfo_reqwidth()
            height = window.winfo_reqheight()
            if width <= 1 or height <= 1:
                window.update()
                width = window.winfo_width()
                height = window.winfo_height()
            screen_w = window.winfo_screenwidth()
            screen_h = window.winfo_screenheight()
            x = max(0, (screen_w - width) // 2)
            y = max(0, (screen_h - height) // 2)
            window.geometry(f"{width}x{height}+{x}+{y}")

        elif 'qt' in backend:
            screen = window.screen() if hasattr(window, 'screen') else None
            if screen is None:
                from matplotlib.backends.qt_compat import QtWidgets
                screen = QtWidgets.QApplication.primaryScreen()
            screen_geo = screen.availableGeometry()
            frame_geo = window.frameGeometry()
            frame_geo.moveCenter(screen_geo.center())
            window.move(frame_geo.topLeft())

        elif 'wx' in backend:
            window.CentreOnScreen()

    except Exception:
        pass

center_window(fig)

plt.show()