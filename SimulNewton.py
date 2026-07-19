from manim import *
import numpy as np

# Cálculo Numérico - Método de Newton-Raphson
# Exemplo: f(x) = x^3 - 2x - 5 = 0  (raiz ~ 2.0946)
class NewtonRaphson(Scene):
    def construct(self):
        def f(x):
            return x**3 - 2*x - 5

        def df(x):
            return 3*x**2 - 2

        x0, n_iter = 3.0, 4
        xs = [x0]
        for _ in range(n_iter):
            xs.append(xs[-1] - f(xs[-1]) / df(xs[-1]))

        y_min, y_max = -8, 18

        # Título e equação
        titulo = Text("Método de Newton-Raphson", font_size=34).to_edge(UP)
        equacao = MathTex(r"f(x) = x^3 - 2x - 5 = 0").scale(0.7).next_to(titulo, DOWN, buff=0.2)

        # --- Gráfico da função ---
        eixos = Axes(
            x_range=[1.3, 3.6, 0.5], y_range=[y_min, y_max, 4],
            x_length=6.0, y_length=4.4,
            axis_config={"tip_length": 0.15}
        ).to_edge(LEFT, buff=0.6).shift(DOWN * 0.8)
        labels = eixos.get_axis_labels(x_label="x", y_label="f(x)")
        curva = eixos.plot(f, x_range=[1.4, 3.07], color=BLUE)

        # --- Gráfico de convergência: x_n em função da iteração n ---
        eixos_conv = Axes(
            x_range=[0, n_iter + 1, 1], y_range=[1.9, 3.1, 0.3],
            x_length=4.6, y_length=2.9,
            axis_config={"tip_length": 0.12}
        ).to_edge(RIGHT, buff=0.6).shift(UP * 0.75)
        labels_conv = eixos_conv.get_axis_labels(x_label="n", y_label="x_n")

        # Fórmula do método (mostrada na introdução)
        formula = MathTex(r"x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}",
                          font_size=34).to_edge(RIGHT, buff=0.9).shift(UP * 0.75)

        def painel_iteracao(n):
            xn, xn1 = xs[n], xs[n + 1]
            return VGroup(
                MathTex(r"n = %d:\quad x_n = %.4f" % (n, xn), font_size=28),
                MathTex(r"f(x_n) = %+.4f,\quad f'(x_n) = %.4f" % (f(xn), df(xn)), font_size=28),
                MathTex(r"x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)} = %.4f" % xn1,
                        font_size=28, color=YELLOW)
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(eixos_conv, DOWN, buff=0.75).align_to(eixos_conv, LEFT)

        # Montagem inicial
        self.add(titulo, equacao, eixos, labels)
        self.play(Create(curva), run_time=1.5)
        self.play(Write(formula))
        self.wait(1.5)
        self.play(FadeOut(formula), Create(eixos_conv), FadeIn(labels_conv))

        # Ponto inicial x0 (no eixo e no gráfico de convergência)
        ponto_x0 = Dot(eixos.c2p(x0, 0), color=YELLOW, radius=0.06)
        label_x0 = MathTex("x_0", color=YELLOW, font_size=30).next_to(ponto_x0, DOWN, buff=0.15)
        ponto_conv_ant = Dot(eixos_conv.c2p(0, x0), color=YELLOW, radius=0.06)
        self.play(FadeIn(ponto_x0, label_x0, ponto_conv_ant))

        # --- Iterações ---
        painel_ant = None
        for n in range(n_iter):
            xn, xn1 = xs[n], xs[n + 1]

            tracejada = DashedLine(eixos.c2p(xn, 0), eixos.c2p(xn, f(xn)),
                                   color=GREY_B, stroke_width=2)
            ponto_curva = Dot(eixos.c2p(xn, f(xn)), color=YELLOW)

            # Reta tangente em (x_n, f(x_n)), prolongada até cruzar o eixo x
            def tang(x, xn=xn):
                return f(xn) + df(xn) * (x - xn)
            x_lo, x_hi = min(xn, xn1) - 0.06, max(xn, xn1) + 0.06
            tangente = Line(eixos.c2p(x_lo, tang(x_lo)), eixos.c2p(x_hi, tang(x_hi)),
                            color=ORANGE, stroke_width=3)

            ponto_novo = Dot(eixos.c2p(xn1, 0), color=YELLOW, radius=0.06)

            ponto_conv = Dot(eixos_conv.c2p(n + 1, xn1), color=YELLOW, radius=0.06)
            seg_conv = Line(ponto_conv_ant.get_center(), ponto_conv.get_center(),
                            color=YELLOW, stroke_width=2)

            painel = painel_iteracao(n)
            if painel_ant is None:
                self.play(Create(tracejada), FadeIn(ponto_curva), FadeIn(painel))
            else:
                self.play(Create(tracejada), FadeIn(ponto_curva),
                          ReplacementTransform(painel_ant, painel))
            self.play(Create(tangente))
            self.play(FadeIn(ponto_novo), Flash(ponto_novo, color=ORANGE, flash_radius=0.3),
                      FadeIn(ponto_conv), Create(seg_conv))
            self.wait(1.0)

            # Limpa a construção, deixando a tangente como rastro tênue
            self.play(FadeOut(tracejada, ponto_curva),
                      tangente.animate.set_stroke(opacity=0.25), run_time=0.6)
            painel_ant = painel
            ponto_conv_ant = ponto_conv

        # --- Raiz encontrada ---
        raiz = xs[-1]
        linha_raiz = DashedLine(eixos_conv.c2p(0, raiz), eixos_conv.c2p(n_iter + 1, raiz),
                                color=GREY_B, stroke_width=2)
        label_raiz = MathTex(r"x^*", color=GREY_B, font_size=30).next_to(
            eixos_conv.c2p(0, raiz), LEFT, buff=0.15)
        resultado = MathTex(r"x^* \approx %.4f" % raiz, font_size=40, color=YELLOW
                            ).next_to(eixos_conv, DOWN, buff=1.0)
        ponto_raiz = Dot(eixos.c2p(raiz, 0), color=YELLOW, radius=0.09)
        self.play(FadeOut(painel_ant, ponto_x0, label_x0),
                  FadeIn(ponto_raiz), Flash(ponto_raiz, color=YELLOW),
                  Create(linha_raiz), FadeIn(label_raiz))
        self.play(Write(resultado))
        self.wait(2)
