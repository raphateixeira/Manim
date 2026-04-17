from manim import *
import numpy as np
from scipy import signal

# --- CONFIGURAÇÃO DO CIRCUITO (REUTILIZÁVEL) ---
def get_buck_circuit(u_val, tracker_t, Vin_label="V_{in}"):
    GND_Y, TOP_Y = -1.8, 0.7
    mid_y = (TOP_Y + GND_Y) / 2
    P1_X, P2_X, P3_X, P4_X, P5_X = -3.8, -1.8, 0.2, 2.2, 4.2
    
    # Fonte
    fonte_circ = Circle(radius=0.35, color=WHITE).move_to([P1_X, mid_y, 0])
    fonte_sign = MathTex("+", "-").arrange(DOWN, buff=0.15).scale(0.8).move_to(fonte_circ)
    fonte = VGroup(
        Line([P1_X, TOP_Y, 0], fonte_circ.get_top()),
        fonte_circ, fonte_sign,
        Line(fonte_circ.get_bottom(), [P1_X, GND_Y, 0]),
        MathTex(Vin_label).next_to(fonte_circ, LEFT)
    )

    # Chave
    no_a = Dot([P2_X - 0.4, TOP_Y, 0])
    no_b = Dot([P2_X + 0.4, TOP_Y, 0])
    chave_line = always_redraw(lambda: Line(
        no_a.get_center(), 
        no_b.get_center() if u_val(tracker_t.get_value()) > 0.5 else no_b.get_center() + UP*0.6,
        color=YELLOW if u_val(tracker_t.get_value()) > 0.5 else WHITE, stroke_width=5
    ))

    # Diodo (Roda Livre - Catodo para cima)
    diodo_tri = Triangle(color=WHITE, fill_opacity=1).scale(0.18).rotate(30*DEGREES).move_to([P3_X, mid_y + 0.1, 0])
    diodo_bar = Line([P3_X-0.25, diodo_tri.get_top()[1], 0], [P3_X+0.25, diodo_tri.get_top()[1], 0], stroke_width=4)
    diodo = VGroup(
        Line([P3_X, TOP_Y, 0], diodo_tri.get_top()),
        diodo_tri, diodo_bar,
        Line(diodo_tri.get_bottom(), [P3_X, GND_Y, 0]),
        MathTex("b").next_to(diodo_tri, LEFT, buff=0.2)
    )

    # Indutor
    indutor = VGroup()
    for i in range(4):
        arc = Arc(radius=0.18, start_angle=PI, angle=-PI, color=GOLD).shift([P3_X + 0.2 + i*0.36, TOP_Y, 0])
        indutor.add(arc)
    l_label = MathTex("L").next_to(indutor, UP, buff=0.2)
    end_indutor_x = P3_X + 0.2 + 3*0.36 + 0.18

    # Capacitor
    cap = VGroup(
        Line([P4_X, TOP_Y, 0], [P4_X, mid_y + 0.1, 0]),
        Line([P4_X-0.3, mid_y + 0.1, 0], [P4_X+0.3, mid_y + 0.1, 0]),
        Line([P4_X-0.3, mid_y - 0.1, 0], [P4_X+0.3, mid_y - 0.1, 0]),
        Line([P4_X, mid_y - 0.1, 0], [P4_X, GND_Y, 0]),
        MathTex("C").next_to([P4_X, mid_y, 0], RIGHT)
    )

    # Resistor
    res_h = 0.8
    res_zig = VMobject().set_points_as_corners([
        [P5_X, mid_y + res_h/2, 0],
        *[ [P5_X + (0.15 if i%2==0 else -0.15), mid_y + res_h/2 - (i+1)*(res_h/7), 0] for i in range(6) ],
        [P5_X, mid_y - res_h/2, 0]
    ])
    resistor = VGroup(
        Line([P5_X, TOP_Y, 0], [P5_X, mid_y + res_h/2, 0]),
        res_zig,
        Line([P5_X, mid_y - res_h/2, 0], [P5_X, GND_Y, 0]),
        MathTex("R").next_to(res_zig, RIGHT)
    )

    terra = Line([P1_X, GND_Y, 0], [P5_X, GND_Y, 0], color=GREY)
    conexoes = VGroup(
        Line([P1_X, TOP_Y, 0], no_a.get_center()),
        Line(no_b.get_center(), [P3_X, TOP_Y, 0]),
        Line([end_indutor_x, TOP_Y, 0], [P4_X, TOP_Y, 0]),
        Line([P4_X, TOP_Y, 0], [P5_X, TOP_Y, 0])
    )
    
    return VGroup(fonte, no_a, no_b, chave_line, diodo, indutor, l_label, cap, resistor, terra, conexoes)

