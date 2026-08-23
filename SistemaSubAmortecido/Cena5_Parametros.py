"""Cena 5 — Os parâmetros característicos da resposta subamortecida:
valor de regime permanente, tempo de subida, tempo de pico, overshoot
(OS%), tempo de acomodação e a separação transitório/regime permanente.
Encerramento com o brasão da UFPA."""

from manim import *
import numpy as np
from sistema_components import *

config.background_color = BG
CMAP = {"K": COL_K, r"\zeta": COL_ZETA, r"\omega_n": COL_WN, r"\omega_d": COL_WD}

K_EX, ZETA_EX, WN_EX = 1.0, 0.35, 3.0
T_MAX = 6.5


class Cena5_Parametros(Scene):
    def construct(self):
        cab = header("5. Parâmetros da resposta transitória")
        self.play(FadeIn(cab, shift=UP * 0.15))

        params = compute_params(K_EX, ZETA_EX, WN_EX)
        t_arr = np.linspace(0, T_MAX, 1200)
        c_arr = step_response(t_arr, K_EX, ZETA_EX, WN_EX)
        env_up = envelope_upper(t_arr, K_EX, ZETA_EX, WN_EX)
        env_lo = envelope_lower(t_arr, K_EX, ZETA_EX, WN_EX)
        peak_val = K_EX * (1 + params["OS"] / 100)

        # ==================== gráfico (metade esquerda) ====================
        eixo = signal_axes(x_range=[0, T_MAX, 1], y_range=[0, 1.55, 0.5],
                             x_length=6.6, y_length=4.6)
        eixo.move_to(LEFT * 3.35 + DOWN * 0.6)
        eixo_labels = eixo.get_axis_labels(
            x_label=Text("t (s)", font_size=16, color=INK),
            y_label=Text("c(t)", font_size=16, color=INK))

        curva_env_up = eixo.plot_line_graph(x_values=t_arr, y_values=env_up,
                                              line_color=COL_ENV, add_vertex_dots=False, stroke_width=2)
        curva_env_lo = eixo.plot_line_graph(x_values=t_arr, y_values=env_lo,
                                              line_color=COL_ENV, add_vertex_dots=False, stroke_width=2)
        curva_env_up.set_opacity(0.55)
        curva_env_lo.set_opacity(0.55)
        curva_c = eixo.plot_line_graph(x_values=t_arr, y_values=c_arr,
                                         line_color=COL_CURVE, add_vertex_dots=False, stroke_width=3.5)
        linha_ss = DashedLine(eixo.c2p(0, K_EX), eixo.c2p(T_MAX, K_EX), color=COL_K, stroke_width=2)

        self.play(Create(eixo), FadeIn(eixo_labels), run_time=0.9)
        self.play(Create(curva_env_up), Create(curva_env_lo), Create(linha_ss), run_time=1.0)
        self.play(Create(curva_c), run_time=1.4)
        self.wait(0.4)

        # ==================== painel de parâmetros (metade direita) ====================
        painel_pos = RIGHT * 3.15 + UP * 2.85

        # ---- 1. valor de regime permanente ----
        tvf = MathTex(r"\lim_{s\to0} sC(s) = K", font_size=26, color=COL_K)
        card_ss = VGroup(
            Text("Regime permanente", font_size=20, color=INK, weight=BOLD),
            tvf,
            MathTex(rf"c(\infty) = K = {K_EX:.2f}", font_size=24, color=COL_K),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        rotulo_ss = MathTex("K", color=COL_K, font_size=22).next_to(
            eixo.c2p(T_MAX, K_EX), RIGHT, buff=0.12)
        self.play(FadeIn(rotulo_ss))
        card_ss.next_to(cab, DOWN, buff=0.5).to_edge(RIGHT, buff=0.6)
        self.play(FadeIn(card_ss, shift=LEFT * 0.15), run_time=0.9)
        self.wait(1.5)

        # ---- 2. tempo de subida Tr ----
        pt_tr = eixo.c2p(params["Tr"], K_EX)
        linha_tr = DashedLine(eixo.c2p(params["Tr"], 0), pt_tr, color=COL_TR, stroke_width=2)
        dot_tr = Dot(pt_tr, radius=0.06, color=COL_TR)
        card_tr = VGroup(
            Text("Tempo de subida", font_size=20, color=INK, weight=BOLD),
            Text("0% → 100% do valor final", font_size=16, color=AXIS),
            MathTex(rf"T_r \approx {params['Tr']:.2f}\ \text{{s}}", font_size=24, color=COL_TR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        card_tr.next_to(card_ss, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(Create(linha_tr), FadeIn(dot_tr))
        self.play(FadeIn(card_tr, shift=LEFT * 0.15), run_time=0.9)
        self.wait(1.5)

        # ---- 3. tempo de pico Tp ----
        pt_tp = eixo.c2p(params["Tp"], peak_val)
        linha_tp = DashedLine(eixo.c2p(params["Tp"], 0), pt_tp, color=COL_TP, stroke_width=2)
        dot_tp = Dot(pt_tp, radius=0.06, color=COL_TP)
        card_tp = VGroup(
            Text("Tempo de pico", font_size=20, color=INK, weight=BOLD),
            MathTex(r"T_p = \dfrac{\pi}{\omega_d}", font_size=24, tex_to_color_map={r"\omega_d": COL_WD}),
            MathTex(rf"T_p = {params['Tp']:.2f}\ \text{{s}}", font_size=24, color=COL_TP),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        card_tp.next_to(card_tr, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(Create(linha_tp), FadeIn(dot_tp))
        self.play(FadeIn(card_tp, shift=LEFT * 0.15), run_time=0.9)
        self.wait(1.5)

        # ---- 4. overshoot OS% ----
        brace_os = BraceBetweenPoints(eixo.c2p(params["Tp"], K_EX), pt_tp, direction=RIGHT, color=COL_OS)
        card_os = VGroup(
            Text("Overshoot (OS%)", font_size=20, color=INK, weight=BOLD),
            MathTex(r"OS\% = 100\,e^{-\zeta\pi/\sqrt{1-\zeta^2}}", font_size=22,
                     tex_to_color_map={r"\zeta": COL_ZETA}),
            MathTex(rf"OS\% \approx {params['OS']:.1f}\%", font_size=24, color=COL_OS),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        card_os.next_to(card_tp, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(GrowFromCenter(brace_os))
        self.play(FadeIn(card_os, shift=LEFT * 0.15), run_time=0.9)
        self.wait(1.8)

        self.play(*[FadeOut(m) for m in
                     [card_ss, card_tr, card_tp, card_os, linha_tr, dot_tr, linha_tp, dot_tp, brace_os]],
                    run_time=0.7)

        # ---- 5. tempo de acomodação Ts ----
        banda = Polygon(
            eixo.c2p(0, 1.02 * K_EX), eixo.c2p(T_MAX, 1.02 * K_EX),
            eixo.c2p(T_MAX, 0.98 * K_EX), eixo.c2p(0, 0.98 * K_EX),
            fill_color=COL_TS, fill_opacity=0.18, stroke_width=0)
        linha_ts = DashedLine(eixo.c2p(params["Ts2"], 0), eixo.c2p(params["Ts2"], 1.15 * K_EX),
                                color=COL_TS, stroke_width=2)
        card_ts = VGroup(
            Text("Tempo de acomodação", font_size=20, color=INK, weight=BOLD),
            Text("faixa de ±2% em torno de K", font_size=16, color=AXIS),
            MathTex(r"T_s \approx \dfrac{4}{\zeta\omega_n}", font_size=24,
                     tex_to_color_map={r"\zeta": COL_ZETA, r"\omega_n": COL_WN}),
            MathTex(rf"T_s \approx {params['Ts2']:.2f}\ \text{{s}}", font_size=24, color=COL_TS),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        card_ts.move_to(painel_pos + DOWN * 0.6, aligned_edge=ORIGIN).to_edge(RIGHT, buff=0.6)
        self.play(FadeIn(banda))
        self.play(Create(linha_ts))
        self.play(FadeIn(card_ts, shift=LEFT * 0.15), run_time=0.9)
        self.wait(2.2)

        self.play(*[FadeOut(m) for m in [card_ts, banda, linha_ts]], run_time=0.7)

        # ---- 6. transitório × regime permanente ----
        ct_final = MathTex(
            r"c(t) = \underbrace{K}_{\text{regime}} "
            r"\underbrace{- K\dfrac{e^{-\zeta\omega_n t}}{\sqrt{1-\zeta^2}}\sin(\omega_d t + \varphi)}_{\text{transitório}}",
            font_size=28,
            tex_to_color_map={**CMAP, r"\text{regime}": COL_SS, r"\text{transitório}": COL_TRANS})
        ct_final.move_to(painel_pos + DOWN * 0.8, aligned_edge=ORIGIN).to_edge(RIGHT, buff=0.55)
        self.play(FadeIn(ct_final, shift=LEFT * 0.15), run_time=1.2)
        self.wait(2.6)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)

        # ==================== quadro-resumo ====================
        titulo_resumo = Text("Resumo — resposta subamortecida (K=1, ζ=0,35, ωn=3 rad/s)",
                               font_size=22, color=INK)
        titulo_resumo.move_to(UP * 1.3)
        self.play(FadeIn(titulo_resumo, shift=UP * 0.1))
        self.wait(0.6)

        resumo_valores = VGroup(
            MathTex(rf"K={K_EX:.2f}", font_size=30, color=COL_K),
            MathTex(rf"T_r\approx{params['Tr']:.2f}\,\text{{s}}", font_size=30, color=COL_TR),
            MathTex(rf"T_p={params['Tp']:.2f}\,\text{{s}}", font_size=30, color=COL_TP),
            MathTex(rf"OS\%\approx{params['OS']:.1f}\%", font_size=30, color=COL_OS),
            MathTex(rf"T_s\approx{params['Ts2']:.2f}\,\text{{s}}", font_size=30, color=COL_TS),
        ).arrange(RIGHT, buff=0.6)
        resumo_valores.move_to(UP * 0.3)

        for v in resumo_valores:
            self.play(FadeIn(v, shift=UP * 0.15), run_time=0.5)
            self.wait(0.7)
        self.wait(2.4)

        self.play(FadeOut(titulo_resumo), FadeOut(resumo_valores), run_time=0.7)

        # ==================== encerramento ====================
        recap = Text("Regime permanente + transitório amortecido: a assinatura de todo\n"
                       "sistema de 2ª ordem subamortecido.", font_size=26, color=INK, line_spacing=1.2)
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait(3.2)
        self.play(FadeOut(recap), run_time=0.6)

        logo_final = load_ufpa_logo(height=2.2).move_to(UP * 0.5)
        obrigado = Text("Obrigado!", font_size=32, color=COL_K).next_to(logo_final, DOWN, buff=0.5)
        autor = Text("Prof. Dr. Raphael Teixeira — Universidade Federal do Pará",
                      font_size=20, color=AXIS).next_to(obrigado, DOWN, buff=0.3)
        self.play(FadeIn(logo_final, scale=0.92), run_time=0.8)
        self.play(FadeIn(obrigado, shift=UP * 0.1), FadeIn(autor, shift=UP * 0.1), run_time=0.8)
        self.wait(4.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)
