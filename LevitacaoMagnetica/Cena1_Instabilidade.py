"""Cena 1 — Atuação e instabilidade da planta: o driver entrega uma
corrente constante ao eletroímã, que mantém a esfera EXATAMENTE no ponto
de equilíbrio (a força magnética cancela a gravidade). Ainda assim, em
malha aberta, uma perturbação mínima basta para a esfera divergir — cair
no chão ou colar no ímã. É a instabilidade que motiva o controle."""

from manim import *
import numpy as np
from maglev_components import *

config.background_color = "#12161c"


class Cena1_Instabilidade(Scene):
    def construct(self):
        logo = load_ufpa_logo(height=1.5)
        titulo = Text("Sistemas de Controle", font_size=38, color=WHITE, weight=BOLD)
        subtitulo = Text("Levitação magnética de uma esfera", font_size=22, color=GOLD)
        autor = Text("Prof. Dr. Raphael Teixeira", font_size=20, color=STEEL_LIGHT)
        textos = VGroup(titulo, subtitulo, autor).arrange(DOWN, buff=0.25)
        abertura = Group(logo, textos).arrange(RIGHT, buff=0.7).move_to(ORIGIN)

        self.play(FadeIn(logo, shift=UP * 0.2),
                   FadeIn(titulo, shift=UP * 0.2), FadeIn(subtitulo, shift=UP * 0.2),
                   FadeIn(autor, shift=UP * 0.2), run_time=0.9)
        self.wait(1.2)
        self.play(FadeOut(abertura), run_time=0.6)

        cabecalho = Text("1. Atuação e instabilidade da planta", font_size=28,
                          color=WHITE, weight=BOLD).to_edge(UP, buff=0.15)
        self.play(FadeIn(cabecalho, shift=UP * 0.15))

        sim = simulate_open_loop(t_end=6.0, perturb_t=1.0, v_kick=0.02)
        x_of = interp_of(sim, "x")
        u_of = interp_of(sim, "u")
        t_arr, x_arr, u_arr = sim["t"], sim["x"], sim["u"]
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

        # -------- diagrama: fonte -> atuador -> eletroímã+esfera --------
        planta = build_planta_maglev(pos_tracker, power_tracker, width=1.7, height=2.9)
        atuador = build_atuador(power_tracker, width=1.3, height=1.0)
        atuador.next_to(planta, LEFT, buff=1.1)
        atuador.shift(UP * (planta.get_power_in()[1] - atuador.get_out()[1]))

        fio = always_redraw(lambda: Line(
            atuador.get_out(), planta.get_power_in(), stroke_color=STEEL_LIGHT, stroke_width=3))

        fonte = build_fonte()
        fonte.next_to(atuador, LEFT, buff=0.55)
        fonte.shift(UP * (atuador.get_in()[1] - fonte.get_right_pt()[1]))
        fio_fonte = Line(fonte.get_right_pt(), atuador.get_in(),
                          stroke_color=STEEL_LIGHT, stroke_width=3)

        diagrama = VGroup(fonte, fio_fonte, atuador, planta, fio)
        diagrama.scale(0.85).move_to(UP * 1.35 + LEFT * 0.3)

        self.play(LaggedStart(
            GrowFromCenter(fonte), Create(fio_fonte),
            GrowFromCenter(atuador), Create(fio),
            FadeIn(planta, shift=LEFT * 0.3),
            lag_ratio=0.35, run_time=2.6
        ))
        self.wait(0.4)

        equilibrio_tag = Text("Corrente travada em i₀: compensa a gravidade exatamente em x₀",
                               font_size=15, color=STEEL_LIGHT)
        equilibrio_tag.next_to(diagrama, DOWN, buff=0.15)
        self.play(FadeIn(equilibrio_tag, shift=UP * 0.1))
        self.wait(1.2)
        self.play(FadeOut(equilibrio_tag))

        # -------- gráfico da posição divergindo --------
        eixo = signal_axes(x_range=[0, t_max, 1], y_range=[X_MIN, X_MAX, 1], x_length=9.0, y_length=2.5)
        eixo.move_to(DOWN * 1.95)
        eixo_labels = eixo.get_axis_labels(x_label=Text("t (s)", font_size=16),
                                            y_label=Text("x (cm)", font_size=16))
        eixo_labels[1].next_to(eixo.y_axis.get_top(), LEFT, buff=0.12)

        curva_x = growing_curve(eixo, t_arr, x_arr, t_tracker, color=BLUE_CTRL, stroke_width=4)
        ponto_x = always_redraw(lambda: Dot(
            eixo.c2p(t_tracker.get_value(), x_of(t_tracker.get_value())), radius=0.05, color=GOLD))
        linha_x0 = DashedLine(eixo.c2p(0, X0), eixo.c2p(t_max, X0), color=STEEL_LIGHT, stroke_width=1.5)
        x0_tag = Text("x₀ (equilíbrio)", font_size=13, color=STEEL_LIGHT).next_to(
            eixo.c2p(0, X0), LEFT, buff=0.15)

        graf_titulo = Text("Posição da esfera em malha aberta (corrente constante)",
                            font_size=16, color=WHITE)
        graf_titulo.next_to(eixo, UP, buff=0.15)

        self.play(FadeIn(graf_titulo), Create(eixo), FadeIn(eixo_labels))
        self.play(Create(linha_x0), FadeIn(x0_tag))
        self.add(curva_x, ponto_x)
        self.wait(0.2)

        self.play(t_tracker.animate.set_value(t_max), run_time=11.0, rate_func=linear)
        self.wait(0.3)

        destino = "no chão" if x_arr[-1] >= (X_MIN + X_MAX) / 2 else "no ímã"
        conclusao = Text(f"Uma perturbação mínima basta: sem controle, a esfera diverge e cai {destino}.",
                          font_size=16, color=WHITE, t2c={"diverge": RED_ERR})
        conclusao.to_edge(DOWN, buff=0.25)
        self.play(FadeIn(conclusao, shift=UP * 0.1))
        self.wait(3.2)
        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.2)
