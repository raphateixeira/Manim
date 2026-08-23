from manim import *
import numpy as np

# Cálculo Numérico - Método do Ponto Fixo (iteração x = g(x))
# Exemplo: x = e^{-x}  (raiz ~ 0.5671), diagrama de teia (cobweb)
class PontoFixo(Scene):
    def construct(self):
        def g(x):
            return np.exp(-x)

        x0, n_iter = 0.1, 10
        xs = [x0]
        for _ in range(n_iter):
            xs.append(g(xs[-1]))

        # Título e equação
        titulo = Text("Método do Ponto Fixo", font_size=34).to_edge(UP)
        equacao = MathTex(r"x = g(x) = e^{-x}").scale(0.7).next_to(titulo, DOWN, buff=0.2)

        # --- Diagrama de teia: g(x) e a reta y = x ---
        eixos = Axes(
            x_range=[0, 1.2, 0.2], y_range=[0, 1.2, 0.2],
            x_length=5.2, y_length=4.4,
            axis_config={"tip_length": 0.15}
        ).to_edge(LEFT, buff=0.8).shift(DOWN * 0.8)
        labels = eixos.get_axis_labels(x_label="x", y_label="y")
        curva = eixos.plot(g, x_range=[0, 1.15], color=BLUE)
        diagonal = eixos.plot(lambda x: x, x_range=[0, 1.15], color=GREY_B)
        label_g = MathTex("y = g(x)", color=BLUE, font_size=28).next_to(
            eixos.c2p(1.15, g(1.15)), DOWN, buff=0.2)
        label_d = MathTex("y = x", color=GREY_B, font_size=28).next_to(
            eixos.c2p(1.15, 1.15), UP, buff=0.15)

        # --- Gráfico de convergência: x_n em função da iteração n ---
        eixos_conv = Axes(
            x_range=[0, n_iter + 1, 1], y_range=[0, 1.1, 0.2],
            x_length=4.6, y_length=2.9,
            axis_config={"tip_length": 0.12}
        ).to_edge(RIGHT, buff=0.6).shift(UP * 0.75)
        labels_conv = eixos_conv.get_axis_labels(x_label="n", y_label="x_n")

        # Condição de convergência (mostrada na introdução)
        condicao = MathTex(r"|g'(x^*)| < 1 \;\Rightarrow\; x_{n+1} = g(x_n) \text{ converge}",
                           font_size=32).to_edge(RIGHT, buff=0.6).shift(UP * 0.75)

        # Montagem inicial
        self.add(titulo, equacao, eixos, labels)
        self.play(Create(curva), Create(diagonal), FadeIn(label_g, label_d), run_time=1.5)
        self.play(Write(condicao))
        self.wait(1.5)
        self.play(FadeOut(condicao), Create(eixos_conv), FadeIn(labels_conv))

        # Ponto inicial
        ponto_x0 = Dot(eixos.c2p(x0, 0), color=YELLOW, radius=0.06)
        label_x0 = MathTex("x_0", color=YELLOW, font_size=30).next_to(ponto_x0, DOWN, buff=0.15)
        ponto_conv_ant = Dot(eixos_conv.c2p(0, x0), color=YELLOW, radius=0.05)
        self.play(FadeIn(ponto_x0, label_x0, ponto_conv_ant))

        # --- Iterações (teia: vertical até g, horizontal até y = x) ---
        painel_ant = None
        y_atual = 0.0
        for n in range(n_iter):
            x_atual, x_prox = xs[n], xs[n + 1]

            vert = Line(eixos.c2p(x_atual, y_atual), eixos.c2p(x_atual, x_prox),
                        color=YELLOW, stroke_width=2)
            ponto_g = Dot(eixos.c2p(x_atual, x_prox), color=YELLOW, radius=0.05)
            horiz = Line(eixos.c2p(x_atual, x_prox), eixos.c2p(x_prox, x_prox),
                         color=YELLOW, stroke_width=2)

            ponto_conv = Dot(eixos_conv.c2p(n + 1, x_prox), color=YELLOW, radius=0.05)
            seg_conv = Line(ponto_conv_ant.get_center(), ponto_conv.get_center(),
                            color=YELLOW, stroke_width=2)

            painel = MathTex(r"n = %d:\quad x_{n+1} = e^{-x_n} = %.4f" % (n, x_prox),
                             font_size=30).next_to(eixos_conv, DOWN, buff=0.75)
            if painel_ant is None:
                anim_painel = FadeIn(painel)
            else:
                anim_painel = ReplacementTransform(painel_ant, painel)

            self.play(Create(vert), FadeIn(ponto_g), anim_painel,
                      FadeIn(ponto_conv), Create(seg_conv), run_time=0.7)
            self.play(Create(horiz), run_time=0.5)
            self.wait(0.3)

            painel_ant = painel
            ponto_conv_ant = ponto_conv
            y_atual = x_prox

        # --- Ponto fixo encontrado ---
        raiz = xs[-1]
        ponto_fixo = Dot(eixos.c2p(raiz, raiz), color=YELLOW, radius=0.09)
        linha_raiz = DashedLine(eixos_conv.c2p(0, raiz), eixos_conv.c2p(n_iter + 1, raiz),
                                color=GREY_B, stroke_width=2)
        label_raiz = MathTex(r"x^*", color=GREY_B, font_size=30).next_to(
            eixos_conv.c2p(n_iter + 1, raiz), RIGHT, buff=0.1)
        resultado = MathTex(r"x^* \approx %.4f" % raiz, font_size=40, color=YELLOW
                            ).next_to(eixos_conv, DOWN, buff=1.0)
        self.play(FadeOut(painel_ant, ponto_x0, label_x0),
                  FadeIn(ponto_fixo), Flash(ponto_fixo, color=YELLOW),
                  Create(linha_raiz), FadeIn(label_raiz))
        self.play(Write(resultado))
        self.wait(2)
