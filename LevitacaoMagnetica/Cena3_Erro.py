"""Cena 3 — Referência, comparação e geração do erro: o operador define a
altura desejada (referência r(t), entra horizontalmente no comparador,
como na malha de controle clássica); a realimentação y(t) entra por
baixo, na entrada negativa. O comparador produz o erro e(t) = r(t) - y(t).
Os gráficos já mostram o resultado com o controlador atuando (formalizado
na Cena 4): sem ele, r(t) e e(t) não teriam sentido, pois a planta diverge."""

from manim import *
import numpy as np
from maglev_components import *

config.background_color = "#12161c"


class Cena3_Erro(Scene):
    def construct(self):
        cabecalho = Text("3. Referência, comparação e geração do erro", font_size=26,
                          color=WHITE, weight=BOLD).to_edge(UP, buff=0.3)
        self.play(FadeIn(cabecalho, shift=UP * 0.15))

        sim = simulate_closed_loop(t_end=14.0, r1=X0, r2=1.3, t_step=6.0)
        t_arr = sim["t"]; r_arr = sim["r"]; x_arr = sim["x"]; e_arr = sim["e"]
        r_of = interp_of(sim, "r")
        t_max = t_arr[-1]
        t_tracker = ValueTracker(0.0)

        # -------- diagrama clássico: r(t) --> (+ Σ -) --> e(t), y(t) por baixo --------
        comparador = build_comparador(radius=0.4)
        comparador.move_to(UP * 1.7)

        seta_r = Arrow(comparador.get_left_pt() + LEFT * 2.6, comparador.get_left_pt(),
                        color=GOLD, buff=0.08, stroke_width=3.5, max_tip_length_to_length_ratio=0.14)
        r_tag = MathTex("r(t)", color=GOLD, font_size=30).next_to(seta_r, UP, buff=0.1)

        seta_e = Arrow(comparador.get_right_pt(), comparador.get_right_pt() + RIGHT * 2.0,
                        color=RED_ERR, buff=0.08, stroke_width=3.5, max_tip_length_to_length_ratio=0.16)
        e_tag = MathTex("e(t) = r(t) - y(t)", color=RED_ERR, font_size=26)
        e_tag.next_to(seta_e, UP, buff=0.1).shift(RIGHT * 0.35)

        fb_bottom = comparador.get_bottom_pt() + DOWN * 0.6
        seta_fb = Arrow(fb_bottom, comparador.get_bottom_pt(), color=GREEN_OK, buff=0.08,
                         stroke_width=3.5, max_tip_length_to_length_ratio=0.16)
        y_tag = MathTex("y(t)", color=GREEN_OK, font_size=28).next_to(fb_bottom, DOWN, buff=0.08)
        sensor_tag = Text("vindo do sensor (Cena 2)", font_size=12, color=GREEN_OK)
        sensor_tag.next_to(y_tag, DOWN, buff=0.06)

        # painel de referência (gap desejado) — acima da seta r(t)
        ref_box = RoundedRectangle(corner_radius=0.08, width=1.6, height=0.9,
                                    fill_color=PANEL, fill_opacity=1,
                                    stroke_color=GOLD, stroke_width=3)
        ref_box.next_to(seta_r, LEFT, buff=0.05).align_to(seta_r, DOWN).shift(UP * 0.02)
        ref_label = Text("GAP DESEJADO", font_size=12, color=WHITE, weight=BOLD)
        ref_label.next_to(ref_box, UP, buff=0.12)
        dial = Circle(radius=0.26, fill_color=SCREEN_BG, fill_opacity=1,
                       stroke_color=GOLD, stroke_width=2).move_to(ref_box.get_center() + LEFT * 0.35)

        def dial_angle():
            f = np.clip((r_of(t_tracker.get_value()) - X_MIN) / (X_MAX - X_MIN), 0, 1)
            return np.deg2rad(200 - 220 * f)
        ponteiro = always_redraw(lambda: Line(
            dial.get_center(),
            dial.get_center() + 0.2 * np.array([np.cos(dial_angle()), np.sin(dial_angle()), 0]),
            stroke_color=RED_ERR, stroke_width=3))
        r_num = DecimalNumber(r_of(0), num_decimal_places=1, color=GOLD, font_size=18)
        r_num.add_updater(lambda m: m.set_value(r_of(t_tracker.get_value())))
        r_unit = Text("cm", font_size=13, color=GOLD)
        r_readout = VGroup(r_num, r_unit).arrange(RIGHT, buff=0.04)
        r_readout.add_updater(lambda m: m.next_to(dial, RIGHT, buff=0.1))

        self.play(GrowFromCenter(comparador))
        self.play(GrowArrow(seta_r), FadeIn(r_tag))
        self.play(FadeIn(ref_box, shift=RIGHT * 0.15), FadeIn(ref_label), FadeIn(dial),
                   FadeIn(ponteiro), FadeIn(r_readout))
        self.play(GrowArrow(seta_fb), FadeIn(y_tag), FadeIn(sensor_tag))
        self.play(GrowArrow(seta_e), FadeIn(e_tag))
        self.wait(1.0)
        self.play(FadeOut(sensor_tag))

        # -------- gráficos: (referência x posição) e (erro) --------
        eixo_ry = signal_axes(x_range=[0, t_max, 4], y_range=[X_MIN, X_MAX, 1], x_length=9.2, y_length=1.6)
        eixo_ry.move_to(DOWN * 0.95 + LEFT * 0.1)
        titulo_ry = Text("Referência r(t)  ×  Posição x(t)", font_size=15, color=WHITE)
        titulo_ry.next_to(eixo_ry, UP, buff=0.08)
        labels_ry = eixo_ry.get_axis_labels(x_label=Text("t (s)", font_size=12),
                                             y_label=Text("cm", font_size=12))
        labels_ry[1].next_to(eixo_ry.y_axis.get_top(), LEFT, buff=0.08)

        eixo_e = signal_axes(x_range=[0, t_max, 4], y_range=[-1, 1, 0.5], x_length=9.2, y_length=1.4)
        eixo_e.next_to(eixo_ry, DOWN, buff=0.4)
        titulo_e = Text("Erro  e(t) = r(t) − x(t)", font_size=15, color=RED_ERR)
        titulo_e.next_to(eixo_e, UP, buff=0.06)
        labels_e = eixo_e.get_axis_labels(x_label=Text("t (s)", font_size=12),
                                           y_label=Text("cm", font_size=12))
        labels_e[1].next_to(eixo_e.y_axis.get_top(), LEFT, buff=0.08)
        zero_e = DashedLine(eixo_e.c2p(0, 0), eixo_e.c2p(t_max, 0), color=STEEL_LIGHT, stroke_width=1.5)

        curva_r = growing_curve(eixo_ry, t_arr, r_arr, t_tracker, color=GOLD, stroke_width=3)
        curva_y = growing_curve(eixo_ry, t_arr, x_arr, t_tracker, color=GREEN_OK, stroke_width=3)
        curva_e = growing_curve(eixo_e, t_arr, e_arr, t_tracker, color=RED_ERR, stroke_width=3)

        self.play(
            FadeIn(titulo_ry), Create(eixo_ry), FadeIn(labels_ry),
            FadeIn(titulo_e), Create(eixo_e), FadeIn(labels_e), Create(zero_e),
        )
        self.add(curva_r, curva_y, curva_e)
        self.wait(0.3)

        self.play(t_tracker.animate.set_value(t_max), run_time=18.0, rate_func=linear)
        self.wait(0.6)

        conclusao = Text("Enquanto e(t) ≠ 0, existe desvio: é esse erro que guiará o controlador.",
                          font_size=22, color=WHITE, t2c={"e(t)": RED_ERR}).to_edge(UP, buff=0.15)
        self.play(FadeOut(cabecalho), FadeIn(conclusao, shift=UP * 0.1))
        self.wait(2.8)
        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.2)
