"""
Componentes visuais reutilizáveis (estilo industrial) e simulação da planta
térmica para o vídeo didático de introdução a sistemas de controle:
controle de temperatura de um forno.

Convenções:
- Temperatura em graus Celsius.
- Sinal de controle / potência do atuador u(t) normalizado em [0, 1].
- Tempo de simulação em "segundos de cena": 1 s de simulação = 1 s de
  animação (run_time), como em SimulBuck.py.
- Todo componente que expõe pontos de conexão (entrada/saída) o faz por
  meio de métodos/lambdas que leem a posição atual de um sub-mobject já
  incluído no grupo — nunca de coordenadas numéricas "congeladas" antes de
  escalar/mover o grupo (isso causava ponteiros/setas desalinhados).
"""

from manim import *
import numpy as np

# ------------------------------------------------------------------
# Paleta (derivada de TemaRTx.scss, para casar com o site do projeto)
# ------------------------------------------------------------------
STEEL       = "#4A6FA5"   # accent
STEEL_DARK  = "#1B365D"   # primary
STEEL_LIGHT = "#9DB2D6"
GOLD        = "#E8C547"   # highlight-color
HEAT        = "#E65100"   # warning-color
GREEN_OK    = "#3FA34D"
RED_ERR     = "#C0455A"   # vermelho-ufpa (clareado)
BLUE_CTRL   = "#2AA1D6"   # info
PANEL       = "#3A414C"
PANEL_DARK  = "#20242B"
SCREEN_BG   = "#0B0F14"
HULL        = "#2B303A"
CAVITY_BG   = "#0E0B09"


def heat_color(frac):
    """Mapeia fração de temperatura/potência [0,1] para uma cor de brasa: cinza -> laranja -> dourado."""
    frac = float(np.clip(frac, 0.0, 1.0))
    if frac < 0.5:
        return interpolate_color(ManimColor(PANEL_DARK), ManimColor(HEAT), frac / 0.5)
    return interpolate_color(ManimColor(HEAT), ManimColor(GOLD), (frac - 0.5) / 0.5)


# ------------------------------------------------------------------
# Simulação da planta (forno) — 1a ordem, atuador satura em [0,1]
# ------------------------------------------------------------------

def simulate_open_loop(t_end=10.0, dt=0.02, t_on=1.0, Tamb=25.0, tau=4.0, K=60.0):
    """Malha aberta: atuador liga em t_on com potência total. Mostra a dinâmica da planta."""
    n = int(t_end / dt)
    t = 0.0
    T = Tamb
    ts = np.empty(n); Ts = np.empty(n); us = np.empty(n)
    for i in range(n):
        u = 1.0 if t >= t_on else 0.0
        T += ((-(T - Tamb) + K * u) / tau) * dt
        ts[i] = t; Ts[i] = T; us[i] = u
        t += dt
    return {"t": ts, "T": Ts, "u": us}


def simulate_closed_loop(t_end=20.0, dt=0.02, Tamb=25.0, tau=4.0, K=60.0,
                          Kp=0.05, Ki=0.03, r1=70.0, r2=85.0, t_step=10.0):
    """Malha fechada com controlador PI e anti-windup por saturação (u em [0,1])."""
    n = int(t_end / dt)
    t = 0.0
    T = Tamb
    integral = 0.0
    ts = np.empty(n); Ts = np.empty(n); us = np.empty(n)
    es = np.empty(n); rs = np.empty(n)
    for i in range(n):
        r = r1 if t < t_step else r2
        e = r - T
        integral += e * dt
        u = Kp * e + Ki * integral
        u_sat = float(np.clip(u, 0.0, 1.0))
        if u_sat != u:
            integral -= e * dt
        T += ((-(T - Tamb) + K * u_sat) / tau) * dt
        ts[i] = t; Ts[i] = T; us[i] = u_sat; es[i] = e; rs[i] = r
        t += dt
    return {"t": ts, "T": Ts, "u": us, "e": es, "r": rs}


def interp_of(sim, key):
    """Retorna uma função contínua f(t) por interpolação linear dos vetores simulados."""
    t = sim["t"]; y = sim[key]
    return lambda tt: np.interp(tt, t, y)


