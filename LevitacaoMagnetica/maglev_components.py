"""
Componentes visuais reutilizáveis (estilo industrial) e simulação da planta
de levitação magnética para o vídeo didático de introdução a sistemas de
controle: uma esfera de aço suspensa por um eletroímã.

Convenções:
- Posição x(t) = distância entre a face do eletroímã e o centro da esfera
  ("gap", em cm de cena). Quanto MENOR x, mais perto do ímã (mais "levitada").
- Sinal de controle / corrente da bobina i(t), em ampères de cena.
- Tempo de simulação em "segundos de cena": 1 s de simulação ≈ 1 s de
  animação (run_time), como em ControleTemperatura/industrial_components.py.
- A planta é NÃO LINEAR e instável em malha aberta ao redor de qualquer
  ponto de equilíbrio: F_mag = K·i²/x² (atração, cresce quando x diminui),
  contra a gravidade m·g. Pequenas perturbações crescem exponencialmente
  sem realimentação — é exatamente isso que a Cena 1 demonstra.
- Todo componente que expõe pontos de conexão (entrada/saída) o faz por
  meio de métodos/lambdas que leem a posição atual de um sub-mobject já
  incluído no grupo — nunca de coordenadas numéricas "congeladas" antes de
  escalar/mover o grupo (evita fios/setas desalinhados).
"""

from manim import *
import numpy as np

# ------------------------------------------------------------------
# Paleta (mesma do ControleTemperatura, derivada de TemaRTx.scss)
# ------------------------------------------------------------------
STEEL       = "#4A6FA5"   # accent
STEEL_DARK  = "#1B365D"   # primary
STEEL_LIGHT = "#9DB2D6"
GOLD        = "#E8C547"   # highlight-color
HEAT        = "#E65100"   # warning-color (aqui: intensidade da corrente/bobina)
GREEN_OK    = "#3FA34D"
RED_ERR     = "#C0455A"   # vermelho-ufpa (clareado)
BLUE_CTRL   = "#2AA1D6"   # info
PANEL       = "#3A414C"
PANEL_DARK  = "#20242B"
SCREEN_BG   = "#0B0F14"
HULL        = "#2B303A"
CAVITY_BG   = "#0E0B09"
BALL_COLOR  = "#C9CFD8"   # esfera de aço


def heat_color(frac):
    """Mapeia fração de corrente/potência [0,1] para uma cor de brasa: cinza -> laranja -> dourado."""
    frac = float(np.clip(frac, 0.0, 1.0))
    if frac < 0.5:
        return interpolate_color(ManimColor(PANEL_DARK), ManimColor(HEAT), frac / 0.5)
    return interpolate_color(ManimColor(HEAT), ManimColor(GOLD), (frac - 0.5) / 0.5)


# ------------------------------------------------------------------
# Simulação da planta (esfera + eletroímã) — 2a ordem, não linear
# ------------------------------------------------------------------
# m·x'' = m·g - K·i²/x²      (x = gap ímã-esfera; cresce quando a esfera cai)
#
# Em torno de qualquer equilíbrio (x0, i0) com K·i0² = m·g·x0², a planta
# linearizada tem um polo estável e um instável (sela): é fisicamente
# impossível levitar em malha aberta.

M_BOLA = 1.0
GRAV = 9.8
K_MAG = 1.0
X0 = 2.0                                  # gap de equilíbrio (cm de cena)
I0 = float(np.sqrt(M_BOLA * GRAV * X0 ** 2 / K_MAG))   # corrente de equilíbrio em x0
I_MAX = 15.0
X_MIN, X_MAX = 0.3, 4.0                   # colisão com o ímã / com o chão


def simulate_open_loop(t_end=6.0, dt=0.001, perturb_t=1.0, v_kick=0.02, x_init=X0):
    """Malha aberta: corrente travada em I0 (o valor que equilibra a
    gravidade exatamente em x_init). Uma pequena perturbação de velocidade
    em perturb_t basta para a esfera divergir — cai no chão ou gruda no ímã.
    Interrompe a simulação no instante da colisão."""
    n = int(t_end / dt)
    t = 0.0
    x = x_init
    v = 0.0
    kicked = False
    ts = np.empty(n); xs = np.empty(n); us = np.empty(n)
    last = n
    for k in range(n):
        if t >= perturb_t and not kicked:
            v += v_kick
            kicked = True
        i = I0
        F = K_MAG * i ** 2 / max(x, 0.01) ** 2
        a = GRAV - F / M_BOLA
        v += a * dt
        x += v * dt
        ts[k] = t; xs[k] = x; us[k] = i
        t += dt
        if x <= X_MIN or x >= X_MAX:
            last = k + 1
            break
    return {"t": ts[:last], "x": xs[:last], "u": us[:last]}


