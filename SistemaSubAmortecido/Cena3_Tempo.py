"""Cena 3 — Transformada inversa de Laplace, termo a termo, até a forma
compacta c(t) = K[1 - e^{-ζωn t}/√(1-ζ²) · sin(ωd t + φ)], com φ = arccos ζ
(o mesmo ângulo θ dos polos no plano s, da Cena 1)."""

from manim import *
import numpy as np
from sistema_components import *

config.background_color = BG
CMAP = {"K": COL_K, r"\zeta": COL_ZETA, r"\omega_n": COL_WN, r"\omega_d": COL_WD}


class Cena3_Tempo(Scene):
    def construct(self):
        cab = header("3. Da frequência para o tempo")
        self.play(FadeIn(cab, shift=UP * 0.15))

        Cs_final = MathTex(
            r"C(s) = \dfrac{K}{s} \;-\; \dfrac{K\left(s + 2\zeta\omega_n\right)}{s^2+2\zeta\omega_n s+\omega_n^2}",
            font_size=38, tex_to_color_map=CMAP)
        Cs_final.move_to(UP * 2.3)
        self.play(FadeIn(Cs_final, shift=UP * 0.1), run_time=1.0)
        self.wait(1.0)

        # ==================== completar o quadrado ====================
        quad = MathTex(r"s^2+2\zeta\omega_n s+\omega_n^2 = (s+\zeta\omega_n)^2 + \omega_d^2",
                        font_size=32, tex_to_color_map=CMAP)
        quad.next_to(Cs_final, DOWN, buff=0.5)
        self.play(Write(quad), run_time=1.3)
        self.wait(0.4)

        wd_def = MathTex(r"\omega_d = \omega_n\sqrt{1-\zeta^2}", font_size=28, tex_to_color_map=CMAP)
        wd_def.next_to(quad, DOWN, buff=0.3)
        self.play(FadeIn(wd_def, shift=UP * 0.1), run_time=0.9)
        self.wait(1.3)

        reescreve = MathTex(
            r"C(s) = \dfrac{K}{s} - \dfrac{K\big[(s+\zeta\omega_n) + \zeta\omega_n\big]}{(s+\zeta\omega_n)^2+\omega_d^2}",
            font_size=32, tex_to_color_map=CMAP)
        reescreve.next_to(wd_def, DOWN, buff=0.4)
        self.play(Write(reescreve), run_time=1.6)
        self.wait(1.5)

        self.play(*[FadeOut(m) for m in [quad, wd_def, reescreve]], run_time=0.7)

        # ==================== pares de transformada ====================
        tabela_titulo = Text("Pares de transformada usados (a = ζωn):", font_size=22, color=INK)
        pares = VGroup(
            MathTex(r"\mathcal{L}^{-1}\left\{\dfrac{1}{s}\right\} = 1", font_size=26),
            MathTex(r"\mathcal{L}^{-1}\left\{\dfrac{s+a}{(s+a)^2+\omega_d^2}\right\} = e^{-at}\cos(\omega_d t)",
                     font_size=26, tex_to_color_map={r"\omega_d": COL_WD}),
            MathTex(r"\mathcal{L}^{-1}\left\{\dfrac{\omega_d}{(s+a)^2+\omega_d^2}\right\} = e^{-at}\sin(\omega_d t)",
                     font_size=26, tex_to_color_map={r"\omega_d": COL_WD}),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        bloco_tabela = VGroup(tabela_titulo, pares).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        bloco_tabela.next_to(Cs_final, DOWN, buff=0.6)

        self.play(FadeIn(tabela_titulo, shift=UP * 0.1))
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.15) for p in pares],
                                lag_ratio=0.4, run_time=2.2))
        self.wait(2.0)
        self.play(FadeOut(bloco_tabela), FadeOut(Cs_final), run_time=0.7)

        # ==================== c(t) termo a termo ====================
        ct_termos = MathTex(
            r"c(t) = K\Big[\,1 \;-\; e^{-\zeta\omega_n t}\cos(\omega_d t) "
            r"\;-\; \dfrac{\zeta}{\sqrt{1-\zeta^2}}\,e^{-\zeta\omega_n t}\sin(\omega_d t)\,\Big]",
            font_size=32, tex_to_color_map=CMAP)
        ct_termos.move_to(UP * 1.6)
        self.play(Write(ct_termos), run_time=2.0)
        self.wait(2.0)

        # ==================== compactação trigonométrica ====================
        nota_trig = Text("cos x + (ζ/√(1-ζ²)) sin x  =  (1/√(1-ζ²)) sin(x + φ)",
                           font_size=22, color=AXIS)
        nota_trig.next_to(ct_termos, DOWN, buff=0.5)
        self.play(FadeIn(nota_trig, shift=UP * 0.1), run_time=1.0)
        self.wait(1.6)

        phi_def = MathTex(r"\varphi = \arccos\zeta = \arctan\!\dfrac{\sqrt{1-\zeta^2}}{\zeta}",
                            font_size=30, tex_to_color_map={r"\zeta": COL_ZETA})
        phi_def.next_to(nota_trig, DOWN, buff=0.4)
        self.play(Write(phi_def), run_time=1.3)
        self.wait(0.6)

        callback = Text("mesmo ângulo θ dos polos no plano s (Cena 1)!", font_size=20, color=COL_WD)
        callback.next_to(phi_def, DOWN, buff=0.3)
        self.play(FadeIn(callback, shift=UP * 0.1), run_time=0.9)
        self.wait(2.0)

        self.play(*[FadeOut(m) for m in [ct_termos, nota_trig, phi_def, callback]], run_time=0.8)

        # ==================== forma compacta final ====================
        titulo_final = Text("Forma compacta da resposta subamortecida:", font_size=24, color=INK)
        titulo_final.move_to(UP * 1.7)
        self.play(FadeIn(titulo_final, shift=UP * 0.1))

        ct_final = MathTex(
            r"c(t) = K\left[\,1 - \dfrac{e^{-\zeta\omega_n t}}{\sqrt{1-\zeta^2}}\,"
            r"\sin\!\big(\omega_d t + \varphi\big)\right]",
            font_size=44, tex_to_color_map=CMAP)
        ct_final.move_to(UP * 0.5)
        caixa = SurroundingRectangle(ct_final, color=COL_K, buff=0.3)

        self.play(Write(ct_final), run_time=2.0)
        self.play(Create(caixa), run_time=0.8)
        self.wait(4.0)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)
        self.wait(0.2)