def growing_curve(axes, t_arr, y_arr, t_tracker, color=WHITE, stroke_width=3):
    """Curva que "cresce" com t_tracker, plotada por segmentos retos entre os
    pontos reais simulados — ao contrário de axes.plot(lambda ...), não
    aplica suavização Bézier, então funções em degrau ficam com transição
    reta (sem overshoot artificial de suavização)."""
    def make():
        t_now = t_tracker.get_value()
        idx = int(np.searchsorted(t_arr, t_now, side="right"))
        idx = max(idx, 2)
        return axes.plot_line_graph(
            x_values=t_arr[:idx], y_values=y_arr[:idx],
            line_color=color, add_vertex_dots=False, stroke_width=stroke_width)
    return always_redraw(make)


# ------------------------------------------------------------------
# Componentes industriais
# ------------------------------------------------------------------

def rivets(mob, inset=0.14):
    """Pequenos rebites nos quatro cantos, para dar cara de chapa metálica."""
    pts = [mob.get_corner(c) for c in (UL, UR, DL, DR)]
    offs = [DR, DL, UR, UL]
    return VGroup(*[
        Dot(radius=0.045, color=STEEL_LIGHT, fill_opacity=0.9).move_to(p + o * inset)
        for p, o in zip(pts, offs)
    ])


