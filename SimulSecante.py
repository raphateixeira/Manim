from manim import *
import numpy as np

# Cálculo Numérico - Método da Secante
# Exemplo: f(x) = cos(x) - x = 0  (raiz ~ 0.7391)
class Secante(Scene):
    def construct(self):
        def f(x):
            return np.cos(x) - x

        x_a, x_b, n_iter = 0.0, 1.5, 4
        xs = [x_a, x_b]
        for _ in range(n_iter):
            x0, x1 = xs[-2], xs[-1]
            xs.append(x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0)))

        y_min, y_max = -1.7, 1.5

        # Título e equação
        titulo = Text("Método da Secante", font_size=34).to_edge(UP)
        equacao = MathTex(r"f(x) = \cos(x) - x = 0").scale(0.7).next_to(titulo, DOWN, buff=0.2)

        # --- Gráfico da função ---
        eixos = Axes(
            x_range=[-0.4, 1.9, 0.5], y_range=[y_min, y_max, 0.5],
            x_length=6.0, y_length=4.4,
            axis_config={"tip_length": 0.15}
        ).to_edge(LEFT, buff=0.6).shift(DOWN * 0.8)
        labels = eixos.get_axis_labels(x_label="x", y_label="f(x)")
        curva = eixos.plot(f, x_range=[-0.35, 1.8], color=BLUE)

        # --- Gráfico de convergência: x_n em função da iteração n ---
        eixos_conv = Axes(
            x_range=[0, n_iter + 2, 1], y_range=[-0.1, 1.7, 0.5],
            x_length=4.6, y_length=2.9,
            axis_config={"tip_length": 0.12}
        ).to_edge(RIGHT, buff=0.6).shift(UP * 0.75)
        labels_conv = eixos_conv.get_axis_labels(x_label="n", y_label="x_n")

        # Fórmula do método (mostrada na introdução)
        formula = MathTex(
            r"x_{n+1} = x_n - f(x_n)\,\frac{x_n - x_{n-1}}{f(x_n) - f(x_{n-1})}",
            font_size=32).to_edge(RIGHT, buff=0.7).shift(UP * 0.75)

        def painel_iteracao(k):
            x0, x1, x2 = xs[k - 1], xs[k], xs[k + 1]
            return VGroup(
                MathTex(r"n = %d:\quad x_{n-1} = %.4f,\quad x_n = %.4f" % (k, x0, x1),
                        font_size=28),
                MathTex(r"f(x_{n-1}) = %+.4f,\quad f(x_n) = %+.4f" % (f(x0), f(x1)),
                        font_size=28),
                MathTex(r"x_{n+1} = %.4f" % x2, font_size=28, color=YELLOW)
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(eixos_conv, DOWN, buff=0.75).align_to(eixos_conv, LEFT)

        # Montagem inicial
        self.add(titulo, equacao, eixos, labels)
        self.play(Create(curva), run_time=1.5)
        self.play(Write(formula))
        self.wait(1.5)
        self.play(FadeOut(formula), Create(eixos_conv), FadeIn(labels_conv))

        # Pontos iniciais x0 e x1
        ponto_a = Dot(eixos.c2p(x_a, 0), color=YELLOW, radius=0.06)
        ponto_b = Dot(eixos.c2p(x_b, 0), color=YELLOW, radius=0.06)
        label_pa = MathTex("x_0", color=YELLOW, font_size=30).next_to(ponto_a, DOWN, buff=0.15)
        label_pb = MathTex("x_1", color=YELLOW, font_size=30).next_to(ponto_b, DOWN, buff=0.15)
        conv_0 = Dot(eixos_conv.c2p(0, x_a), color=YELLOW, radius=0.06)
        conv_1 = Dot(eixos_conv.c2p(1, x_b), color=YELLOW, radius=0.06)
        seg_01 = Line(conv_0.get_center(), conv_1.get_center(), color=YELLOW, stroke_width=2)
        self.play(FadeIn(ponto_a, ponto_b, label_pa, label_pb, conv_0, conv_1), Create(seg_01))

        # --- Iterações ---
        painel_ant = None
        ponto_conv_ant = conv_1
        for k in range(1, n_iter + 1):
            x0, x1, x2 = xs[k - 1], xs[k], xs[k + 1]

            p0 = Dot(eixos.c2p(x0, f(x0)), color=YELLOW)
            p1 = Dot(eixos.c2p(x1, f(x1)), color=YELLOW)
            d0 = DashedLine(eixos.c2p(x0, 0), eixos.c2p(x0, f(x0)), color=GREY_B, stroke_width=2)
            d1 = DashedLine(eixos.c2p(x1, 0), eixos.c2p(x1, f(x1)), color=GREY_B, stroke_width=2)

            # Reta secante pelos dois últimos pontos, prolongada até o eixo x
            def sec(x, x0=x0, x1=x1):
                return f(x0) + (f(x1) - f(x0)) / (x1 - x0) * (x - x0)
            x_lo, x_hi = min(x0, x1, x2) - 0.06, max(x0, x1, x2) + 0.06
            secante = Line(eixos.c2p(x_lo, sec(x_lo)), eixos.c2p(x_hi, sec(x_hi)),
                           color=ORANGE, stroke_width=3)

            ponto_novo = Dot(eixos.c2p(x2, 0), color=YELLOW, radius=0.06)

            ponto_conv = Dot(eixos_conv.c2p(k + 1, x2), color=YELLOW, radius=0.06)
            seg_conv = Line(ponto_conv_ant.get_center(), ponto_conv.get_center(),
                            color=YELLOW, stroke_width=2)

            painel = painel_iteracao(k)
            if painel_ant is None:
                self.play(Create(d0), Create(d1), FadeIn(p0, p1), FadeIn(painel))
            else:
                self.play(Create(d0), Create(d1), FadeIn(p0, p1),
                          ReplacementTransform(painel_ant, painel))
            self.play(Create(secante))
            self.play(FadeIn(ponto_novo), Flash(ponto_novo, color=ORANGE, flash_radius=0.3),
                      FadeIn(ponto_conv), Create(seg_conv))
            self.wait(1.0)

            self.play(FadeOut(d0, d1, p0, p1),
                      secante.animate.set_stroke(opacity=0.25), run_time=0.6)
            painel_ant = painel
            ponto_conv_ant = ponto_conv

        # --- Raiz encontrada ---
        raiz = xs[-1]
        linha_raiz = DashedLine(eixos_conv.c2p(0, raiz), eixos_conv.c2p(n_iter + 2, raiz),
                                color=GREY_B, stroke_width=2)
        label_raiz = MathTex(r"x^*", color=GREY_B, font_size=30).next_to(
            eixos_conv.c2p(n_iter + 2, raiz), RIGHT, buff=0.1)
        resultado = MathTex(r"x^* \approx %.4f" % raiz, font_size=40, color=YELLOW
                            ).next_to(eixos_conv, DOWN, buff=1.0)
        ponto_raiz = Dot(eixos.c2p(raiz, 0), color=YELLOW, radius=0.09)
        self.play(FadeOut(painel_ant, ponto_a, ponto_b, label_pa, label_pb),
                  FadeIn(ponto_raiz), Flash(ponto_raiz, color=YELLOW),
                  Create(linha_raiz), FadeIn(label_raiz))
        self.play(Write(resultado))
        self.wait(2)
