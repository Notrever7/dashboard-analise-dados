import tkinter as tk
from tkinter import font as tkfont, filedialog, messagebox, ttk
import csv
import os

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ════════════════════════════════════════
#  CORES
# ════════════════════════════════════════

CORES = {
    "bg": "#0f0f13",
    "surface": "#1a1a24",
    "border": "#2a2a3a",
    "accent": "#7c6cfc",
    "accent2": "#4cc9f0",
    "accent3": "#f72585",
    "accent4": "#fca311",
    "correct": "#3ddc84",
    "wrong": "#ff5c5c",
    "text": "#e8e8f0",
    "muted": "#7a7a9a",
    "chart_bg": "#12121a",
}

PALETA = ["#7c6cfc", "#4cc9f0", "#f72585", "#fca311", "#3ddc84", "#ff5c5c", "#a78bfa", "#06d6a0"]


# ════════════════════════════════════════
#  LER CSV GENÉRICO
# ════════════════════════════════════════

def ler_csv(caminho):
    """Lê qualquer CSV e retorna colunas, tipos e dados."""
    with open(caminho, newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        colunas = leitor.fieldnames
        dados = {col: [] for col in colunas}
        for linha in leitor:
            for col in colunas:
                dados[col].append(linha[col].strip())

    # Detectar tipo de cada coluna
    tipos = {}
    for col in colunas:
        numeros = 0
        for val in dados[col]:
            try:
                float(val.replace(",", "."))
                numeros += 1
            except ValueError:
                pass
        # Se mais de 70% dos valores são números, é numérica
        tipos[col] = "numero" if numeros / max(len(dados[col]), 1) > 0.7 else "texto"

    # Converter numéricas
    for col in colunas:
        if tipos[col] == "numero":
            convertidos = []
            for val in dados[col]:
                try:
                    convertidos.append(float(val.replace(",", ".")))
                except ValueError:
                    convertidos.append(0.0)
            dados[col] = convertidos

    return colunas, tipos, dados


# ════════════════════════════════════════
#  CLASSE PRINCIPAL
# ════════════════════════════════════════

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard — Análise de Dados")
        self.root.configure(bg=CORES["bg"])

        largura, altura = 1100, 750
        x = (self.root.winfo_screenwidth() - largura) // 2
        y = (self.root.winfo_screenheight() - altura) // 2
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")
        self.root.minsize(800, 600)

        # Fontes
        self.font_titulo = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.font_card_num = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        self.font_card_label = tkfont.Font(family="Segoe UI", size=10)
        self.font_btn = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.font_small = tkfont.Font(family="Segoe UI", size=9)
        self.font_combo = tkfont.Font(family="Segoe UI", size=10)

        # Estilo do combobox
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TCombobox",
            fieldbackground=CORES["surface"],
            background=CORES["accent"],
            foreground=CORES["text"],
            arrowcolor=CORES["text"],
            bordercolor=CORES["border"],
            lightcolor=CORES["border"],
            darkcolor=CORES["border"],
        )
        style.map("Dark.TCombobox",
            fieldbackground=[("readonly", CORES["surface"])],
            foreground=[("readonly", CORES["text"])],
        )

        # Estado
        self.colunas = []
        self.tipos = {}
        self.dados = {}
        self.caminho_csv = None

        # Tentar CSV padrão
        pasta = os.path.dirname(os.path.abspath(__file__))
        csv_padrao = os.path.join(pasta, "dados_vendas.csv")
        if os.path.exists(csv_padrao):
            self.carregar_dados(csv_padrao)

        self.construir_interface()

    def carregar_dados(self, caminho):
        self.colunas, self.tipos, self.dados = ler_csv(caminho)
        self.caminho_csv = caminho
        self.cols_num = [c for c in self.colunas if self.tipos[c] == "numero"]
        self.cols_texto = [c for c in self.colunas if self.tipos[c] == "texto"]

    # ──────────────────────────────────
    #  INTERFACE PRINCIPAL
    # ──────────────────────────────────
    def construir_interface(self):
        for w in self.root.winfo_children():
            w.destroy()

        # ── TOPO ──
        topo = tk.Frame(self.root, bg=CORES["bg"], padx=24, pady=14)
        topo.pack(fill="x")

        tk.Label(
            topo, text="📊  Dashboard Inteligente", font=self.font_titulo,
            bg=CORES["bg"], fg=CORES["text"]
        ).pack(side="left")

        btn_carregar = tk.Label(
            topo, text="📁 Carregar CSV", font=self.font_btn,
            bg=CORES["accent"], fg="#fff", padx=16, pady=8, cursor="hand2"
        )
        btn_carregar.pack(side="right")
        btn_carregar.bind("<Enter>", lambda e: btn_carregar.configure(bg="#9588ff"))
        btn_carregar.bind("<Leave>", lambda e: btn_carregar.configure(bg=CORES["accent"]))
        btn_carregar.bind("<Button-1>", lambda e: self.abrir_csv())

        if self.caminho_csv:
            nome = os.path.basename(self.caminho_csv)
            tk.Label(
                topo, text=f"  {nome}", font=self.font_small,
                bg=CORES["bg"], fg=CORES["muted"]
            ).pack(side="right", padx=(0, 12))

        if not self.dados:
            self.tela_vazia()
            return

        # ── INFO DO ARQUIVO ──
        info_frame = tk.Frame(self.root, bg=CORES["bg"], padx=24)
        info_frame.pack(fill="x", pady=(0, 4))

        total_linhas = len(self.dados[self.colunas[0]])
        total_cols = len(self.colunas)
        nums = len(self.cols_num)
        textos = len(self.cols_texto)

        tk.Label(
            info_frame,
            text=f"{total_linhas} linhas  •  {total_cols} colunas  •  {nums} numéricas  •  {textos} texto",
            font=self.font_small, bg=CORES["bg"], fg=CORES["muted"]
        ).pack(side="left")

        # ── CARDS RESUMO (colunas numéricas) ──
        if self.cols_num:
            cards_frame = tk.Frame(self.root, bg=CORES["bg"], padx=24)
            cards_frame.pack(fill="x", pady=(8, 4))

            # Mostrar no máximo 4 cards
            cols_card = self.cols_num[:4]
            for i in range(len(cols_card)):
                cards_frame.columnconfigure(i, weight=1, uniform="card")

            for i, col in enumerate(cols_card):
                valores = self.dados[col]
                total = sum(valores)
                media = total / len(valores) if valores else 0
                cor = PALETA[i % len(PALETA)]

                card = tk.Frame(cards_frame, bg=CORES["surface"], padx=16, pady=12)
                card.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)

                barra = tk.Frame(card, bg=cor, width=4, height=36)
                barra.pack(side="left", padx=(0, 12))

                info = tk.Frame(card, bg=CORES["surface"])
                info.pack(side="left", fill="x", expand=True)

                tk.Label(
                    info, text=col.upper(), font=self.font_card_label,
                    bg=CORES["surface"], fg=CORES["muted"], anchor="w"
                ).pack(fill="x")

                # Formatar número
                if total > 1000000:
                    texto_val = f"{total/1000000:.1f}M"
                elif total > 1000:
                    texto_val = f"{total/1000:.1f}K"
                else:
                    texto_val = f"{total:.1f}"

                tk.Label(
                    info, text=texto_val, font=self.font_card_num,
                    bg=CORES["surface"], fg=cor, anchor="w"
                ).pack(fill="x")

                tk.Label(
                    info, text=f"média: {media:,.1f}".replace(",", "."),
                    font=self.font_small, bg=CORES["surface"], fg=CORES["muted"], anchor="w"
                ).pack(fill="x")

        # ── SELETORES ──
        sel_frame = tk.Frame(self.root, bg=CORES["bg"], padx=24)
        sel_frame.pack(fill="x", pady=(8, 4))

        # Eixo X (texto ou qualquer)
        tk.Label(
            sel_frame, text="Eixo X (rótulos):", font=self.font_combo,
            bg=CORES["bg"], fg=CORES["muted"]
        ).pack(side="left", padx=(0, 6))

        opcoes_x = self.cols_texto if self.cols_texto else self.colunas
        self.var_eixo_x = tk.StringVar(value=opcoes_x[0] if opcoes_x else "")
        combo_x = ttk.Combobox(
            sel_frame, textvariable=self.var_eixo_x, values=opcoes_x,
            state="readonly", style="Dark.TCombobox", font=self.font_combo, width=15
        )
        combo_x.pack(side="left", padx=(0, 20))

        # Eixo Y (numérica)
        tk.Label(
            sel_frame, text="Eixo Y (valores):", font=self.font_combo,
            bg=CORES["bg"], fg=CORES["muted"]
        ).pack(side="left", padx=(0, 6))

        self.var_eixo_y = tk.StringVar(value=self.cols_num[0] if self.cols_num else "")
        combo_y = ttk.Combobox(
            sel_frame, textvariable=self.var_eixo_y, values=self.cols_num,
            state="readonly", style="Dark.TCombobox", font=self.font_combo, width=15
        )
        combo_y.pack(side="left", padx=(0, 20))

        # Segunda coluna Y (opcional)
        tk.Label(
            sel_frame, text="Comparar com:", font=self.font_combo,
            bg=CORES["bg"], fg=CORES["muted"]
        ).pack(side="left", padx=(0, 6))

        self.var_eixo_y2 = tk.StringVar(value="Nenhum")
        opcoes_y2 = ["Nenhum"] + self.cols_num
        combo_y2 = ttk.Combobox(
            sel_frame, textvariable=self.var_eixo_y2, values=opcoes_y2,
            state="readonly", style="Dark.TCombobox", font=self.font_combo, width=15
        )
        combo_y2.pack(side="left", padx=(0, 20))

        # Botão atualizar
        btn_att = tk.Label(
            sel_frame, text="🔄 Atualizar", font=self.font_btn,
            bg=CORES["correct"], fg="#000", padx=14, pady=6, cursor="hand2"
        )
        btn_att.pack(side="left")
        btn_att.bind("<Button-1>", lambda e: self.atualizar_graficos())

        # ── ÁREA DOS GRÁFICOS ──
        self.graficos_frame = tk.Frame(self.root, bg=CORES["bg"], padx=24, pady=8)
        self.graficos_frame.pack(fill="both", expand=True)

        self.atualizar_graficos()

    # ──────────────────────────────────
    #  ATUALIZAR GRÁFICOS
    # ──────────────────────────────────
    def atualizar_graficos(self):
        for w in self.graficos_frame.winfo_children():
            w.destroy()

        self.graficos_frame.columnconfigure(0, weight=1)
        self.graficos_frame.columnconfigure(1, weight=1)
        self.graficos_frame.rowconfigure(0, weight=1)
        self.graficos_frame.rowconfigure(1, weight=1)

        col_x = self.var_eixo_x.get()
        col_y = self.var_eixo_y.get()
        col_y2 = self.var_eixo_y2.get()

        if not col_x or not col_y:
            return

        rotulos = self.dados[col_x]
        valores = self.dados[col_y]

        # Abreviar rótulos se forem longos
        rotulos_curtos = [str(r)[:8] for r in rotulos]

        valores2 = None
        if col_y2 != "Nenhum" and col_y2 in self.dados:
            valores2 = self.dados[col_y2]

        # Gráfico 1 — Linhas
        self.grafico_linhas(rotulos_curtos, valores, col_y, valores2, col_y2, 0, 0)

        # Gráfico 2 — Barras
        self.grafico_barras(rotulos_curtos, valores, col_y, valores2, col_y2, 0, 1)

        # Gráfico 3 — Área
        self.grafico_area(rotulos_curtos, valores, col_y, 1, 0)

        # Gráfico 4 — Pizza (agrupa se muitos itens)
        self.grafico_pizza(rotulos, valores, col_y, 1, 1)

    # ──────────────────────────────────
    #  GRÁFICOS
    # ──────────────────────────────────
    def estilo(self, fig, ax):
        fig.patch.set_facecolor(CORES["chart_bg"])
        ax.set_facecolor(CORES["chart_bg"])
        ax.tick_params(colors=CORES["muted"], labelsize=7)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(CORES["border"])
        ax.spines["bottom"].set_color(CORES["border"])
        ax.title.set_color(CORES["text"])

    def embed(self, fig, row, col):
        frame = tk.Frame(self.graficos_frame, bg=CORES["surface"], padx=4, pady=4)
        frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def grafico_linhas(self, rotulos, valores, nome, valores2, nome2, row, col):
        fig = Figure(figsize=(5, 2.8), dpi=90)
        ax = fig.add_subplot(111)
        self.estilo(fig, ax)

        ax.plot(rotulos, valores, color=PALETA[0], linewidth=2, marker="o", markersize=3, label=nome)
        if valores2:
            ax.plot(rotulos, valores2, color=PALETA[2], linewidth=2, marker="s", markersize=3, label=nome2)
            ax.legend(fontsize=7, facecolor=CORES["chart_bg"], edgecolor=CORES["border"], labelcolor=CORES["text"])

        ax.set_title(f"Linha — {nome}", fontsize=10, fontweight="bold", pad=8)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout(pad=1.2)
        self.embed(fig, row, col)

    def grafico_barras(self, rotulos, valores, nome, valores2, nome2, row, col):
        fig = Figure(figsize=(5, 2.8), dpi=90)
        ax = fig.add_subplot(111)
        self.estilo(fig, ax)

        x = range(len(rotulos))
        largura = 0.35 if valores2 else 0.6

        ax.bar([i - largura/2 for i in x] if valores2 else x,
               valores, width=largura, color=PALETA[0], label=nome)
        if valores2:
            ax.bar([i + largura/2 for i in x], valores2, width=largura, color=PALETA[2], label=nome2)
            ax.legend(fontsize=7, facecolor=CORES["chart_bg"], edgecolor=CORES["border"], labelcolor=CORES["text"])

        ax.set_xticks(list(x))
        ax.set_xticklabels(rotulos, rotation=45)
        ax.set_title(f"Barras — {nome}", fontsize=10, fontweight="bold", pad=8)
        fig.tight_layout(pad=1.2)
        self.embed(fig, row, col)

    def grafico_area(self, rotulos, valores, nome, row, col):
        fig = Figure(figsize=(5, 2.8), dpi=90)
        ax = fig.add_subplot(111)
        self.estilo(fig, ax)

        ax.fill_between(rotulos, valores, alpha=0.3, color=PALETA[1])
        ax.plot(rotulos, valores, color=PALETA[1], linewidth=2, marker="o", markersize=3)
        ax.set_title(f"Área — {nome}", fontsize=10, fontweight="bold", pad=8)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout(pad=1.2)
        self.embed(fig, row, col)

    def grafico_pizza(self, rotulos, valores, nome, row, col):
        fig = Figure(figsize=(5, 2.8), dpi=90)
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor(CORES["chart_bg"])
        ax.set_facecolor(CORES["chart_bg"])

        # Se tiver muitos itens, agrupa os menores em "Outros"
        if len(rotulos) > 8:
            pares = sorted(zip(valores, rotulos), reverse=True)
            top = pares[:7]
            resto = sum(v for v, r in pares[7:])
            vals_pizza = [v for v, r in top] + [resto]
            labs_pizza = [str(r)[:10] for v, r in top] + ["Outros"]
        else:
            vals_pizza = valores
            labs_pizza = [str(r)[:10] for r in rotulos]

        cores_pizza = PALETA[:len(vals_pizza)]

        wedges, texts, autotexts = ax.pie(
            vals_pizza, labels=labs_pizza, autopct="%1.1f%%",
            colors=cores_pizza, startangle=90,
            textprops={"fontsize": 7, "color": CORES["text"]},
            wedgeprops={"edgecolor": CORES["chart_bg"], "linewidth": 2}
        )
        for t in autotexts:
            t.set_fontsize(6)
            t.set_color("#fff")

        ax.set_title(f"Distribuição — {nome}", fontsize=10, fontweight="bold",
                      pad=8, color=CORES["text"])
        fig.tight_layout(pad=1.2)
        self.embed(fig, row, col)

    # ──────────────────────────────────
    #  TELA VAZIA
    # ──────────────────────────────────
    def tela_vazia(self):
        centro = tk.Frame(self.root, bg=CORES["bg"])
        centro.pack(expand=True)

        tk.Label(centro, text="📂", font=tkfont.Font(size=48),
                 bg=CORES["bg"], fg=CORES["muted"]).pack(pady=(0, 16))
        tk.Label(centro, text="Nenhum arquivo carregado",
                 font=self.font_titulo, bg=CORES["bg"], fg=CORES["text"]).pack(pady=(0, 8))
        tk.Label(centro,
                 text="Clique em 'Carregar CSV' para começar.\nO dashboard detecta automaticamente as colunas.",
                 font=self.font_card_label, bg=CORES["bg"], fg=CORES["muted"], justify="center").pack()

    # ──────────────────────────────────
    #  CARREGAR CSV
    # ──────────────────────────────────
    def abrir_csv(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo CSV",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")]
        )
        if caminho:
            try:
                self.carregar_dados(caminho)
                self.construir_interface()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler o arquivo:\n{e}")


# ════════════════════════════════════════
#  INICIAR
# ════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