def build_forno(temp_tracker, power_tracker, t_min=25.0, t_max=100.0,
                 width=4.2, height=3.0, label="FORNO (planta)"):
    """Forno industrial com a resistência de aquecimento DENTRO da câmara.

    - `power_tracker` (0..1) controla o brilho imediato da resistência.
    - `temp_tracker` (°C) controla o brilho ambiente da câmara e os
      instrumentos (manômetro analógico + display digital).

    Retorna um VGroup com métodos "vivos" de conexão:
    - .get_power_in(): ponto (esquerda) onde a fiação de potência entra.
    - .get_output_tap(): ponto (embaixo/direita) de onde sai y(t) para o sensor.
    """
    body = RoundedRectangle(corner_radius=0.16, width=width, height=height,
                             fill_color=HULL, fill_opacity=1,
                             stroke_color=STEEL_DARK, stroke_width=5)
    feet = VGroup(*[
        Rectangle(width=0.3, height=0.26, fill_color=PANEL_DARK, fill_opacity=1, stroke_width=0)
        .move_to(body.get_bottom() + RIGHT * dx + DOWN * 0.09)
        for dx in (-width / 2 + 0.45, width / 2 - 0.45)
    ])
    rv = rivets(body)

    # câmara (porta com visor) — ocupa a maior parte do corpo
    cavity_w, cavity_h = width * 0.58, height * 0.62
    cavity_frame = RoundedRectangle(corner_radius=0.1, width=cavity_w + 0.14, height=cavity_h + 0.14,
                                     fill_color=PANEL_DARK, fill_opacity=1,
                                     stroke_color=STEEL_DARK, stroke_width=4)
    cavity_frame.move_to(body.get_center() + LEFT * (width * 0.08))
    cavity = RoundedRectangle(corner_radius=0.06, width=cavity_w, height=cavity_h,
                               fill_color=CAVITY_BG, fill_opacity=1, stroke_width=0)
    cavity.move_to(cavity_frame)

    frac_T = lambda: (temp_tracker.get_value() - t_min) / (t_max - t_min)
    frac_P = lambda: np.clip(power_tracker.get_value(), 0.0, 1.0)

    # NOTA: ambient_glow e coil precisam continuar corretos mesmo depois que
    # o VGroup do forno for escalado/movido pela cena (ex.: malha.scale(...)
    # .move_to(...) na Cena 4). Por isso eles são criados como mobjects reais
    # (entram no VGroup e acompanham a transformação do grupo) e atualizados
    # apenas por cor/opacidade *in-place* — nunca recriados do zero a cada
    # quadro a partir de números "congelados" fora do grupo, que é o que
    # causava peças "descoladas" do forno depois de escalar/mover.
    ambient_glow = RoundedRectangle(corner_radius=0.06, width=cavity_w, height=cavity_h,
                                     stroke_width=0, fill_opacity=0).move_to(cavity)
    ambient_glow.add_updater(lambda m: m.set_fill(
        color=heat_color(frac_T()), opacity=0.55 * np.clip(frac_T(), 0, 1)))

    # resistência (serpentina) DENTRO da câmara
    n_coils = 5
    coil_span = cavity_w * 0.7
    coil = VMobject(stroke_color=PANEL_DARK, stroke_width=5)
    pts = []
    x0 = -coil_span / 2
    for i in range(n_coils * 2 + 1):
        x = x0 + coil_span * i / (n_coils * 2)
        y = 0.16 if i % 2 == 0 else -0.16
        pts.append(np.array([x, y, 0]))
    coil.set_points_smoothly(pts)
    coil.move_to(cavity)
    coil.add_updater(lambda m: m.set_stroke(
        color=heat_color(0.1 + 0.9 * frac_P()), width=5 + 5 * frac_P(), opacity=1))

    leads = VGroup(
        Line(cavity.get_left() + LEFT * 0.001, coil.get_left()),
        Line(coil.get_right(), cavity.get_right() + RIGHT * 0.001),
    ).set_stroke(color=STEEL_LIGHT, width=3)

    label_txt = Text(label, font_size=16, color=STEEL_LIGHT, weight=BOLD)
    label_txt.next_to(body, UP, buff=0.16)

    # manômetro analógico (canto superior direito do corpo)
    gauge_c_local = body.get_corner(UR) + LEFT * 0.55 + DOWN * 0.55
    gauge_face = Circle(radius=0.36, fill_color=SCREEN_BG, fill_opacity=1,
                         stroke_color=GOLD, stroke_width=2.5).move_to(gauge_c_local)
    ticks = VGroup(*[
        Line(0.27 * np.array([np.cos(a), np.sin(a), 0]),
             0.33 * np.array([np.cos(a), np.sin(a), 0]),
             stroke_color=GOLD, stroke_width=2).shift(gauge_c_local)
        for a in np.deg2rad(np.linspace(200, -20, 6))
    ])
    gauge_anchor = Dot(gauge_c_local, radius=0.001, fill_opacity=0)

    def needle_angle():
        f = np.clip(frac_T(), 0, 1)
        return np.deg2rad(200 - 220 * f)

    needle = always_redraw(lambda: Line(
        gauge_anchor.get_center(),
        gauge_anchor.get_center() + 0.29 * (gauge_face.width / 0.72) * np.array(
            [np.cos(needle_angle()), np.sin(needle_angle()), 0]),
        stroke_color=RED_ERR, stroke_width=3))
    needle_pin = Dot(gauge_c_local, radius=0.035, color=STEEL_LIGHT)

    digital_bg = RoundedRectangle(corner_radius=0.05, width=1.05, height=0.38,
                                   fill_color=SCREEN_BG, fill_opacity=1,
                                   stroke_color=GOLD, stroke_width=1.5)
    digital_bg.next_to(gauge_face, DOWN, buff=0.12)
    digital_num = DecimalNumber(temp_tracker.get_value(), num_decimal_places=1,
                                 color=GOLD, font_size=20)
    digital_num.add_updater(lambda m: m.set_value(temp_tracker.get_value()))
    digital_unit = Text("°C", font_size=15, color=GOLD)
    digital_row = VGroup(digital_num, digital_unit).arrange(RIGHT, buff=0.05)
    digital_row.add_updater(lambda m: m.move_to(digital_bg))

    # terminal de potência (onde o fio do atuador chega) — meia-altura do
    # corpo (mesma altura do centro), para que a fiação até o atuador saia
    # sempre perfeitamente horizontal.
    term_in = Dot(body.get_left() + RIGHT * 0.12, radius=0.05, color=STEEL_LIGHT)
    term_in_ring = Circle(radius=0.08, stroke_color=STEEL_LIGHT, stroke_width=2, fill_opacity=0).move_to(term_in)

    # ponto de saída do sinal medido y(t) — também na meia-altura do corpo
    term_out = Dot(body.get_right() + LEFT * 0.12, radius=0.001, fill_opacity=0)

    forno = VGroup(
        body, feet, rv, cavity_frame, cavity, ambient_glow, coil, leads,
        gauge_face, ticks, gauge_anchor, needle, needle_pin,
        digital_bg, digital_row, label_txt, term_in_ring, term_in, term_out,
    )
    forno.get_power_in = lambda: term_in.get_center()
    forno.get_output_tap = lambda: term_out.get_center()
    forno.get_cavity_left = lambda: cavity.get_left()
    return forno


