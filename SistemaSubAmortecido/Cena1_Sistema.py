"""Cena 1 — O sistema de segunda ordem: forma geral de G(s), o papel de
K, ζ e ωn, a condição de subamortecimento (0<ζ<1) e a localização dos
polos complexos conjugados no plano s."""

from manim import *
import numpy as np
from sistema_components import *

config.background_color = BG


class Cena1_Sistema(Scene):
    def construct(self):
        # ==================== abertura ====================
        logo = load_ufpa_logo(height=1.4)
        titulo = Text("Sistemas de Controle", font_size=38, color=INK, weight=BOLD)
        subtitulo = Text("Resposta ao degrau de sistemas de 2ª ordem subamortecidos",
                          font_size=22, color=COL_K)
        autor = Text("Prof. Dr. Raphael Teixeira", font_size=20, color=INK)
        universidade = Text("Universidade Federal do Pará", font_size=17, color=AXIS)
        textos = VGroup(titulo, subtitulo, autor, universidade).arrange(DOWN, buff=0.22)
        abertura = Group(logo, textos).arrange(RIGHT, buff=0.7).move_to(ORIGIN)

        self.play(FadeIn(logo, shift=UP * 0.2), FadeIn(titulo, shift=UP * 0.2),
                   FadeIn(subtitulo, shift=UP * 0.2), FadeIn(autor, shift=UP * 0.2),
                   FadeIn(universidade, shift=UP * 0.2), run_time=1.0)
        self.wait(1.8)
        self.play(FadeOut(abertura), run_time=0.6)

        cab = header("1. O sistema de segunda ordem")
        self.play(FadeIn(cab, shift=UP * 0.15))

        # ==================== G(s) geral ====================
        Gs = MathTex(r"G(s) = \dfrac{K\,\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}",
                      font_size=50, tex_to_color_map={"K": COL_K, r"\zeta": COL_ZETA, r"\omega_n": COL_WN})
        Gs.move_to(UP * 2.15)
        self.play(Write(Gs), run_time=1.6)
        self.wait(1.0)

        # ==================== diagrama de blocos ====================
        bloco = build_block("G(s)", color=INK, width=2.0, height=1.1)
        bloco.move_to(UP * 0.55)
        entrada = MathTex("R(s)", font_size=30, color=INK).next_to(bloco, LEFT, buff=1.1)
        saida = MathTex("C(s)", font_size=30, color=INK).next_to(bloco, RIGHT, buff=1.1)
        seta_in = Arrow(entrada.get_right(), bloco.get_in(), buff=0.12, color=INK,
                          stroke_width=3, max_tip_length_to_length_ratio=0.3)
        seta_out = Arrow(bloco.get_out(), saida.get_left(), buff=0.12, color=INK,
                           stroke_width=3, max_tip_length_to_length_ratio=0.3)
        diagrama = VGroup(entrada, seta_in, bloco, seta_out, saida)

        self.play(LaggedStart(
            FadeIn(entrada, shift=RIGHT * 0.2), GrowArrow(seta_in),
            Create(bloco), GrowArrow(seta_out), FadeIn(saida, shift=RIGHT * 0.2),
            lag_ratio=0.25, run_time=1.8))
        self.wait(0.5)

        # ==================== legenda dos parâmetros ====================
        legenda = VGroup(
            bullet("K", COL_K, "ganho estático (valor final da resposta)"),
            bullet(r"\zeta", COL_ZETA, "coeficiente de amortecimento"),
            bullet(r"\omega_n", COL_WN, "frequência natural não amortecida"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        legenda.next_to(diagrama, DOWN, buff=0.65)

        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.1) for b in legenda],
                                lag_ratio=0.35, run_time=1.8))
        self.wait(1.4)

        self.play(FadeOut(legenda), FadeOut(diagrama), FadeOut(Gs), run_time=0.6)

        # ==================== condição de subamortecimento ====================
        cond_titulo = Text("Casos possíveis, de acordo com ζ:", font_size=24, color=INK)
        casos = VGroup(
            Text("ζ = 0    →  oscilatório (sem amortecimento)", font_size=22, color=AXIS),
            Text("0 < ζ < 1  →  subamortecido  (nosso foco aqui)", font_size=22, color=COL_ZETA),
            Text("ζ = 1    →  criticamente amortecido", font_size=22, color=AXIS),
            Text("ζ > 1    →  superamortecido", font_size=22, color=AXIS),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        bloco_casos = VGroup(cond_titulo, casos).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        bloco_casos.move_to(UP * 0.5)

        self.play(FadeIn(cond_titulo, shift=UP * 0.1))
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.15) for c in casos],
                                lag_ratio=0.3, run_time=1.8))
        self.wait(1.6)

        destaque = SurroundingRectangle(casos[1], color=COL_ZETA, buff=0.12)
        self.play(Create(destaque))
        self.wait(1.4)
        self.play(FadeOut(bloco_casos), FadeOut(destaque), run_time=0.6)

        # ==================== polos complexos ====================
        cmap_zwn = {r"\zeta": COL_ZETA, r"\omega_n": COL_WN}
        cmap_zwnwd = {r"\zeta": COL_ZETA, r"\omega_n": COL_WN, r"\omega_d": COL_WD}
        eq_carac = MathTex(r"s^2 + 2\zeta\omega_n s + \omega_n^2 = 0", font_size=34,
                            tex_to_color_map=cmap_zwn)
        eq_polos = MathTex(
            r"s = -\zeta\omega_n \pm j\,\omega_n\sqrt{1-\zeta^2} = -\zeta\omega_n \pm j\,\omega_d",
            font_size=34, tex_to_color_map=cmap_zwnwd)
        def_wd = MathTex(r"\omega_d \triangleq \omega_n\sqrt{1-\zeta^2}", font_size=30,
                          tex_to_color_map=cmap_zwnwd)

        grupo_eq = VGroup(eq_carac, eq_polos, def_wd).arrange(DOWN, buff=0.35)
        grupo_eq.to_edge(UP, buff=1.0)

        self.play(Write(eq_carac), run_time=1.2)
        self.wait(0.4)
        self.play(TransformMatchingShapes(eq_carac.copy(), eq_polos), run_time=1.4)
        self.wait(0.3)
        self.play(FadeIn(def_wd, shift=UP * 0.1), run_time=0.9)
        self.wait(1.2)
        self.play(grupo_eq.animate.scale(0.75).to_corner(UL, buff=0.4), run_time=0.9)

        # ---- plano s ----
        zeta_ex, wn_ex = 0.35, 3.0
        wd_ex = wn_ex * np.sqrt(1 - zeta_ex ** 2)

        plano = Axes(x_range=[-4, 1.5, 1], y_range=[-3.5, 3.5, 1],
                      x_length=5.6, y_length=5.2,
                      axis_config={"stroke_color": AXIS, "stroke_width": 2,
                                    "tip_length": 0.15, "include_ticks": False},
                      tips=True)
        plano.move_to(DOWN * 0.35 + RIGHT * 1.6)
        rotulo_sigma = MathTex(r"\sigma", font_size=26, color=INK).next_to(plano.x_axis.get_end(), UR, buff=0.1)
        rotulo_jw = MathTex(r"j\omega", font_size=26, color=INK).next_to(plano.y_axis.get_end(), LEFT, buff=0.15)

        polo_sup = plano.c2p(-zeta_ex * wn_ex, wd_ex)
        polo_inf = plano.c2p(-zeta_ex * wn_ex, -wd_ex)
        origem = plano.c2p(0, 0)

        raio_sup = Line(origem, polo_sup, color=COL_WN, stroke_width=2.5)
        raio_inf = Line(origem, polo_inf, color=COL_WN, stroke_width=2.5)
        rotulo_wn = MathTex(r"\omega_n", font_size=24, color=COL_WN)
        rotulo_wn.move_to(raio_sup.point_from_proportion(0.5) + UP * 0.28 + LEFT * 0.05)

        marca_x_sup = Cross(scale_factor=0.14, stroke_color=COL_WD, stroke_width=3).move_to(polo_sup)
        marca_x_inf = Cross(scale_factor=0.14, stroke_color=COL_WD, stroke_width=3).move_to(polo_inf)

        proj_h = DashedLine(origem, plano.c2p(-zeta_ex * wn_ex, 0), color=COL_ZETA, stroke_width=2)
        proj_v = DashedLine(plano.c2p(-zeta_ex * wn_ex, 0), polo_sup, color=COL_WD, stroke_width=2)
        rotulo_re = MathTex(r"-\zeta\omega_n", font_size=22, color=COL_ZETA).next_to(proj_h, DOWN, buff=0.12)
        rotulo_im = MathTex(r"\omega_d", font_size=22, color=COL_WD).next_to(proj_v, RIGHT, buff=0.1)

        theta = Angle(Line(origem, plano.c2p(-1, 0)), raio_sup, radius=0.55, color=INK)
        rotulo_theta = MathTex(r"\theta", font_size=22, color=INK).move_to(
            Angle(Line(origem, plano.c2p(-1, 0)), raio_sup, radius=0.8).point_from_proportion(0.5))
        cos_theta = MathTex(r"\cos\theta = \zeta", font_size=26, color=INK,
                             tex_to_color_map={r"\zeta": COL_ZETA})
        cos_theta.next_to(plano, DOWN, buff=0.35)

        titulo_plano = Text("Polos complexos conjugados no plano s", font_size=20, color=INK)
        titulo_plano.next_to(plano, UP, buff=0.15)

        self.play(Create(plano), FadeIn(rotulo_sigma), FadeIn(rotulo_jw), FadeIn(titulo_plano), run_time=1.0)
        self.play(Create(raio_sup), Create(raio_inf), FadeIn(rotulo_wn), run_time=1.0)
        self.play(FadeIn(marca_x_sup, scale=1.4), FadeIn(marca_x_inf, scale=1.4), run_time=0.7)
        self.play(Create(proj_h), FadeIn(rotulo_re), Create(proj_v), FadeIn(rotulo_im), run_time=1.0)
        self.play(Create(theta), FadeIn(rotulo_theta), run_time=0.8)
        self.play(Write(cos_theta), run_time=0.9)
        self.wait(4.0)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)
        self.wait(0.2)
