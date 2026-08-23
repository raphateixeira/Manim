from manim import *

class VectoresNoR2(Scene):
    def construct(self):
        # 1. Criar plano de coordenadas
        plane = NumberPlane(
            x_range=(-4, 4),
            y_range=(-4, 4),
            axis_config={"color": GREY_A},
            background_line_style={"stroke_width": 1}
        )
        self.add(plane)
        
        # 2. Criar vetores
        v1 = Arrow(ORIGIN, [2, 1, 0], color=BLUE, buff=0)
        v2 = Arrow(ORIGIN, [1, 2, 0], color=RED, buff=0)
        
        # 3. Animar adição
        self.play(Create(v1))
        self.play(Create(v2))
        self.wait(1)
        
        # 4. Rótulos
        label_v1 = MathTex(r"\vec{v}_1 = \begin{pmatrix} 2 \\ 1 \end{pmatrix}", 
                           color=BLUE).to_corner(UP + LEFT)
        self.play(Write(label_v1))
        label_v2 = MathTex(r"\vec{v}_2 = \begin{pmatrix} 1 \\ 2 \end{pmatrix}", 
                           color=RED).to_corner(LEFT)
        self.play(Write(label_v2))
        self.wait()