def simulate_closed_loop(t_end=14.0, dt=0.001, r1=X0, r2=1.3, t_step=6.0,
                          Kp=40.0, Ki=6.0, Kd=8.0, x_init=X0, perturb_t=None, v_kick=0.3):
    """Malha fechada com controlador PID (o termo derivativo é essencial:
    a planta é instável e P puro não basta para estabilizá-la). Erro
    definido como e = x - r (positivo quando a esfera está mais longe do
    ímã que o desejado) para que Kp>0 aumente a corrente corretamente;
    os vetores retornados usam a convenção clássica e(t) = r(t) - x(t)."""
    n = int(t_end / dt)
    t = 0.0
    x = x_init
    v = 0.0
    integral = 0.0
    e_prev = None
    kicked = False
    ts = np.empty(n); xs = np.empty(n); us = np.empty(n)
    es = np.empty(n); rs = np.empty(n)
    last = n
    for k in range(n):
        r = r1 if t < t_step else r2
        e = x - r
        de = 0.0 if e_prev is None else (e - e_prev) / dt
        integral += e * dt
        i_unsat = I0 + Kp * e + Ki * integral + Kd * de
        i = float(np.clip(i_unsat, 0.0, I_MAX))
        if i != i_unsat:
            integral -= e * dt  # anti-windup
        if perturb_t is not None and t >= perturb_t and not kicked:
            v += v_kick
            kicked = True
        F = K_MAG * i ** 2 / max(x, 0.01) ** 2
        a = GRAV - F / M_BOLA
        v += a * dt
        x += v * dt
        ts[k] = t; xs[k] = x; us[k] = i; es[k] = -e; rs[k] = r
        e_prev = e
        t += dt
        if x <= X_MIN or x >= X_MAX:
            last = k + 1
            break
    return {"t": ts[:last], "x": xs[:last], "u": us[:last], "e": es[:last], "r": rs[:last]}


def interp_of(sim, key):
    """Retorna uma função contínua f(t) por interpolação linear dos vetores simulados."""
    t = sim["t"]; y = sim[key]
    return lambda tt: np.interp(tt, t, y)


def growing_curve(axes, t_arr, y_arr, t_tracker, color=WHITE, stroke_width=3):
    """Curva que "cresce" com t_tracker, plotada por segmentos retos entre os
    pontos reais simulados (sem suavização Bézier, para não criar overshoot
    artificial em transições rápidas)."""
    def make():
        t_now = t_tracker.get_value()
        idx = int(np.searchsorted(t_arr, t_now, side="right"))
        idx = max(idx, 2)
        idx = min(idx, len(t_arr))
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


