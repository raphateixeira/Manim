from manim import *
import numpy as np

# Cálculo Numérico - Método da Bissecção para raízes de equações transcendentais
# Exemplo: f(x) = e^{-x} - sen(x) = 0  (primeira raiz ~ 0.5885)
class Bisseccao(Scene):
    def construct(self):
        def f(x):
            return np.exp(-x) - np.sin(x)

        a0, b0, n_iter = 0.0, 1.5, 6
        y_min, y_max = -1.4, 1.5

        # Título e equação
        titulo = Text("Método da Bissecção", font_size=34).to_edge(UP)
        equacao = MathTex(r"f(x) = e^{-x} - \operatorname{sen}(x) = 0").scale(0.7).next_to(titulo, DOWN, buff=0.2)

        # --- Gráfico da função (janela ampla: mostra outras raízes fora de [a, b]) ---
        eixos = Axes(
            x_range=[-0.3, 4.3, 1], y_range=[y_min, y_max, 0.5],
            x_length=6.0, y_length=4.4,
            axis_config={"tip_length": 0.15}
        ).to_edge(LEFT, buff=0.6).shift(DOWN * 0.8)
        labels = eixos.get_axis_labels(x_label="x", y_label="f(x)")
        curva = eixos.plot(f, x_range=[-0.25, 4.2], color=BLUE)

        # Extremos do intervalo controlados por trackers
        tracker_a, tracker_b = ValueTracker(a0), ValueTracker(b0)

        regiao = always_redraw(lambda: Polygon(
            eixos.c2p(tracker_a.get_value(), y_min),
            eixos.c2p(tracker_b.get_value(), y_min),
            eixos.c2p(tracker_b.get_value(), y_max),
            eixos.c2p(tracker_a.get_value(), y_max),
            stroke_width=0, fill_color=YELLOW, fill_opacity=0.12
        ))

        def linha_vertical(tracker, cor):
            return always_redraw(lambda: DashedLine(
                eixos.c2p(tracker.get_value(), y_min),
                eixos.c2p(tracker.get_value(), y_max),
                color=cor, stroke_width=2
            ))

        linha_a = linha_vertical(tracker_a, GREEN)
        linha_b = linha_vertical(tracker_b, RED)
        label_a = always_redraw(lambda: MathTex("a", color=GREEN, font_size=32).next_to(
            eixos.c2p(tracker_a.get_value(), y_min), DOWN, buff=0.15))
        label_b = always_redraw(lambda: MathTex("b", color=RED, font_size=32).next_to(
            eixos.c2p(tracker_b.get_value(), y_min), DOWN, buff=0.15))

        # --- Gráfico de convergência: c_n em função da iteração n ---
        eixos_conv = Axes(
            x_range=[0, n_iter + 1, 1], y_range=[0.3, 0.85, 0.1],
            x_length=4.6, y_length=2.9,
            axis_config={"tip_length": 0.12}
        ).to_edge(RIGHT, buff=0.6).shift(UP * 1.0)
        labels_conv = eixos_conv.get_axis_labels(x_label="n", y_label="c_n")

        # --- Painel de informações (abaixo do gráfico de convergência) ---
        condicao = MathTex(r"f(a)\,f(b) < 0 \;\Rightarrow\; \exists\ x^* \in [a, b]",
                           font_size=32).to_edge(RIGHT, buff=0.6).shift(UP * 1.0)

        def painel_iteracao(n, a, b, c):
            fc = f(c)
            if f(a) * fc < 0:
                decisao = r"f(a)\,f(c) < 0 \;\Rightarrow\; b \leftarrow c"
            else:
                decisao = r"f(c)\,f(b) < 0 \;\Rightarrow\; a \leftarrow c"
            return VGroup(
                MathTex(r"n = %d:\quad c = \frac{a + b}{2} = %.4f" % (n, c), font_size=28),
                MathTex(r"f(c) = %+.4f" % fc, font_size=28),
                MathTex(decisao, font_size=28, color=YELLOW),
                MathTex(r"b - a = %.4f" % (b - a), font_size=28)
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.28).next_to(eixos_conv, DOWN, buff=0.75).align_to(eixos_conv, LEFT)

        # Montagem inicial
        self.add(titulo, equacao, eixos, labels)
        self.play(Create(curva), run_time=1.5)
        self.play(FadeIn(regiao, linha_a, linha_b, label_a, label_b), Write(condicao))

        # Sinais nos extremos iniciais
        ponto_fa = Dot(eixos.c2p(a0, f(a0)), color=GREEN)
        ponto_fb = Dot(eixos.c2p(b0, f(b0)), color=RED)
        sinal_fa = MathTex("+", color=GREEN, font_size=36).next_to(ponto_fa, UR, buff=0.1)
        sinal_fb = MathTex("-", color=RED, font_size=36).next_to(ponto_fb, UR, buff=0.1)
        self.play(FadeIn(ponto_fa, ponto_fb, sinal_fa, sinal_fb))
        self.wait(1.5)

        # A condição sai de cena e entra o gráfico de convergência
        self.play(FadeOut(ponto_fa, ponto_fb, sinal_fa, sinal_fb, condicao),
                  Create(eixos_conv), FadeIn(labels_conv))

        # --- Iterações ---
        painel_ant = None
        ponto_conv_ant = None
        for n in range(1, n_iter + 1):
            a, b = tracker_a.get_value(), tracker_b.get_value()
            c = (a + b) / 2

            ponto_c = Dot(eixos.c2p(c, f(c)), color=YELLOW)
            linha_c = DashedLine(eixos.c2p(c, y_min), eixos.c2p(c, f(c)),
                                 color=YELLOW, stroke_width=2)
            label_c = MathTex("c", color=YELLOW, font_size=32).next_to(
                eixos.c2p(c, y_min), DOWN, buff=0.15)

            # Ponto novo no gráfico de convergência, ligado ao anterior
            ponto_conv = Dot(eixos_conv.c2p(n, c), color=YELLOW, radius=0.06)
            anim_conv = [FadeIn(ponto_conv)]
            if ponto_conv_ant is not None:
                anim_conv.append(Create(Line(
                    ponto_conv_ant.get_center(), ponto_conv.get_center(),
                    color=YELLOW, stroke_width=2
                )))

            painel = painel_iteracao(n, a, b, c)
            if painel_ant is None:
                self.play(Create(linha_c), FadeIn(ponto_c, label_c),
                          FadeIn(painel), *anim_conv)
            else:
                self.play(Create(linha_c), FadeIn(ponto_c, label_c),
                          ReplacementTransform(painel_ant, painel), *anim_conv)
            self.wait(1.2)

            # Atualiza o extremo que perde o lugar para c
            if f(a) * f(c) < 0:
                movimento = tracker_b.animate.set_value(c)
            else:
                movimento = tracker_a.animate.set_value(c)
            self.play(movimento, FadeOut(ponto_c, linha_c, label_c), run_time=1.0)
            painel_ant = painel
            ponto_conv_ant = ponto_conv

        # --- Raiz encontrada ---
        raiz = (tracker_a.get_value() + tracker_b.get_value()) / 2
        ponto_raiz = Dot(eixos.c2p(raiz, 0), color=YELLOW, radius=0.09)
        linha_raiz = DashedLine(eixos_conv.c2p(0, raiz), eixos_conv.c2p(n_iter + 1, raiz),
                                color=GREY_B, stroke_width=2)
        label_raiz = MathTex(r"x^*", color=GREY_B, font_size=30).next_to(
            eixos_conv.c2p(n_iter + 1, raiz), RIGHT, buff=0.1)
        resultado = MathTex(r"x^* \approx %.4f" % raiz, font_size=40, color=YELLOW
                            ).next_to(eixos_conv, DOWN, buff=1.0)
        self.play(FadeOut(painel_ant, regiao, linha_a, linha_b, label_a, label_b),
                  FadeIn(ponto_raiz), Flash(ponto_raiz, color=YELLOW),
                  Create(linha_raiz), FadeIn(label_raiz))
        self.play(Write(resultado))
        self.wait(2)
