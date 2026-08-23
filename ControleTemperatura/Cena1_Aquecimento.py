"""Cena 1 — Atuação e aquecimento: o atuador entrega potência à resistência,
que fica DENTRO do forno e o aquece. Planta em malha aberta (sem controle)."""

from manim import *
import numpy as np
from industrial_components import *

config.background_color = "#12161c"


class Cena1_Aquecimento(Scene):
    def construct(self):
        logo = load_ufpa_logo(height=1.5)
        titulo = Text("Sistemas de Controle", font_size=38, color=WHITE, weight=BOLD)
        subtitulo = Text("Controle de temperatura de um forno industrial",
                          font_size=22, color=GOLD)
        autor = Text("Prof. Dr. Raphael Teixeira", font_size=20, color=STEEL_LIGHT)
        textos = VGroup(titulo, subtitulo, autor).arrange(DOWN, buff=0.25)
        abertura = Group(logo, textos).arrange(RIGHT, buff=0.7).move_to(ORIGIN)

        self.play(FadeIn(logo, shift=UP * 0.2),
                   FadeIn(titulo, shift=UP * 0.2), FadeIn(subtitulo, shift=UP * 0.2),
                   FadeIn(autor, shift=UP * 0.2), run_time=0.9)
        self.wait(1.2)
        self.play(FadeOut(abertura), run_time=0.6)

        cabecalho = Text("1. Atuação e aquecimento da planta", font_size=28,
                          color=WHITE, weight=BOLD).to_edge(UP, buff=0.15)
        self.play(FadeIn(cabecalho, shift=UP * 0.15))

        sim = simulate_open_loop(t_end=10.0, t_on=1.0)
        T_of = interp_of(sim, "T")
        u_of = interp_of(sim, "u")
        t_arr, T_arr, u_arr = sim["t"], sim["T"], sim["u"]
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

        # -------- diagrama: atuador -> forno (resistência já dentro dele) --------
        # NOTA: next_to() centraliza pela caixa delimitadora de cada bloco,
        # não pelo terminal real — como os rótulos (“ATUADOR” em cima, “P”
        # embaixo) não têm a mesma altura, a caixa fica levemente
        # assimétrica e o fio saía torto. Por isso corrigimos a posição
        # vertical de cada bloco pelo terminal de ligação real, garantindo
        # fios sempre perfeitamente horizontais.
        atuador = build_atuador(power_tracker)
        forno = build_forno(temp_tracker, power_tracker, width=4.4, height=3.1)
        atuador.next_to(forno, LEFT, buff=1.3)
        atuador.shift(UP * (forno.get_power_in()[1] - atuador.get_out()[1]))

        fio = always_redraw(lambda: Line(
            atuador.get_out(), forno.get_power_in(), stroke_color=STEEL_LIGHT, stroke_width=3))

        fonte = build_fonte()
        fonte.next_to(atuador, LEFT, buff=0.6)
        fonte.shift(UP * (atuador.get_in()[1] - fonte.get_right_pt()[1]))
        fio_fonte = Line(fonte.get_right_pt(), atuador.get_in(),
                          stroke_color=STEEL_LIGHT, stroke_width=3)

        diagrama = VGroup(fonte, fio_fonte, atuador, forno, fio)
        diagrama.move_to(UP * 1.55)

        self.play(LaggedStart(
            GrowFromCenter(fonte), Create(fio_fonte),
            GrowFromCenter(atuador), Create(fio),
            FadeIn(forno, shift=LEFT * 0.3),
            lag_ratio=0.35, run_time=2.6
        ))
        self.wait(0.6)

        # -------- gráfico da temperatura subindo --------
        eixo = signal_axes(x_range=[0, t_max, 2], y_range=[20, 90, 20], x_length=9.0, y_length=2.6)
        eixo.move_to(DOWN * 1.85)
        eixo_labels = eixo.get_axis_labels(x_label=Text("t (s)", font_size=16),
                                            y_label=Text("T (°C)", font_size=16))
        eixo_labels[1].next_to(eixo.y_axis.get_top(), LEFT, buff=0.12)

        curva_T = growing_curve(eixo, t_arr, T_arr, t_tracker, color=HEAT, stroke_width=4)
        ponto_T = always_redraw(lambda: Dot(
            eixo.c2p(t_tracker.get_value(), T_of(t_tracker.get_value())), radius=0.05, color=GOLD))

        graf_titulo = Text("Resposta da planta em malha aberta (sem controle)",
                            font_size=16, color=WHITE)
        graf_titulo.next_to(eixo, UP, buff=0.15)

        self.play(FadeIn(graf_titulo), Create(eixo), FadeIn(eixo_labels))
        self.add(curva_T, ponto_T)
        self.wait(0.2)

        self.play(t_tracker.animate.set_value(t_max), run_time=9.0, rate_func=linear)
        self.wait(0.6)

        conclusao = Text("Sem controle, a temperatura sobe até um patamar e não segue nenhuma referência.",
                          font_size=16, color=WHITE, t2c={"referência": GOLD})
        conclusao.to_edge(DOWN, buff=0.25)
        self.play(FadeIn(conclusao, shift=UP * 0.1))
        self.wait(1.8)
        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.2)