# --- CENA 1: FREQUÊNCIA LENTA (4 Hz) ---
class BuckLento(Scene):
    def construct(self):
        Vin, L, C, R = 12.0, 0.04, 0.01, 5.0
        freq, duty, t_max = 4.0, 0.6, 2.0
        
        # Simulação
        sys = signal.TransferFunction([Vin], [L*C, L/R, 1])
        t_sim = np.linspace(0, t_max, 2000)
        u_sim = [1.0 if (t % (1/freq)) < (duty * (1/freq)) else 0.0 for t in t_sim]
        _, y_sim, _ = signal.lsim(sys, U=u_sim, T=t_sim)
        
        y_interp = lambda t: np.interp(t, t_sim, y_sim)
        u_func = lambda t: 1.0 if (t % (1/freq)) < (duty * (1/freq)) else 0.0
        tracker_t = ValueTracker(0)

        circuito = get_buck_circuit(u_func, tracker_t).scale(0.85).to_edge(LEFT, buff=0.7).shift(UP*1.0)

        eixos_pwm = Axes(x_range=[0, t_max, 0.5], y_range=[0, 1.2, 1], x_length=4, y_length=1.2,
                         axis_config={"tip_length": 0.1, "tip_width": 0.1}).to_edge(RIGHT, buff=0.5).shift(UP*2.2)
        eixos_vo = Axes(x_range=[0, t_max, 0.5], y_range=[0, 12, 4], x_length=4, y_length=2.2,
                        axis_config={"tip_length": 0.1, "tip_width": 0.1}).next_to(eixos_pwm, DOWN, buff=0.8)

        ponto_pwm = always_redraw(lambda: Dot(eixos_pwm.c2p(tracker_t.get_value(), u_func(tracker_t.get_value())), color=YELLOW, radius=0.04))
        ponto_vo = always_redraw(lambda: Dot(eixos_vo.c2p(tracker_t.get_value(), y_interp(tracker_t.get_value())), color=RED, radius=0.04))

        self.add(circuito, eixos_pwm, eixos_vo, eixos_pwm.get_axis_labels(x_label="t", y_label="u(t)"), 
                 eixos_vo.get_axis_labels(x_label="t", y_label="y(t)"), ponto_pwm, TracedPath(ponto_pwm.get_center, stroke_color=YELLOW),
                 ponto_vo, TracedPath(ponto_vo.get_center, stroke_color=RED))
        
        self.play(tracker_t.animate.set_value(t_max), run_time=12, rate_func=linear)
        self.wait(2)

# --- CENA 2: FREQUÊNCIA RÁPIDA (100 Hz) ---
class BuckRapido(Scene):
    def construct(self):
        Vin, L, C, R = 12.0, 0.04, 0.01, 5.0
        freq, duty, t_max = 100.0, 0.6, 0.5
        
        sys = signal.TransferFunction([Vin], [L*C, L/R, 1])
        t_sim = np.linspace(0, t_max, 5000)
        u_sim = [1.0 if (t % (1/freq)) < (duty * (1/freq)) else 0.0 for t in t_sim]
        _, y_sim, _ = signal.lsim(sys, U=u_sim, T=t_sim)
        
        y_interp = lambda t: np.interp(t, t_sim, y_sim)
        u_func = lambda t: 1.0 if (t % (1/freq)) < (duty * (1/freq)) else 0.0
        tracker_t = ValueTracker(0)

        circuito = get_buck_circuit(u_func, tracker_t).scale(0.85).to_edge(LEFT, buff=0.7).shift(UP*1.0)

        eixos_pwm = Axes(x_range=[0, t_max, 0.1], y_range=[0, 1.2, 1], x_length=4, y_length=1.2,
                         axis_config={"tip_length": 0.1, "tip_width": 0.1}).to_edge(RIGHT, buff=0.5).shift(UP*2.2)
        eixos_vo = Axes(x_range=[0, t_max, 0.1], y_range=[0, 12, 4], x_length=4, y_length=2.2,
                        axis_config={"tip_length": 0.1, "tip_width": 0.1}).next_to(eixos_pwm, DOWN, buff=0.8)

        ponto_pwm = always_redraw(lambda: Dot(eixos_pwm.c2p(tracker_t.get_value(), u_func(tracker_t.get_value())), color=YELLOW, radius=0.02))
        ponto_vo = always_redraw(lambda: Dot(eixos_vo.c2p(tracker_t.get_value(), y_interp(tracker_t.get_value())), color=RED, radius=0.02))

        self.add(circuito, eixos_pwm, eixos_vo, eixos_pwm.get_axis_labels(x_label="t", y_label="u(t)"), 
                 eixos_vo.get_axis_labels(x_label="t", y_label="y(t)"), ponto_pwm, TracedPath(ponto_pwm.get_center, stroke_color=YELLOW, stroke_width=2),
                 ponto_vo, TracedPath(ponto_vo.get_center, stroke_color=RED, stroke_width=2))
        
        self.play(tracker_t.animate.set_value(t_max), run_time=15, rate_func=linear)
        self.wait(2)