def build_planta_maglev(pos_tracker, power_tracker, x_min=X_MIN, x_max=X_MAX, x_scale=0.42,
                         width=1.9, height=3.3, label="ELETROÍMÃ + ESFERA (planta)"):
    """Planta de levitação magnética: eletroímã fixo no topo, esfera de aço
    deslizando por uma guia vertical, chão/batente embaixo.

    - `power_tracker` (corrente, em A) controla o brilho do eletroímã.
    - `pos_tracker` (gap x, em cm de cena) controla a altura da esfera:
      quanto menor x, mais perto do ímã.

    Retorna um VGroup com métodos "vivos" de conexão:
    - .get_power_in(): ponto (esquerda do núcleo) onde a fiação de corrente entra.
    - .get_output_tap(): ponto fixo na carcaça onde o sensor "enxerga" a esfera.
    """
    core_w, core_h = width * 0.8, 0.5
    core = RoundedRectangle(corner_radius=0.06, width=core_w, height=core_h,
                             fill_color=HULL, fill_opacity=1,
                             stroke_color=STEEL_DARK, stroke_width=5)
    core.move_to(UP * (height / 2 - core_h / 2))
    rv = rivets(core, inset=0.08)

    frac_i = lambda: np.clip(power_tracker.get_value() / I_MAX, 0.0, 1.0)
    frac_x = lambda: 1.0 - np.clip((pos_tracker.get_value() - x_min) / (x_max - x_min), 0.0, 1.0)

    # bobina (serpentina) sob o núcleo do ímã, brilha com a corrente
    n_coils = 6
    coil_span = core_w * 0.82
    coil = VMobject(stroke_color=PANEL_DARK, stroke_width=4)
    pts = []
    x0c = -coil_span / 2
    for i in range(n_coils * 2 + 1):
        xx = x0c + coil_span * i / (n_coils * 2)
        yy = 0.07 if i % 2 == 0 else -0.07
        pts.append(np.array([xx, yy, 0]))
    coil.set_points_smoothly(pts)
    coil.move_to(core.get_bottom() + UP * 0.02)
    coil.add_updater(lambda m: m.set_stroke(
        color=heat_color(0.15 + 0.85 * frac_i()), width=4 + 4 * frac_i(), opacity=1))

    pole_glow = RoundedRectangle(corner_radius=0.04, width=core_w * 0.86, height=0.1,
                                  stroke_width=0, fill_opacity=0)
    pole_glow.move_to(core.get_bottom())
    pole_glow.add_updater(lambda m: m.set_fill(color=heat_color(frac_i()), opacity=0.85 * frac_i()))

    label_txt = Text(label, font_size=15, color=STEEL_LIGHT, weight=BOLD)
    label_txt.next_to(core, UP, buff=0.14)

    # guia vertical (trilho) + chão/batente
    rail_top = core.get_bottom()
    rail_len = (x_max - x_min) * x_scale + 0.9
    rail = DashedLine(rail_top, rail_top + DOWN * rail_len,
                       stroke_color=STEEL_LIGHT, stroke_width=1.5, dash_length=0.08)
    floor = Line(rail.get_end() + LEFT * 0.4, rail.get_end() + RIGHT * 0.4,
                 stroke_color=STEEL_LIGHT, stroke_width=4)

    # NOTE: a esfera precisa continuar alinhada ao trilho mesmo depois que o
    # VGroup da planta for escalado/movido pela cena (ex.: malha.scale(...)
    # .move_to(...) na Cena 4). Por isso a posição vertical NÃO é calculada a
    # partir de coordenadas numéricas "congeladas" (rail_top, x_scale) — em
    # vez disso, dois âncoras (Dots) marcando x_min e x_max são inseridos no
    # próprio grupo, e a cada quadro a esfera interpola entre as posições
    # ATUAIS (já transformadas) desses âncoras.
    ball_radius = 0.22
    anchor_min = Dot(rail_top + DOWN * (x_min * x_scale + ball_radius), radius=0.001, fill_opacity=0)
    anchor_max = Dot(rail_top + DOWN * (x_max * x_scale + ball_radius), radius=0.001, fill_opacity=0)

    def ball_center():
        frac = np.clip((pos_tracker.get_value() - x_min) / (x_max - x_min), 0.0, 1.0)
        return interpolate(anchor_min.get_center(), anchor_max.get_center(), frac)

    ball = always_redraw(lambda: VGroup(
        Circle(radius=ball_radius, fill_color=BALL_COLOR, fill_opacity=1,
               stroke_color=STEEL_DARK, stroke_width=2).move_to(ball_center()),
        Circle(radius=ball_radius * 0.42, fill_color=WHITE, fill_opacity=0.55,
               stroke_width=0).move_to(ball_center() + UP * 0.06 + LEFT * 0.06),
    ))

    # ponto fixo na carcaça onde o "olho" do sensor mede a posição (altura
    # de referência x0, no meio do curso — não acompanha a esfera)
    tap_y = rail_top[1] - (X0 * x_scale + ball_radius)
    term_out = Dot(np.array([rail.get_end()[0] + 0.4, tap_y, 0]), radius=0.001, fill_opacity=0)
    term_in = Dot(core.get_left(), radius=0.001, fill_opacity=0)

    planta = VGroup(core, rv, coil, pole_glow, rail, floor, anchor_min, anchor_max,
                     ball, label_txt, term_in, term_out)
    planta.get_power_in = lambda: term_in.get_center()
    planta.get_output_tap = lambda: term_out.get_center()
    return planta


def build_atuador(power_tracker, width=1.5, height=1.1, label="ATUADOR", i_max=I_MAX):
    """Driver de corrente para a bobina: corpo retangular com terminais
    IN/OUT, símbolo de energia e barra indicando a corrente entregue."""
    body = RoundedRectangle(corner_radius=0.1, width=width, height=height,
                             fill_color=PANEL, fill_opacity=1,
                             stroke_color=STEEL_DARK, stroke_width=3.5)
    label_txt = Text(label, font_size=15, color=WHITE, weight=BOLD).next_to(body, UP, buff=0.1)

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
        height=max(0.005, 0.52 * np.clip(power_tracker.get_value() / i_max, 0.0, 1.0)),
        fill_color=HEAT, fill_opacity=1, stroke_width=0
    ).move_to(bar_bg.get_bottom(), aligned_edge=DOWN).shift(UP * 0.03))
    bar_label = Text("i", font_size=11, color=STEEL_LIGHT).next_to(bar_bg, DOWN, buff=0.05)

    term_in = Dot(body.get_left(), radius=0.001, fill_opacity=0)
    term_out = Dot(body.get_right(), radius=0.001, fill_opacity=0)

    atuador = VGroup(body, bolt_bg, bolt, bar_bg, bar_fill, bar_label, label_txt, term_in, term_out)
    atuador.get_in = lambda: term_in.get_center()
    atuador.get_out = lambda: term_out.get_center()
    return atuador


def build_sensor(width=1.15, height=0.62, label="SENSOR"):
    """Sensor ótico de posição (par emissor/receptor infravermelho) +
    transmissor — corpo simples com pontos de conexão vivos."""
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
    """Símbolo clássico de fonte de tensão CC/CA, usado para representar a
    rede elétrica que alimenta o atuador — sem precisar de texto."""
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
