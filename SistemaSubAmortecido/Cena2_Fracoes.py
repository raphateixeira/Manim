"""Cena 2 — Aplicação da entrada degrau e expansão de C(s) em frações
parciais: A/s + (Bs+D)/(s²+2ζωn s+ωn²), com A, B, D obtidos por
comparação de coeficientes."""

from manim import *
import numpy as np
from sistema_components import *

config.background_color = BG
CMAP = {"K": COL_K, r"\zeta": COL_ZETA, r"\omega_n": COL_WN}


class Cena2_Fracoes(Scene):
    def construct(self):
        cab = header("2. Entrada degrau e frações parciais")
        self.play(FadeIn(cab, shift=UP * 0.15))

        # ==================== G(s) e degrau ====================
        Gs = MathTex(r"G(s) = \dfrac{K\,\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}",
                      font_size=38, tex_to_color_map=CMAP)

        Rs = MathTex(r"R(s) = \dfrac{1}{s}", font_size=38)

        linha1 = VGroup(Gs, Rs).arrange(RIGHT, buff=1.2).move_to(UP * 2.2)
        self.play(Write(Gs), run_time=1.1)
        self.play(Write(Rs), run_time=0.8)
        self.wait(0.6)

        degrau_nota = Text("entrada degrau unitário: r(t) = u(t)", font_size=20, color=AXIS)
        degrau_nota.next_to(Rs, DOWN, buff=0.3)
        self.play(FadeIn(degrau_nota, shift=UP * 0.1))
        self.wait(1.3)
        self.play(FadeOut(degrau_nota))

        # ==================== C(s) = G(s)R(s) ====================
        Cs1 = MathTex(
            r"C(s) = G(s)\,R(s) = \dfrac{K\,\omega_n^2}{s\,\left(s^2+2\zeta\omega_n s+\omega_n^2\right)}",
            font_size=38, tex_to_color_map=CMAP)
        Cs1.move_to(UP * 1.0)

        self.play(FadeOut(Gs), FadeOut(Rs), Write(Cs1), run_time=1.4)
        self.wait(1.3)

        self.play(Cs1.animate.scale(0.78).to_edge(UP, buff=0.9), run_time=0.8)

        # ==================== forma das frações parciais ====================
        pf_forma = MathTex(
            r"C(s) = \dfrac{A}{s} + \dfrac{B\,s + D}{s^2+2\zeta\omega_n s+\omega_n^2}",
            font_size=36, tex_to_color_map=CMAP)
        pf_forma.next_to(Cs1, DOWN, buff=0.55)
        self.play(Write(pf_forma), run_time=1.3)
        self.wait(1.3)

        # ==================== igualando numeradores ====================
        eq_num = MathTex(
            r"K\,\omega_n^2 = A\left(s^2+2\zeta\omega_n s+\omega_n^2\right) + (B\,s+D)\,s",
            font_size=32, tex_to_color_map=CMAP)
        eq_num.next_to(pf_forma, DOWN, buff=0.55)
        self.play(Write(eq_num), run_time=1.5)
        self.wait(1.3)

        # ==================== resolvendo A, B, D ====================
        passos = VGroup(
            MathTex(r"s=0:\quad K\,\omega_n^2 = A\,\omega_n^2 \;\Rightarrow\; A = K",
                     font_size=28, tex_to_color_map=CMAP),
            MathTex(r"\text{coef. } s^2:\quad 0 = A + B \;\Rightarrow\; B = -K",
                     font_size=28, tex_to_color_map=CMAP),
            MathTex(r"\text{coef. } s^1:\quad 0 = 2\zeta\omega_n A + D \;\Rightarrow\; D = -2\zeta\omega_n K",
                     font_size=28, tex_to_color_map=CMAP),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        passos.next_to(eq_num, DOWN, buff=0.5)

        self.play(FadeIn(passos[0], shift=RIGHT * 0.15), run_time=1.0)
        self.wait(1.0)
        self.play(FadeIn(passos[1], shift=RIGHT * 0.15), run_time=1.0)
        self.wait(1.0)
        self.play(FadeIn(passos[2], shift=RIGHT * 0.15), run_time=1.0)
        self.wait(1.6)

        self.play(*[FadeOut(m) for m in
                     [Cs1, pf_forma, eq_num, passos]], run_time=0.8)

        # ==================== C(s) final ====================
        Cs_final = MathTex(
            r"C(s) = \dfrac{K}{s} \;-\; \dfrac{K\left(s + 2\zeta\omega_n\right)}{s^2+2\zeta\omega_n s+\omega_n^2}",
            font_size=42, tex_to_color_map=CMAP)
        Cs_final.move_to(UP * 0.3)

        caixa = SurroundingRectangle(Cs_final, color=COL_K, buff=0.3)
        self.play(Write(Cs_final), run_time=1.6)
        self.play(Create(caixa), run_time=0.8)
        self.wait(1.6)

        conclusao = Text("Agora falta apenas transformar cada termo de volta para o tempo.",
                           font_size=22, color=INK)
        conclusao.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(conclusao, shift=UP * 0.1))
        self.wait(3.4)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)
        self.wait(0.2)
