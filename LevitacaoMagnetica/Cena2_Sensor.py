"""Cena 2 — Sensor e medição da posição: um par ótico (emissor/receptor
infravermelho) mede a posição da esfera e o transmissor converte essa
medida no sinal medido y(t). A informação flui da planta PARA o sensor
(não o contrário) — ainda em malha aberta, mesmo com a esfera divergindo."""

from manim import *
import numpy as np
from maglev_components import *

config.background_color = "#12161c"


class Cena2_Sensor(Scene):
    def construct(self):
        cabecalho = Text("2. Sensor e medição da posição", font_size=28,
                          color=WHITE, weight=BOLD).to_edge(UP, buff=0.15)
        self.play(FadeIn(cabecalho, shift=UP * 0.15))

        sim = simulate_open_loop(t_end=6.0, perturb_t=1.0, v_kick=0.02)
        x_of = interp_of(sim, "x")
        u_of = interp_of(sim, "u")
        t_arr, x_arr, u_arr = sim["t"], sim["x"], sim["u"]
        # sinal medido: mesma posição com um pequeno atraso de sensor
        y_arr = np.interp(t_arr - 0.15, t_arr, x_arr, left=x_arr[0])
        t_max = t_arr[-1]

        pos_tracker = ValueTracker(x_of(0))
        power_tracker = ValueTracker(u_of(0))
        t_tracker = ValueTracker(0.0)

        def sync(_m, dt):
            tt = t_tracker.get_value()
            pos_tracker.set_value(x_of(tt))
            power_tracker.set_value(u_of(tt))
        ghost = Mobject()
        ghost.add_updater(sync)
        self.add(ghost)

        # -------- planta (compacta) + sensor, lado a lado --------
        planta = build_planta_maglev(pos_tracker, power_tracker, width=1.5, height=2.5).scale(0.85)
        sensor = build_sensor()
        sensor.next_to(planta, RIGHT, buff=1.7)
        sensor.shift(UP * (planta.get_output_tap()[1] - sensor.get_in()[1]))
        grupo = VGroup(planta, sensor).move_to(UP * 1.55)

        self.play(FadeIn(planta, shift=LEFT * 0.2), run_time=1.0)

        # feixe ótico: sai do sensor, atravessa até a carcaça na altura de referência
        probe_tip = planta.get_output_tap() + RIGHT * 0.05
        probe = DashedLine(sensor.get_in(), probe_tip, stroke_color=RED_ERR, stroke_width=2.5, dash_length=0.06)
        probe_bulb = Circle(radius=0.05, fill_color=RED_ERR, fill_opacity=1, stroke_width=0).move_to(probe_tip)

        self.play(GrowFromCenter(sensor), run_time=0.6)
        self.play(Create(probe), FadeIn(probe_bulb), run_time=0.8)
        self.wait(0.8)

        # saída do sensor: y(t), segue adiante (para o comparador, próxima cena)
        y_seta = Arrow(sensor.get_out(), sensor.get_out() + RIGHT * 1.0, color=GREEN_OK,
                        buff=0.05, stroke_width=3, max_tip_length_to_length_ratio=0.25)
        y_label = MathTex("y(t)", color=GREEN_OK, font_size=30).next_to(y_seta, RIGHT, buff=0.1)
        self.play(GrowArrow(y_seta), FadeIn(y_label, shift=RIGHT * 0.1))
        self.wait(0.8)

        # -------- gráfico: posição real x sinal medido --------
        eixo = signal_axes(x_range=[0, t_max, 1], y_range=[X_MIN, X_MAX, 1], x_length=9.0, y_length=2.5)
        eixo.move_to(DOWN * 1.95)
        eixo_labels = eixo.get_axis_labels(x_label=Text("t (s)", font_size=14),
                                            y_label=Text("x (cm)", font_size=14))
        eixo_labels[1].next_to(eixo.y_axis.get_top(), LEFT, buff=0.1)
        graf_titulo = Text("Posição real  ×  sinal medido pelo sensor", font_size=15, color=WHITE)
        graf_titulo.next_to(eixo, UP, buff=0.12)

        curva_real = growing_curve(eixo, t_arr, x_arr, t_tracker, color=BLUE_CTRL, stroke_width=4)
        curva_medida = growing_curve(eixo, t_arr, y_arr, t_tracker, color=GREEN_OK, stroke_width=3)

        legenda = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.3, stroke_color=BLUE_CTRL, stroke_width=4),
                   Text("x real", font_size=13, color=WHITE)).arrange(RIGHT, buff=0.08),
            VGroup(Line(ORIGIN, RIGHT * 0.3, stroke_color=GREEN_OK, stroke_width=4),
                   Text("y(t) medido", font_size=13, color=WHITE)).arrange(RIGHT, buff=0.08),
        ).arrange(RIGHT, buff=0.4)
        legenda.next_to(eixo, DOWN, buff=0.12)

        self.play(FadeIn(graf_titulo), Create(eixo), FadeIn(eixo_labels), FadeIn(legenda))
        self.add(curva_real, curva_medida)

        self.play(t_tracker.animate.set_value(t_max), run_time=11.0, rate_func=linear)
        self.wait(0.6)

        conclusao = Text("O sensor converte posição em sinal elétrico y(t), com um pequeno atraso.",
                          font_size=16, color=WHITE, t2c={"y(t)": GREEN_OK})
        conclusao.to_edge(DOWN, buff=0.15)
        self.play(FadeIn(conclusao, shift=UP * 0.1))
        self.wait(2.8)
        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.2)