def build_atuador(power_tracker, width=1.5, height=1.1, label="ATUADOR"):
    """Módulo atuador (relé de estado sólido / driver de potência): corpo
    retangular com terminais IN/OUT bem marcados, bolt de energia e barra
    de potência — para deixar claro que é um driver elétrico, não uma
    chave mecânica genérica."""
    body = RoundedRectangle(corner_radius=0.1, width=width, height=height,
                             fill_color=PANEL, fill_opacity=1,
                             stroke_color=STEEL_DARK, stroke_width=3.5)
    label_txt = Text(label, font_size=15, color=WHITE, weight=BOLD).next_to(body, UP, buff=0.1)

    # símbolo de energia: círculo com raio, universal para "potência elétrica"
    bolt_bg = Circle(radius=0.24, fill_color=SCREEN_BG, fill_opacity=1,
                      stroke_color=GOLD, stroke_width=2).move_to(body.get_center() + LEFT * width * 0.12)
    bolt = VMobject(stroke_color=GOLD, stroke_width=3, fill_color=GOLD, fill_opacity=1)
    bolt.set_points_as_corners([
        [0.06, 0.16, 0], [-0.05, 0.02, 0], [0.02, 0.02, 0],
        [-0.06, -0.16, 0], [0.05, -0.02, 0], [-0.02, -0.02, 0], [0.06, 0.16, 0],
    ])
    bolt.move_to(bolt_bg)

    bar_bg = Rectangle(width=0.2, height=0.58, fill_color=SCREEN_BG, fill_opacity=1,
                        stroke_color=STEEL_DARK, stroke_width=1.5)
    bar_bg.move_to(body.get_center() + RIGHT * (width * 0.22))
    bar_fill = always_redraw(lambda: Rectangle(
        width=0.14,
        height=max(0.005, 0.52 * np.clip(power_tracker.get_value(), 0.0, 1.0)),
        fill_color=HEAT, fill_opacity=1, stroke_width=0
    ).move_to(bar_bg.get_bottom(), aligned_edge=DOWN).shift(UP * 0.03))
    bar_label = Text("P", font_size=11, color=STEEL_LIGHT).next_to(bar_bg, DOWN, buff=0.05)

    term_in = Dot(body.get_left(), radius=0.001, fill_opacity=0)
    term_out = Dot(body.get_right(), radius=0.001, fill_opacity=0)

    atuador = VGroup(body, bolt_bg, bolt, bar_bg, bar_fill, bar_label, label_txt, term_in, term_out)
    atuador.get_in = lambda: term_in.get_center()
    atuador.get_out = lambda: term_out.get_center()
    return atuador


def build_sensor(width=1.15, height=0.62, label="SENSOR"):
    """Sensor de temperatura (termopar) + transmissor — corpo simples com
    pontos de conexão vivos (entrada da câmara, saída y(t))."""
    box = RoundedRectangle(corner_radius=0.07, width=width, height=height,
                            fill_color=PANEL, fill_opacity=1,
                            stroke_color=GREEN_OK, stroke_width=3)
    label_txt = Text(label, font_size=13, color=WHITE, weight=BOLD).next_to(box, UP, buff=0.08)
    led = Dot(radius=0.045, color=GREEN_OK).move_to(box.get_corner(UR) + DL * 0.13)
    term_in = Dot(box.get_left(), radius=0.001, fill_opacity=0)
    term_out = Dot(box.get_right(), radius=0.001, fill_opacity=0)
    term_bottom = Dot(box.get_bottom(), radius=0.001, fill_opacity=0)

    sensor = VGroup(box, led, label_txt, term_in, term_out, term_bottom)
    sensor.get_in = lambda: term_in.get_center()
    sensor.get_out = lambda: term_out.get_center()
    sensor.get_bottom_pt = lambda: term_bottom.get_center()
    return sensor


def build_controlador(width=2.0, height=1.4, texto="PID", label="CONTROLADOR"):
    """Controlador (CLP) com tela e LED de status."""
    body = RoundedRectangle(corner_radius=0.1, width=width, height=height,
                             fill_color=PANEL, fill_opacity=1,
                             stroke_color=STEEL_DARK, stroke_width=4)
    label_txt = Text(label, font_size=15, color=WHITE, weight=BOLD).next_to(body, UP, buff=0.1)

    screen = RoundedRectangle(corner_radius=0.05, width=width * 0.6, height=height * 0.42,
                               fill_color=SCREEN_BG, fill_opacity=1,
                               stroke_color=BLUE_CTRL, stroke_width=1.5)
    screen.move_to(body.get_center() + UP * height * 0.1)
    screen_text = Text(texto, font_size=19, color=BLUE_CTRL, weight=BOLD).move_to(screen)

    knobs = VGroup(*[
        Circle(radius=0.08, fill_color=SCREEN_BG, fill_opacity=1, stroke_color=STEEL_LIGHT, stroke_width=2)
        .move_to(body.get_bottom() + UP * 0.24 + RIGHT * dx)
        for dx in np.linspace(-width * 0.25, width * 0.25, 3)
    ])
    status_led = Dot(radius=0.05, color=GREEN_OK).move_to(body.get_corner(UL) + DR * 0.16)

    term_in = Dot(body.get_left(), radius=0.001, fill_opacity=0)
    term_out = Dot(body.get_right(), radius=0.001, fill_opacity=0)

    ctrl = VGroup(body, screen, screen_text, knobs, status_led, label_txt, term_in, term_out)
    ctrl.get_in = lambda: term_in.get_center()
    ctrl.get_out = lambda: term_out.get_center()
    return ctrl


