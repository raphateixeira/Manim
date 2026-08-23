from manim import *
import numpy as np
from scipy.integrate import odeint
from scipy.interpolate import interp1d

class MassaMola(Scene):
    def construct(self):
        # Parâmetros
        m_val, b_val, k_val, U_degrau = 1.0, 0.5, 2.0, 1.0
        
        def sistema(y, t): 
            return [y[1], (U_degrau - b_val*y[1] - k_val*y[0])/m_val]
        
        t_max = 15
        t_arr = np.linspace(0, t_max, 300)
        sol = odeint(sistema, [0.0, 0.0], t_arr)
        pos_func = interp1d(t_arr, sol[:, 0], kind='cubic')

        tracker_t = ValueTracker(0)

        # Diagrama de Blocos
        bloco_ft = Rectangle(width=3.5, height=1.5, color=WHITE)
        texto_ft = MathTex(r"\frac{1}{ms^2 + bs + k}").move_to(bloco_ft.get_center())
        
        seta_in = Arrow(start=bloco_ft.get_left() + LEFT*1.5, end=bloco_ft.get_left(), buff=0, tip_length=0.15)
        texto_in = MathTex(r"U(s)").next_to(seta_in, UP, buff=0.1)
        
        seta_out = Arrow(start=bloco_ft.get_right(), end=bloco_ft.get_right() + RIGHT*1.5, buff=0, tip_length=0.15)
        texto_out = MathTex(r"Y(s)").next_to(seta_out, UP, buff=0.1)
        
        diagrama = VGroup(seta_in, texto_in, bloco_ft, texto_ft, seta_out, texto_out).to_edge(UP)

        # Gráfico (Setas dos eixos ajustadas proporcionalmente)
        eixos = Axes(
            x_range=[0, t_max, 3], y_range=[-0.2, 1.2, 0.5],
            x_length=5, y_length=3.5,
            axis_config={
                "tip_length": 0.1,
                "tip_width": 0.1
            }
        ).to_edge(RIGHT, buff=0.5).shift(DOWN*1.2)
        labels = eixos.get_axis_labels(x_label="t", y_label="y(t)")
        
        # Sistema Físico
        parede = Line(UP*1.5, DOWN*1.5).move_to(LEFT*6.5 + DOWN*1.2)
        parede.set_stroke(width=6)
        
        massa = Square(side_length=1.2, color=BLUE, fill_opacity=0.5)
        
        def update_massa(mob):
            y_pos = pos_func(tracker_t.get_value())
            mob.move_to(parede.get_center() + RIGHT * (float(y_pos) * 1.5 + 3.5))

        massa.add_updater(update_massa)

        # Identificadores m, k, b
        texto_m = always_redraw(lambda: MathTex("m").move_to(massa.get_center()))
        
        texto_k = always_redraw(lambda: MathTex("k").move_to(
            [(parede.get_center()[0] + massa.get_left()[0])/2, parede.get_center()[1] + 0.8, 0]
        ))
        
        texto_b = always_redraw(lambda: MathTex("b").move_to(
            [(parede.get_center()[0] + massa.get_left()[0])/2, parede.get_center()[1] - 0.8, 0]
        ))

        # Seta da força u(t)
        seta_forca = always_redraw(lambda: Arrow(
            start=massa.get_right() + RIGHT*0.1, 
            end=massa.get_right() + RIGHT*1.3, 
            buff=0, color=YELLOW, tip_length=0.15
        ))
        texto_forca = always_redraw(lambda: MathTex("u(t)").scale(0.8).next_to(seta_forca, UP, buff=0.1).set_color(YELLOW))

        # Funções de desenho da mola e amortecedor
        def get_mola():
            start = parede.get_center() + UP*0.4
            end = massa.get_left() + UP*0.4
            
            p1 = start + RIGHT*0.3
            p2 = end + LEFT*0.3
            L_mola = np.linalg.norm(p2 - p1)
            
            pts = [start, p1]
            n_voltas = 9
            for i in range(1, n_voltas + 1):
                x_p = p1[0] + (L_mola/(n_voltas+1))*i
                y_p = p1[1] + (0.15 if i%2!=0 else -0.15)
                pts.append([x_p, y_p, 0])
            pts.extend([p2, end])
            
            return VMobject(color=WHITE).set_points_as_corners(pts)

        def get_amortecedor():
            start = parede.get_center() + DOWN*0.4
            end = massa.get_left() + DOWN*0.4
            
            p1_cil = start + RIGHT*0.3
            p2_cil = start + RIGHT*2.5 
            
            l_parede = Line(start, p1_cil, color=GREY)
            c_sup = Line(p1_cil + UP*0.15, p2_cil + UP*0.15, color=GREY)
            c_inf = Line(p1_cil + DOWN*0.15, p2_cil + DOWN*0.15, color=GREY)
            c_fundo = Line(p1_cil + UP*0.15, p1_cil + DOWN*0.15, color=GREY)
            
            p2_pist = end + LEFT*2.2
            
            haste = Line(end, p2_pist, color=WHITE)
            cabeca = Line(p2_pist + UP*0.1, p2_pist + DOWN*0.1, color=WHITE)
            
            return VGroup(l_parede, c_sup, c_inf, c_fundo, haste, cabeca)

        mola = always_redraw(get_mola)
        amortecedor = always_redraw(get_amortecedor)

        ponto = always_redraw(lambda: Dot(
            eixos.c2p(tracker_t.get_value(), pos_func(tracker_t.get_value())),
            color=RED
        ))
        rastro = TracedPath(ponto.get_center, stroke_color=RED, stroke_width=4)

        # Renderização
        self.add(diagrama, eixos, labels, parede, massa, texto_m, mola, texto_k, 
                 amortecedor, texto_b, ponto, rastro, seta_forca, texto_forca)
        self.play(tracker_t.animate.set_value(t_max), run_time=8, rate_func=linear)
        self.wait(1)