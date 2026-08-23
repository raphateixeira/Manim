"""
Componentes compartilhados para a série "Resposta ao degrau de sistemas de
2ª ordem subamortecidos": paleta matemática (não industrial), eixos limpos,
bloco de diagrama genérico G(s)/R(s)/C(s), simulação numérica da resposta
c(t) e dos parâmetros característicos (OS%, Tp, Ts, Tr).

Convenção de cores: cada símbolo (K, ζ, ωn, ωd) mantém a MESMA cor em todas
as cenas, para que o espectador reconheça o papel de cada termo só pela cor,
como em uma aula com giz colorido — sem ícones ou paineis de engenharia.
"""

from manim import *
import numpy as np
import os

# ------------------------------------------------------------------
# Paleta matemática (fundo quase-preto, cores de giz)
# ------------------------------------------------------------------
BG        = "#0E1116"
INK       = "#ECECEC"   # texto/eixos principais
AXIS      = "#7A828E"   # eixos, grades, texto secundário
COL_K     = "#F2C94C"   # K — ganho estático / valor de regime permanente
COL_ZETA  = "#EB5757"   # ζ — coeficiente de amortecimento
COL_WN    = "#5BC0EB"   # ωn — frequência natural não amortecida
COL_WD    = "#56C596"   # ωd — frequência natural amortecida
COL_TRANS = "#BB86FC"   # termo transitório
COL_SS    = "#F2C94C"   # termo de regime permanente (mesma cor de K)
COL_CURVE = "#5BC0EB"   # curva c(t)
COL_ENV   = "#7A828E"   # envoltória exponencial
COL_OS    = "#EB5757"   # overshoot / pico
COL_TP    = "#BB86FC"   # tempo de pico
COL_TS    = "#56C596"   # tempo de acomodação
COL_TR    = "#F2994A"   # tempo de subida


def header(text, font_size=30):
    return Text(text, font_size=font_size, color=INK, weight=BOLD).to_edge(UP, buff=0.15)


def load_ufpa_logo(height=1.0):
    """Brasão da UFPA (assets/ufpa_logo_crop.png)."""
    path = os.path.join(os.path.dirname(__file__), "assets", "ufpa_logo_crop.png")
    logo = ImageMobject(path)
    logo.height = height
    return logo


def signal_axes(x_range, y_range, x_length, y_length, **kwargs):
    ax = Axes(x_range=x_range, y_range=y_range, x_length=x_length, y_length=y_length,
              axis_config={"stroke_color": AXIS, "stroke_width": 2,
                            "tip_length": 0.15, "tip_width": 0.1,
                            "include_ticks": True, "font_size": 16},
              tips=True, **kwargs)
    ax.set_color(AXIS)
    return ax


def build_block(label, width=2.2, height=1.2, color=INK, font_size=32):
    """Bloco genérico de diagrama de blocos (retângulo + rótulo em LaTeX),
    com pontos de conexão vivos .get_in() / .get_out()."""
    body = Rectangle(width=width, height=height, stroke_color=color,
                      stroke_width=3, fill_color=BG, fill_opacity=1)
    txt = MathTex(label, font_size=font_size, color=color).move_to(body)
    left = Dot(body.get_left(), radius=0.001, fill_opacity=0)
    right = Dot(body.get_right(), radius=0.001, fill_opacity=0)
    blk = VGroup(body, txt, left, right)
    blk.get_in = lambda: left.get_center()
    blk.get_out = lambda: right.get_center()
    return blk


def bullet(symbol_tex, color, desc, font_size=24, sym_size=None):
    sym = MathTex(symbol_tex, color=color, font_size=sym_size or (font_size + 6))
    txt = Text(desc, color=INK, font_size=font_size)
    return VGroup(sym, txt).arrange(RIGHT, buff=0.3)


# ------------------------------------------------------------------
# Modelo matemático: c(t) para o sistema subamortecido
# ------------------------------------------------------------------

def step_response(t, K=1.0, zeta=0.35, wn=3.0):
    wd = wn * np.sqrt(1 - zeta ** 2)
    phi = np.arccos(zeta)
    return K * (1.0 - (np.exp(-zeta * wn * t) / np.sqrt(1 - zeta ** 2)) * np.sin(wd * t + phi))


def envelope_upper(t, K=1.0, zeta=0.35, wn=3.0):
    return K * (1.0 + np.exp(-zeta * wn * t) / np.sqrt(1 - zeta ** 2))


def envelope_lower(t, K=1.0, zeta=0.35, wn=3.0):
    return K * (1.0 - np.exp(-zeta * wn * t) / np.sqrt(1 - zeta ** 2))


def compute_params(K=1.0, zeta=0.35, wn=3.0):
    """Parâmetros característicos da resposta subamortecida ao degrau."""
    wd = wn * np.sqrt(1 - zeta ** 2)
    phi = np.arccos(zeta)
    Tp = np.pi / wd
    OS = 100.0 * np.exp(-zeta * np.pi / np.sqrt(1 - zeta ** 2))
    Ts2 = 4.0 / (zeta * wn)   # critério de 2%
    Ts5 = 3.0 / (zeta * wn)   # critério de 5%

    t_fine = np.linspace(0, 3 * Ts2, 40000)
    c = step_response(t_fine, K, zeta, wn)
    idx = np.argmax(c >= K)
    Tr = t_fine[idx]

    return {"wd": wd, "phi": phi, "Tp": Tp, "OS": OS,
            "Ts2": Ts2, "Ts5": Ts5, "Tr": Tr, "K": K, "zeta": zeta, "wn": wn}


def growing_curve(axes, t_arr, y_arr, t_tracker, color=COL_CURVE, stroke_width=4):
    def make():
        t_now = t_tracker.get_value()
        idx = max(int(np.searchsorted(t_arr, t_now, side="right")), 2)
        return axes.plot_line_graph(
            x_values=t_arr[:idx], y_values=y_arr[:idx],
            line_color=color, add_vertex_dots=False, stroke_width=stroke_width)
    return always_redraw(make)
