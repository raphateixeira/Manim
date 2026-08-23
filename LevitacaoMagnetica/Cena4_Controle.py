"""Cena 4 — Geração do sinal de controle e malha fechada completa, no
layout clássico de diagrama de blocos: referência entra horizontalmente
no comparador; a cadeia direta segue à direita (controlador -> atuador ->
planta); a realimentação sai da planta, desce, passa pelo sensor e volta
por baixo até a entrada negativa do comparador. O termo derivativo do
PID é o que estabiliza a planta — só P não bastaria."""

from manim import *
import numpy as np
from maglev_components import *

config.background_color = "#12161c"


class Cena4_Controle(Scene):
    def construct(self):
        cabecalho = Text("4. Sinal de controle e malha fechada", font_size=28,
                          color=WHITE, weight=BOLD).to_edge(UP, buff=0.15)
        self.play(FadeIn(cabecalho, shift=UP * 0.15))

        sim = simulate_closed_loop(t_end=14.0, r1=X0, r2=1.3, t_step=6.0)
        t_arr = sim["t"]; r_arr = sim["r"]; x_arr = sim["x"]; u_arr = sim["u"]; e_arr = sim["e"]
        r_of = interp_of(sim, "r")
        x_of = interp_of(sim, "x")
        u_of = interp_of(sim, "u")
        t_max = t_arr[-1]

        t_tracker = ValueTracker(0.0)
        pos_tracker = ValueTracker(x_of(0))
        power_tracker = ValueTracker(u_of(0))

        def sync(_m, dt):
            tt = t_tracker.get_value()
            pos_tracker.set_value(x_of(tt))
            power_tracker.set_value(u_of(tt))
        ghost = Mobject()
        ghost.add_updater(sync)
        self.add(ghost)

        # ================= diagrama de blocos (topologia clássica) =================
        comparador = build_comparador(radius=0.3)
        controlador = build_controlador(width=1.7, height=1.2, texto="PID")
        atuador = build_atuador(power_tracker, width=1.25, height=0.95)
        planta = build_planta_maglev(pos_tracker, power_tracker, width=1.5, height=2.6)
        sensor = build_sensor(width=1.0, height=0.55)

        row_y = comparador.get_right_pt()[1]

        controlador.next_to(comparador, RIGHT, buff=1.0)
        controlador.shift(UP * (row_y - controlador.get_in()[1]))

        atuador.next_to(controlador, RIGHT, buff=0.55)
        atuador.shift(UP * (row_y - atuador.get_in()[1]))

        planta.next_to(atuador, RIGHT, buff=0.85)
        planta.shift(UP * (row_y - planta.get_power_in()[1]))

        seta_cmp_ctrl = Arrow(comparador.get_right_pt(), controlador.get_in(), color=RED_ERR,
                               buff=0.06, stroke_width=3, max_tip_length_to_length_ratio=0.15)
        e_tag = MathTex("e(t)", color=RED_ERR, font_size=20).next_to(seta_cmp_ctrl, UP, buff=0.05)

        seta_ctrl_at = Arrow(controlador.get_out(), atuador.get_in(), color=BLUE_CTRL,
                              buff=0.06, stroke_width=3, max_tip_length_to_length_ratio=0.18)
        u_tag = MathTex("u(t)", color=BLUE_CTRL, font_size=20).next_to(seta_ctrl_at, UP, buff=0.05)

        fio_at_planta = Line(atuador.get_out(), planta.get_power_in(),
                              stroke_color=STEEL_LIGHT, stroke_width=2.5)

        seta_r = Arrow(comparador.get_left_pt() + LEFT * 1.7, comparador.get_left_pt(), color=GOLD,
                        buff=0.06, stroke_width=3, max_tip_length_to_length_ratio=0.14)
        r_tag = MathTex("r(t)", color=GOLD, font_size=22).next_to(seta_r, UP, buff=0.06)

        tap = planta.get_output_tap()
        cb = comparador.get_bottom_pt()
        fb_y = row_y - 1.0
        sensor.move_to(np.array([(atuador.get_in()[0] + atuador.get_out()[0]) / 2, fb_y, 0]))
        sensor.shift(UP * (fb_y - sensor.get_out()[1]))

        path_desce = polyline_path(tap, np.array([tap[0], fb_y, 0]), sensor.get_out())
        path_desce.set_stroke(color=GREEN_OK, width=2.5)
        path_volta = polyline_path(sensor.get_in(), np.array([cb[0], fb_y, 0]))
        path_volta.set_stroke(color=GREEN_OK, width=2.5)
        seta_fb_final = Arrow(np.array([cb[0], fb_y, 0]), cb, buff=0, color=GREEN_OK,
                               stroke_width=2.5, max_tip_length_to_length_ratio=0.35)
        y_tag = MathTex("y(t)", color=GREEN_OK, font_size=20).next_to(sensor, DOWN, buff=0.1)

        malha = VGroup(
            comparador, controlador, atuador, fio_at_planta, planta,
            seta_cmp_ctrl, e_tag, seta_ctrl_at, u_tag, seta_r, r_tag,
            path_desce, sensor, path_volta, seta_fb_final, y_tag,
        )
        malha.scale(0.8).move_to(UP * 1.7)

        self.play(LaggedStart(
            GrowFromCenter(comparador), GrowArrow(seta_r), FadeIn(r_tag),
            GrowArrow(seta_cmp_ctrl), FadeIn(e_tag), GrowFromCenter(controlador),
            GrowArrow(seta_ctrl_at), FadeIn(u_tag), GrowFromCenter(atuador),
            Create(fio_at_planta), FadeIn(planta, shift=LEFT * 0.2),
            lag_ratio=0.3, run_time=3.2
        ))
        self.play(Create(path_desce), GrowFromCenter(sensor), Create(path_volta),
                   GrowArrow(seta_fb_final), FadeIn(y_tag), run_time=1.4)
        self.wait(0.6)

        explicacao = Text("O termo derivativo do PID é o que estabiliza a planta instável.",
                           font_size=16, color=WHITE, t2c={"derivativo": BLUE_CTRL})
        explicacao.to_edge(DOWN, buff=3.55)
        self.play(FadeIn(explicacao, shift=UP * 0.1))
        self.wait(2.0)
        self.play(FadeOut(explicacao))

        # ================= os três gráficos fundamentais =================
        eixo_ry = signal_axes(x_range=[0, t_max, 4], y_range=[X_MIN, X_MAX, 1], x_length=9.4, y_length=1.1)
        eixo_ry.move_to(np.array([0.1, -0.7, 0]))
        titulo_ry = Text("Referência r(t)  ×  Posição x(t)", font_size=14, color=WHITE)
        titulo_ry.next_to(eixo_ry, UP, buff=0.06)

        eixo_u = signal_axes(x_range=[0, t_max, 4], y_range=[0, I_MAX, I_MAX / 2], x_length=9.4, y_length=0.95)
        eixo_u.next_to(eixo_ry, DOWN, buff=0.25)
        titulo_u = Text("Sinal de controle u(t) — corrente na bobina", font_size=14, color=BLUE_CTRL)
        titulo_u.next_to(eixo_u, UP, buff=0.05)

        eixo_e = signal_axes(x_range=[0, t_max, 4], y_range=[-1, 1, 0.5], x_length=9.4, y_length=0.95)
        eixo_e.next_to(eixo_u, DOWN, buff=0.25)
        titulo_e = Text("Erro e(t) = r(t) − x(t)", font_size=14, color=RED_ERR)
        titulo_e.next_to(eixo_e, UP, buff=0.05)
        zero_e = DashedLine(eixo_e.c2p(0, 0), eixo_e.c2p(t_max, 0), color=STEEL_LIGHT, stroke_width=1.2)

        curva_r = growing_curve(eixo_ry, t_arr, r_arr, t_tracker, color=GOLD, stroke_width=3)
        curva_x = growing_curve(eixo_ry, t_arr, x_arr, t_tracker, color=BLUE_CTRL, stroke_width=3)
        curva_u = growing_curve(eixo_u, t_arr, u_arr, t_tracker, color=BLUE_CTRL, stroke_width=3)
        curva_e = growing_curve(eixo_e, t_arr, e_arr, t_tracker, color=RED_ERR, stroke_width=3)

        self.play(
            FadeIn(titulo_ry), Create(eixo_ry),
            FadeIn(titulo_u), Create(eixo_u),
            FadeIn(titulo_e), Create(eixo_e), Create(zero_e),
            run_time=1.4
        )
        self.add(curva_r, curva_x, curva_u, curva_e)
        self.wait(0.2)

        self.play(t_tracker.animate.set_value(t_max), run_time=23.0, rate_func=linear)
        self.wait(0.6)

        conclusao = Text("Medir, comparar, decidir e atuar — repetido continuamente.",
                          font_size=22, color=WHITE).to_edge(UP, buff=0.15)
        self.play(FadeOut(cabecalho), FadeIn(conclusao, shift=UP * 0.1))
        self.wait(3.0)
        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.2)

        logo_final = load_ufpa_logo(height=2.4).move_to(ORIGIN)
        self.play(FadeIn(logo_final, scale=0.92), run_time=0.8)
        self.wait(2.2)
        self.play(FadeOut(logo_final), run_time=0.6)
