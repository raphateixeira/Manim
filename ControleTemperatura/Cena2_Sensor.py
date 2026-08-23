"""Cena 2 — Sensor e medição: o termopar mede a temperatura da planta e o
transmissor converte essa medida no sinal medido y(t). A informação flui
do forno PARA o sensor (não o contrário)."""

from manim import *
import numpy as np
from industrial_components import *

config.background_color = "#12161c"


class Cena2_Sensor(Scene):
    def construct(self):
        cabecalho = Text("2. Sensor e medição da temperatura", font_size=28,
                          color=WHITE, weight=BOLD).to_edge(UP, buff=0.15)
        self.play(FadeIn(cabecalho, shift=UP * 0.15))

        sim = simulate_open_loop(t_end=10.0, t_on=1.0)
        T_of = interp_of(sim, "T")
        u_of = interp_of(sim, "u")
        t_arr, T_arr, u_arr = sim["t"], sim["T"], sim["u"]
        # sinal medido: mesma temperatura com um pequeno atraso de sensor
        y_arr = np.interp(t_arr - 0.4, t_arr, T_arr, left=T_arr[0])
        t_max = t_arr[-1]

        temp_tracker = ValueTracker(T_of(0))
        power_tracker = ValueTracker(u_of(0))
        t_tracker = ValueTracker(0.0)

        def sync(_m, dt):
            tt = t_tracker.get_value()
            temp_tracker.set_value(T_of(tt))
            power_tracker.set_value(u_of(tt))
        ghost = Mobject()
        ghost.add_updater(sync)
        self.add(ghost)

        # -------- forno (compacto) + sensor, lado a lado, centralizados --------
        # NOTA: next_to() centraliza pela caixa delimitadora, não pelo
        # terminal real — o rótulo "SENSOR" (só em cima, sem nada embaixo
        # para compensar) desloca essa caixa para cima. Por isso realinhamos
        # pelo ponto de conexão de fato, garantindo a ligação horizontal.
        forno = build_forno(temp_tracker, power_tracker, width=3.6, height=2.6).scale(0.82)
        sensor = build_sensor()
        sensor.next_to(forno, RIGHT, buff=1.7)
        sensor.shift(UP * (forno.get_output_tap()[1] - sensor.get_in()[1]))
        grupo = VGroup(forno, sensor).move_to(UP * 1.55)

        self.play(FadeIn(forno, shift=LEFT * 0.2), run_time=1.0)

        # sonda física: entra pela parede do forno (thermowell), toca a câmara
        probe_tip = forno.get_output_tap() + RIGHT * 0.05
        probe = Line(sensor.get_in(), probe_tip, stroke_color=STEEL_LIGHT, stroke_width=4)
        probe_bulb = Circle(radius=0.05, fill_color=RED_ERR, fill_opacity=1, stroke_width=0).move_to(probe_tip)

        self.play(GrowFromCenter(sensor), run_time=0.6)
        self.play(Create(probe), FadeIn(probe_bulb), run_time=0.8)
        self.wait(0.5)

        # saída do sensor: y(t), segue adiante (para o controlador, próxima cena)
        # — a seta verde marca só isso: o sinal MEDIDO que sai do sensor.
        y_seta = Arrow(sensor.get_out(), sensor.get_out() + RIGHT * 1.0, color=GREEN_OK,
                        buff=0.05, stroke_width=3, max_tip_length_to_length_ratio=0.25)
        y_label = MathTex("y(t)", color=GREEN_OK, font_size=30).next_to(y_seta, RIGHT, buff=0.1)
        self.play(GrowArrow(y_seta), FadeIn(y_label, shift=RIGHT * 0.1))
        self.wait(0.6)

        # -------- gráfico: temperatura real x sinal medido --------
        eixo = signal_axes(x_range=[0, t_max, 2], y_range=[20, 90, 20], x_length=9.0, y_length=2.5)
        eixo.move_to(DOWN * 1.95)
        eixo_labels = eixo.get_axis_labels(x_label=Text("t (s)", font_size=14),
                                            y_label=Text("T (°C)", font_size=14))
        eixo_labels[1].next_to(eixo.y_axis.get_top(), LEFT, buff=0.1)
        graf_titulo = Text("Temperatura real  ×  sinal medido pelo sensor", font_size=15, color=WHITE)
        graf_titulo.next_to(eixo, UP, buff=0.12)

        curva_real = growing_curve(eixo, t_arr, T_arr, t_tracker, color=HEAT, stroke_width=4)
        curva_medida = growing_curve(eixo, t_arr, y_arr, t_tracker, color=GREEN_OK, stroke_width=3)

        legenda = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.3, stroke_color=HEAT, stroke_width=4),
                   Text("T real", font_size=13, color=WHITE)).arrange(RIGHT, buff=0.08),
            VGroup(Line(ORIGIN, RIGHT * 0.3, stroke_color=GREEN_OK, stroke_width=4),
                   Text("y(t) medido", font_size=13, color=WHITE)).arrange(RIGHT, buff=0.08),
        ).arrange(RIGHT, buff=0.4)
        legenda.next_to(eixo, DOWN, buff=0.12)

        self.play(FadeIn(graf_titulo), Create(eixo), FadeIn(eixo_labels), FadeIn(legenda))
        self.add(curva_real, curva_medida)

        self.play(t_tracker.animate.set_value(t_max), run_time=9.0, rate_func=linear)
        self.wait(0.6)

        conclusao = Text("O sensor converte temperatura em sinal elétrico y(t), com um pequeno atraso.",
                          font_size=16, color=WHITE, t2c={"y(t)": GREEN_OK})
        conclusao.to_edge(DOWN, buff=0.15)
        self.play(FadeIn(conclusao, shift=UP * 0.1))
        self.wait(1.8)
        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.2)
