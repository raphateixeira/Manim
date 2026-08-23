"""Cena 4 — A curva de resposta subamortecida: exemplo numérico (K=1,
ζ=0.35, ωn=3 rad/s), envoltória exponencial e oscilação amortecida ωd."""

from manim import *
import numpy as np
from sistema_components import *

config.background_color = BG
CMAP = {"K": COL_K, r"\zeta": COL_ZETA, r"\omega_n": COL_WN, r"\omega_d": COL_WD}

K_EX, ZETA_EX, WN_EX = 1.0, 0.35, 3.0
T_MAX = 6.5


class Cena4_Curva(Scene):
    def construct(self):
        cab = header("4. A curva de resposta subamortecida")
        self.play(FadeIn(cab, shift=UP * 0.15))

        ct_final = MathTex(
            r"c(t) = K\left[\,1 - \dfrac{e^{-\zeta\omega_n t}}{\sqrt{1-\zeta^2}}\,"
            r"\sin\!\big(\omega_d t + \varphi\big)\right]", font_size=30, tex_to_color_map=CMAP)
        ct_final.move_to(UP * 2.9)
        self.play(FadeIn(ct_final, shift=UP * 0.1), run_time=1.0)
        self.wait(0.6)

        params = compute_params(K_EX, ZETA_EX, WN_EX)
        exemplo = MathTex(
            r"K=1 \qquad \zeta=0{,}35 \qquad \omega_n=3\ \text{rad/s} \qquad "
            rf"\omega_d={params['wd']:.2f}\ \text{{rad/s}} \qquad \varphi={params['phi']:.2f}\ \text{{rad}}",
            font_size=22)
        exemplo.next_to(ct_final, DOWN, buff=0.3)
        self.play(FadeIn(exemplo, shift=UP * 0.1), run_time=1.1)
        self.wait(1.4)

        # ==================== eixos ====================
        eixo = signal_axes(x_range=[0, T_MAX, 1], y_range=[0, 2.2, 0.5],
                             x_length=10.5, y_length=4.0)
        eixo.move_to(DOWN * 1.3)
        eixo_labels = eixo.get_axis_labels(
            x_label=Text("t (s)", font_size=18, color=INK),
            y_label=Text("c(t)", font_size=18, color=INK))

        t_arr = np.linspace(0, T_MAX, 1200)
        c_arr = step_response(t_arr, K_EX, ZETA_EX, WN_EX)
        env_up = envelope_upper(t_arr, K_EX, ZETA_EX, WN_EX)
        env_lo = envelope_lower(t_arr, K_EX, ZETA_EX, WN_EX)

        linha_ss = DashedLine(eixo.c2p(0, K_EX), eixo.c2p(T_MAX, K_EX),
                                color=COL_K, stroke_width=2)
        rotulo_ss = MathTex("K", color=COL_K, font_size=24).next_to(
            eixo.c2p(T_MAX, K_EX), RIGHT, buff=0.15)

        curva_env_up = eixo.plot_line_graph(
            x_values=t_arr, y_values=env_up, line_color=COL_ENV,
            add_vertex_dots=False, stroke_width=2)
        curva_env_lo = eixo.plot_line_graph(
            x_values=t_arr, y_values=env_lo, line_color=COL_ENV,
            add_vertex_dots=False, stroke_width=2)
        curva_env_up.set_opacity(0.6)
        curva_env_lo.set_opacity(0.6)

        rotulo_env = Text("envoltória exponencial", font_size=18, color=COL_ENV)
        rotulo_env.next_to(eixo.c2p(T_MAX * 0.62, envelope_upper(np.array([T_MAX * 0.62]), K_EX, ZETA_EX, WN_EX)[0]),
                             UP, buff=0.35)

        self.play(Create(eixo), FadeIn(eixo_labels), run_time=1.0)
        self.play(Create(linha_ss), FadeIn(rotulo_ss), run_time=0.8)
        self.wait(0.4)
        self.play(Create(curva_env_up), Create(curva_env_lo), run_time=1.6)
        self.play(FadeIn(rotulo_env, shift=DOWN * 0.1), run_time=0.7)
        self.wait(1.0)

        # ==================== curva crescendo ====================
        t_tracker = ValueTracker(0.0)
        curva_c = growing_curve(eixo, t_arr, c_arr, t_tracker, color=COL_CURVE, stroke_width=4)
        ponto = always_redraw(lambda: Dot(
            eixo.c2p(t_tracker.get_value(),
                       step_response(np.array([t_tracker.get_value()]), K_EX, ZETA_EX, WN_EX)[0]),
            radius=0.06, color=COL_CURVE))

        rotulo_wd = Text(f"oscilação amortecida (ωd = {params['wd']:.2f} rad/s)",
                          font_size=18, color=COL_WD)
        rotulo_wd.next_to(eixo, DOWN, buff=0.35)

        self.add(curva_c, ponto)
        self.play(FadeIn(rotulo_wd, shift=UP * 0.1), run_time=0.6)
        self.play(t_tracker.animate.set_value(T_MAX), run_time=13.0, rate_func=linear)
        self.wait(1.6)

        conclusao = Text("A resposta oscila em torno de K e se aproxima do regime permanente.",
                           font_size=20, color=INK)
        conclusao.to_edge(DOWN, buff=0.25)
        self.play(FadeOut(rotulo_wd), FadeIn(conclusao, shift=UP * 0.1))
        self.wait(2.6)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)
        self.wait(0.2)
