from manim import *
import numpy as np

# Circuitos Elétricos 1 - Relação entre sinal senoidal e fasor
class FasorSenoide(Scene):
    def construct(self):
        # Parâmetros do sinal v(t) = Vm*cos(w*t + fase)
        Vm, freq, fase = 2.0, 0.5, PI / 6
        omega = 2 * PI * freq
        periodo = 1 / freq
        t_max = 2 * periodo  # anima 2 ciclos completos

        def v(t):
            return Vm * np.cos(omega * t + fase)

        def get_theta(t):
            return (omega * t + fase) % TAU

        tracker_t = ValueTracker(0)

        # Título e fórmulas
        titulo = Text("Sinal Senoidal e Fasor", font_size=34).to_edge(UP)
        formula_v = MathTex(r"v(t) = V_m\cos(\omega t + \varphi)").scale(0.65)
        formula_V = MathTex(r"\vec{V} = V_m\angle\varphi").scale(0.65)
        formulas = VGroup(formula_v, formula_V).arrange(RIGHT, buff=1.2).next_to(titulo, DOWN)

        # --- Diagrama fasorial (plano complexo) ---
        eixos_fasor = Axes(
            x_range=[-Vm - 0.5, Vm + 0.5, 1], y_range=[-Vm - 0.5, Vm + 0.5, 1],
            x_length=4.2, y_length=4.2,
            axis_config={"tip_length": 0.15}
        ).to_edge(LEFT, buff=0.7).shift(DOWN * 0.4)
        labels_fasor = eixos_fasor.get_axis_labels(x_label="Re", y_label="Im")

        origem = eixos_fasor.c2p(0, 0)
        raio_tela = np.linalg.norm(eixos_fasor.c2p(Vm, 0) - origem)
        circulo = Circle(radius=raio_tela, color=GREY_B, stroke_opacity=0.6).move_to(origem)

        def get_ponta():
            theta = get_theta(tracker_t.get_value())
            return eixos_fasor.c2p(Vm * np.cos(theta), Vm * np.sin(theta))

        def get_projecao():
            theta = get_theta(tracker_t.get_value())
            return eixos_fasor.c2p(Vm * np.cos(theta), 0)

        fasor = always_redraw(lambda: Arrow(
            origem, get_ponta(), buff=0, color=YELLOW, stroke_width=5,
            max_tip_length_to_length_ratio=0.15
        ))
        ponto_ponta = always_redraw(lambda: Dot(get_ponta(), color=YELLOW))

        arco_theta = always_redraw(lambda: Arc(
            radius=0.6, start_angle=0, angle=get_theta(tracker_t.get_value()),
            arc_center=origem, color=BLUE
        ))
        label_theta = always_redraw(lambda: MathTex(r"\theta", font_size=30, color=BLUE).move_to(
            origem + 0.85 * np.array([
                np.cos(get_theta(tracker_t.get_value()) / 2),
                np.sin(get_theta(tracker_t.get_value()) / 2), 0
            ])
        ))

        # Projeção sobre o eixo real = valor instantâneo v(t)
        linha_projecao = always_redraw(lambda: DashedLine(get_ponta(), get_projecao(), color=GREEN, stroke_width=2))
        ponto_projecao = always_redraw(lambda: Dot(get_projecao(), color=GREEN, radius=0.07))

        status = always_redraw(lambda: MathTex(
            r"\theta(t) = %d^\circ" % round(np.degrees(get_theta(tracker_t.get_value()))),
            font_size=28
        ).next_to(eixos_fasor, DOWN, buff=0.3))

        # --- Gráfico do sinal no tempo ---
        eixos_t = Axes(
            x_range=[0, t_max, periodo / 4], y_range=[-Vm - 0.5, Vm + 0.5, 1],
            x_length=6.2, y_length=4.2,
            axis_config={"tip_length": 0.15}
        ).to_edge(RIGHT, buff=0.7).shift(DOWN * 0.4)
        labels_t = eixos_t.get_axis_labels(x_label="t", y_label="v(t)")

        ponto_v = always_redraw(lambda: Dot(
            eixos_t.c2p(tracker_t.get_value(), v(tracker_t.get_value())), color=GREEN
        ))
        rastro_v = TracedPath(ponto_v.get_center, stroke_color=GREEN, stroke_width=4)

        self.add(titulo, formulas,
                 eixos_fasor, labels_fasor, circulo, arco_theta, label_theta,
                 fasor, ponto_ponta, linha_projecao, ponto_projecao, status,
                 eixos_t, labels_t, ponto_v, rastro_v)

        self.play(tracker_t.animate.set_value(t_max), run_time=12, rate_func=linear)
        self.wait(1)
