from manim import *
import numpy as np

# Circuitos Elétricos - Geração de corrente alternada: fasor girante x sinal no tempo

config.background_color = WHITE

# --- Paleta UFPA (fundo claro) ---
UFPA_BLUE = "#002C6F"
UFPA_GOLD = "#B8860B"        # dourado escurecido para contraste sobre fundo branco
AXIS_GREY = "#6C757D"
VERMELHO = "#C0392B"
CURVA_AZUL = UFPA_BLUE


class GeradorCA(Scene):
    def construct(self):
        # --- Parâmetros físicos ---
        Vm = 1.0
        omega = TAU                 # 2π rad/s → 1 ciclo por segundo
        n_ciclos_total = 10         # ciclos completos do fasor na circunferência
        n_ciclos_janela = 2         # ciclos mantidos visíveis (janela deslizante) no gráfico
        t_max = n_ciclos_total * TAU / omega
        janela = n_ciclos_janela * TAU

        tracker_t = ValueTracker(0)
        theta = lambda: omega * tracker_t.get_value()

        titulo = Text("Gerador de Corrente Alternada", font_size=34,
                       color=UFPA_BLUE, weight=BOLD).to_edge(UP, buff=0.35)

        # --- Diagrama fasorial (estator) ---
        eixos_fasor = Axes(
            x_range=[-1.4, 1.4, 1], y_range=[-1.4, 1.4, 1],
            x_length=4.6, y_length=4.6,
            axis_config={"include_tip": False, "stroke_color": AXIS_GREY, "stroke_width": 1.5},
        ).to_edge(LEFT, buff=0.9).shift(DOWN * 0.35)

        origem = eixos_fasor.c2p(0, 0)
        raio_tela = np.linalg.norm(eixos_fasor.c2p(Vm, 0) - origem)

        estator = Circle(radius=raio_tela, color=UFPA_BLUE, stroke_width=3).move_to(origem)
        label_estator = Text("Domínio Fasorial", font_size=24, color=UFPA_BLUE
                              ).next_to(estator, DOWN, buff=0.5)

        def get_ponta():
            th = theta()
            return eixos_fasor.c2p(Vm * np.cos(th), Vm * np.sin(th))

        def get_projecao():
            th = theta()
            return eixos_fasor.c2p(Vm * np.cos(th), 0)

        fasor = always_redraw(lambda: Arrow(
            origem, get_ponta(), buff=0, color=UFPA_GOLD, stroke_width=6,
            max_tip_length_to_length_ratio=0.18
        ))
        ponto_ponta = always_redraw(lambda: Dot(get_ponta(), color=VERMELHO, radius=0.09))

        arco_theta = always_redraw(lambda: Arc(
            radius=0.5, start_angle=0, angle=theta() % TAU,
            arc_center=origem, color=UFPA_GOLD, stroke_width=3
        ))

        label_angulo = always_redraw(lambda: MathTex(
            r"\theta = %d^\circ" % round(np.degrees(theta()) % 360),
            font_size=26, color=UFPA_BLUE
        ).move_to(estator.get_corner(UL) + UP * 0.35 + RIGHT * 0.5))

        linha_projecao = always_redraw(lambda: DashedLine(
            get_ponta(), get_projecao(), color=AXIS_GREY, stroke_width=2, dash_length=0.08
        ))
        ponto_projecao = always_redraw(lambda: Dot(get_projecao(), color=UFPA_GOLD, radius=0.05))

        # --- Gráfico de tempo (janela deslizante de n_ciclos_janela ciclos) ---
        eixos_t = Axes(
            x_range=[0, janela, PI / 2], y_range=[-1.4, 1.4, 1],
            x_length=6.4, y_length=4.6,
            axis_config={"include_tip": False, "stroke_color": AXIS_GREY, "stroke_width": 1.5},
        ).to_edge(RIGHT, buff=0.8).shift(DOWN * 0.35)
        labels_t = eixos_t.get_axis_labels(
            x_label=MathTex(r"\omega t", color=AXIS_GREY).scale(0.7),
            y_label=MathTex("v(t)", color=AXIS_GREY).scale(0.7),
        )

        label_grafico = MathTex(
            r"\text{Domínio do Tempo: } v(t) = \cos(\omega t)",
            font_size=28, color=UFPA_BLUE
        ).next_to(eixos_t, DOWN, buff=0.5)
        legenda_janela = Text(f"(janela deslizante — últimos {n_ciclos_janela} ciclos)",
                               font_size=18, color=AXIS_GREY).next_to(label_grafico, DOWN, buff=0.15)

        def s_max_agora():
            # posição (em fase) do instante atual dentro da janela visível;
            # cresce de 0 até "janela" e depois fica fixa na borda direita
            return min(theta(), janela)

        def get_ponto_v():
            return eixos_t.c2p(s_max_agora(), Vm * np.cos(theta()))

        ponto_v = always_redraw(lambda: Dot(get_ponto_v(), color=VERMELHO, radius=0.07))

        def get_curva_janela():
            s_max = s_max_agora()
            th_fim = theta()
            th_ini = th_fim - s_max
            if s_max < 1e-3:
                return VMobject()
            return eixos_t.plot(lambda s: Vm * np.cos(th_ini + s), x_range=[0, s_max],
                                 color=CURVA_AZUL, stroke_width=4)

        rastro_v = always_redraw(get_curva_janela)

        # Linha tracejada vertical: marca o instante atual dentro do gráfico,
        # ligando o eixo do tempo ao ponto correspondente na curva v(t).
        def get_base_tempo():
            return eixos_t.c2p(s_max_agora(), 0)

        linha_playhead = always_redraw(lambda: DashedLine(
            get_base_tempo(), get_ponto_v(), color=VERMELHO, stroke_width=2, dash_length=0.08
        ))

        self.play(
            Create(eixos_fasor), Create(estator), Create(eixos_t),
            FadeIn(titulo, label_estator, label_grafico, labels_t, legenda_janela),
            run_time=1.0
        )
        self.add(rastro_v, fasor, ponto_ponta, arco_theta, label_angulo,
                 linha_projecao, ponto_projecao, linha_playhead, ponto_v)

        self.play(tracker_t.animate.set_value(t_max), run_time=17, rate_func=linear)
        self.wait(2)