def build_comparador(radius=0.34):
    """Junção somadora clássica: entrada + à esquerda (horizontal, para a
    referência), entrada − embaixo (vertical, para a realimentação), saída
    à direita (para o erro)."""
    circle = Circle(radius=radius, fill_color=PANEL_DARK, fill_opacity=1,
                     stroke_color=RED_ERR, stroke_width=3)
    cross = VGroup(
        Line(UP * radius * 0.5, DOWN * radius * 0.5),
        Line(LEFT * radius * 0.5, RIGHT * radius * 0.5),
    ).set_stroke(color=STEEL_LIGHT, width=1, opacity=0.35)
    plus = Text("+", font_size=20, color=GOLD).move_to(
        circle.get_center() + rotate_vector(RIGHT, 130 * DEGREES) * radius * 0.55)
    minus = Text("−", font_size=22, color=RED_ERR).move_to(
        circle.get_center() + DOWN * radius * 0.55 + RIGHT * radius * 0.4)

    left_pt = Dot(circle.get_left(), radius=0.001, fill_opacity=0)
    right_pt = Dot(circle.get_right(), radius=0.001, fill_opacity=0)
    bottom_pt = Dot(circle.get_bottom(), radius=0.001, fill_opacity=0)

    comp = VGroup(circle, cross, plus, minus, left_pt, right_pt, bottom_pt)
    comp.get_left_pt = lambda: left_pt.get_center()
    comp.get_right_pt = lambda: right_pt.get_center()
    comp.get_bottom_pt = lambda: bottom_pt.get_center()
    return comp


def build_fonte(radius=0.26):
    """Símbolo clássico de fonte de tensão CA (círculo com um traço
    senoidal), usado para representar a rede elétrica que alimenta o
    atuador — sem precisar de texto."""
    circle = Circle(radius=radius, fill_color=PANEL_DARK, fill_opacity=1,
                     stroke_color=STEEL_LIGHT, stroke_width=3)
    wave = ParametricFunction(
        lambda t: np.array([t, 0.5 * radius * np.sin(t * PI / (0.55 * radius)), 0]),
        t_range=[-0.55 * radius, 0.55 * radius], stroke_color=STEEL_LIGHT, stroke_width=2.5)
    left_pt = Dot(circle.get_left(), radius=0.001, fill_opacity=0)
    right_pt = Dot(circle.get_right(), radius=0.001, fill_opacity=0)
    fonte = VGroup(circle, wave, left_pt, right_pt)
    fonte.get_left_pt = lambda: left_pt.get_center()
    fonte.get_right_pt = lambda: right_pt.get_center()
    return fonte


def load_ufpa_logo(height=1.0):
    """Carrega o brasão oficial da UFPA (assets/ufpa_logo_crop.png,
    baixado de ascom.ufpa.br) como ImageMobject."""
    import os
    path = os.path.join(os.path.dirname(__file__), "assets", "ufpa_logo_crop.png")
    logo = ImageMobject(path)
    logo.height = height
    return logo


def polyline_path(*points):
    """Caminho poligonal (estilo diagrama de blocos) por N pontos."""
    path = VMobject()
    path.set_points_as_corners(list(points))
    return path


def signal_axes(x_range, y_range, x_length, y_length, **kwargs):
    ax = Axes(x_range=x_range, y_range=y_range, x_length=x_length, y_length=y_length,
              axis_config={"stroke_color": STEEL_LIGHT, "stroke_width": 2,
                            "tip_length": 0.1, "tip_width": 0.1,
                            "include_ticks": True, "font_size": 14},
              tips=True, **kwargs)
    ax.set_color(STEEL_LIGHT)
    return ax
