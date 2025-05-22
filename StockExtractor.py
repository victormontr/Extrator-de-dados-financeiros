import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import yfinance as yf
from datetime import datetime # timedelta não é mais estritamente necessária com a lógica antiga
import os
import sys
import subprocess
import threading
import platform
from tkcalendar import DateEntry

# --- Configuração de DPI Awareness (Principalmente para Windows) ---
if platform.system() == "Windows":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            print("Aviso: Não foi possível configurar o DPI awareness.")
    except Exception as e:
        print(f"Aviso: Erro inesperado ao configurar DPI awareness: {e}")

# 🔒 Redireciona saída no modo .exe
if getattr(sys, 'frozen', False):
    sys.stdout = sys.stdout or open(os.devnull, 'w')
    sys.stderr = sys.stderr or open(os.devnull, 'w')

# 📁 Diretório de saída
DOCUMENTS_PATH = os.path.join(os.path.expanduser("~"), "Documents")
PASTA_SAIDA = os.path.join(DOCUMENTS_PATH, "Dados financeiros Extraídos")
os.makedirs(PASTA_SAIDA, exist_ok=True)

# 📄 Caminho do CSV com os tickers
base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
def carregar_tickers():
    """Lê o arquivo CSV 'Mapa Tickers B3.csv' e retorna uma lista e um mapa de tickers."""
    try:
        csv_path_options = [
            os.path.join(base_path, "Mapa", "Mapa Tickers B3.csv"),
            os.path.join(base_path, "Mapa Tickers B3.csv"),
            os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "Mapa", "Mapa Tickers B3.csv")
        ]
        df = None
        for path_option in csv_path_options:
            if os.path.exists(path_option):
                df = pd.read_csv(path_option, sep=";")
                break
        
        if df is None:
            messagebox.showerror("Erro Crítico", "Arquivo 'Mapa Tickers B3.csv' não encontrado.")
            sys.exit(1)
            
        lista = [f"{row['Ação']} - {row['Código']}.SA" for _, row in df.iterrows()]
        mapa = {f"{row['Ação']} - {row['Código']}.SA": f"{row['Código']}.SA" for _, row in df.iterrows()}
        return lista, mapa
    except Exception as e:
        messagebox.showerror("Erro ao Carregar Tickers", f"Não foi possível carregar o arquivo de tickers: {e}")
        sys.exit(1)

lista_tickers, mapa_tickers = carregar_tickers()

# 🎨 Interface principal
janela = tk.Tk()
janela.title("Extrator de Dados Financeiros")
janela.geometry("500x230")
janela.resizable(False, False)

style = ttk.Style(janela)
style.theme_use('clam') # Ou o tema que funcionou bem para você

cor_fundo_janela = 'white'
cinza_claro_fundo_widget = '#E0E0E0'
cinza_claro_fundo_ativo = '#C8C8C8'
cor_texto_principal = 'black'
cor_texto_desabilitado = '#A9A9A9'
cinza_claro_fundo_desabilitado = '#F0F0F0'

janela.configure(bg=cor_fundo_janela)
style.configure('TFrame', background=cor_fundo_janela)
style.configure('TLabel', background=cor_fundo_janela, foreground=cor_texto_principal)

fonte_label = ("Segoe UI", 9)
fonte_entry = ("Segoe UI", 9)
fonte_botao = ("Segoe UI", 10, "bold")
fonte_rodape = ("Segoe UI", 8, "italic")

style.configure("Icon.TButton", font=fonte_botao, padding=(8, 4), background=cinza_claro_fundo_widget, foreground=cor_texto_principal, borderwidth=1, relief='flat')
style.map("Icon.TButton", background=[('active', '!disabled', cinza_claro_fundo_ativo), ('pressed', '!disabled', cinza_claro_fundo_ativo)])
style.configure("Gray.TCombobox", fieldbackground=cinza_claro_fundo_widget, foreground=cor_texto_principal, borderwidth=1, relief='flat')
style.map("Gray.TCombobox", fieldbackground=[('readonly', '!focus', cinza_claro_fundo_widget), ('readonly', 'focus', cinza_claro_fundo_widget), ('disabled', cinza_claro_fundo_desabilitado)], foreground=[('disabled', cor_texto_desabilitado)], selectbackground=[('readonly', '#A0A0A0')], selectforeground=[('readonly', 'white')])
style.map("TEntry", fieldbackground=[('disabled', cinza_claro_fundo_desabilitado)], foreground=[('disabled', cor_texto_desabilitado)])
style.map("TCombobox", fieldbackground=[('disabled', cinza_claro_fundo_desabilitado)], foreground=[('disabled', cor_texto_desabilitado)], selectbackground=[('focus', '#0078D7'), ('!focus', '#D0E8FF')], selectforeground=[('focus', 'white'), ('!focus', 'black')])

content_frame = ttk.Frame(janela, padding="5 5 5 5", style='TFrame')
content_frame.pack(expand=True, fill=tk.BOTH)
form_frame = ttk.Frame(content_frame, style='TFrame')
form_frame.pack(pady=3, padx=3, fill=tk.X)
form_frame.columnconfigure(1, weight=1)
form_frame.columnconfigure(3, weight=1)

def autocompletar(event):
    texto_digitado = combo_ticker.get().lower()
    if not texto_digitado:
        combo_ticker['values'] = lista_tickers
        return
    sugestoes = [item for item in lista_tickers if texto_digitado in item.lower()]
    combo_ticker['values'] = sugestoes

# 🪵 --- INÍCIO DA LÓGICA DE BUSCA 'ANTIGA' ADAPTADA --- 🪵
def buscar():
    empresa = combo_ticker.get().strip()
    if empresa not in mapa_tickers:
        messagebox.showerror("Erro", "Selecione um ticker válido.")
        return

    ticker = mapa_tickers[empresa]
    
    # Obter datas do DateEntry
    inicio_date_obj = entry_inicio.get_date() # Retorna datetime.date
    fim_date_obj = entry_fim.get_date()     # Retorna datetime.date

    if not inicio_date_obj or not fim_date_obj:
        messagebox.showwarning("Campos obrigatórios", "Preencha as datas.") # Mensagem do código antigo
        return

    # Criar strings "DD-MM-YYYY" como no input antigo
    inicio_raw = inicio_date_obj.strftime("%d-%m-%Y")
    fim_raw = fim_date_obj.strftime("%d-%m-%Y")

    # Converter para datetime.datetime para lógica de validação e yfinance
    # (Similar ao que strptime fazia no código antigo)
    inicio_dt = datetime.combine(inicio_date_obj, datetime.min.time())
    fim_dt = datetime.combine(fim_date_obj, datetime.min.time())
    
    intervalo, formato = var_intervalo.get(), var_formato.get()

    try:
        # Validações de data do código antigo
        if inicio_dt > fim_dt:
            messagebox.showerror("Erro de Data", "Data inicial maior que final.")
            return 
        if max(inicio_dt, fim_dt) > datetime.today(): # Lógica antiga para data futura
            messagebox.showerror("Erro de Data", "Datas não podem estar no futuro.")
            return

        # Chamada yf.download como no código antigo (sem progress=False)
        df = yf.download(ticker, start=inicio_dt.strftime("%Y-%m-%d"), end=fim_dt.strftime("%Y-%m-%d"), interval=intervalo)

        # Processamento do DataFrame como no código antigo
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.reset_index(inplace=True) # Assume que cria coluna 'Date' com datetime objects

        # Lógica de seleção de colunas do código antigo
        # A seleção só ocorria se "Adj Close" estivesse presente
        if "Adj Close" in df.columns:
            # O código antigo faria a seleção direta. Se uma coluna faltasse, daria erro.
            # Para replicar fielmente:
            try:
                df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
            except KeyError as e:
                messagebox.showwarning("Aviso de Coluna", f"Não foi possível selecionar todas as colunas padrão (Date, Open, High, Low, Close, Volume) após encontrar 'Adj Close'. Coluna ausente: {e}. Os dados serão salvos com as colunas disponíveis.")
                # Neste caso, df continua como estava antes da tentativa de seleção, mas após o reset_index e remoção do MultiIndex
        # Se "Adj Close" não estiver nas colunas, o df antigo prosseguia sem essa seleção específica de colunas.

        if df.empty:
            messagebox.showwarning("Aviso", "Nenhum dado encontrado.") # Mensagem do código antigo
            return

        extensao = "xlsx" if formato == "XLSX" else "csv"
        # Nome do arquivo como no código antigo
        nome_arquivo = f"{ticker} {inicio_raw} {fim_raw} {intervalo}.{extensao}".replace(":", "-")
        caminho = os.path.join(PASTA_SAIDA, nome_arquivo)

        if formato == "XLSX":
            df.to_excel(caminho, index=False)
        else: # CSV
            # O código antigo não especificava sep=';' ou decimal='.' para to_csv
            # Mantendo o padrão do pandas to_csv ou ajustando se necessário:
            df.to_csv(caminho, index=False, sep=';', decimal='.') # Usando o formato CSV mais comum no Brasil, como no código mais recente

        messagebox.showinfo("Sucesso", f"Dados salvos em:\n{caminho}")

    except ValueError as ve: # Captura outros ValueErrors que não sejam de strptime
        messagebox.showerror("Erro de Valor", f"Ocorreu um erro de valor: {str(ve)}")
    except Exception as e: # Tratamento de erro do código antigo (adaptado)
        if "Failed to establish a new connection" in str(e) or "No connection adapters were found" in str(e):
            messagebox.showerror("Erro de conexão", "Verifique sua conexão com a internet ou se o ticker é válido.") # Mensagem mais completa
        # Adicionando a checagem de "No data found" que era útil na versão mais recente, mas adaptando a mensagem
        elif "No data found, symbol may be delisted" in str(e) or "No data found for this date range" in str(e):
             messagebox.showwarning("Aviso", f"Nenhum dado encontrado para {ticker} no período e intervalo especificados. Pode ter sido deslistado ou não há dados para o período.")
        else:
            messagebox.showerror("Erro", str(e)) # Mensagem genérica do código antigo
# 🪵 --- FIM DA LÓGICA DE BUSCA 'ANTIGA' ADAPTADA --- 🪵

def iniciar_busca_thread():
    botao_buscar.config(state=tk.DISABLED)
    thread = threading.Thread(target=buscar_e_reabilitar_botao)
    thread.daemon = True
    thread.start()

def buscar_e_reabilitar_botao():
    try:
        buscar()
    finally:
        janela.after(0, lambda: botao_buscar.config(state=tk.NORMAL))

def abrir_pasta(): # Mantendo a versão multiplataforma melhorada
    try:
        if sys.platform == "win32":
            os.startfile(PASTA_SAIDA)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", PASTA_SAIDA])
        else:
            subprocess.Popen(["xdg-open", PASTA_SAIDA])
    except Exception as e:
        messagebox.showerror("Erro ao Abrir Pasta", f"Não foi possível abrir a pasta: {e}")

# 📋 Campos do formulário (mantendo a estrutura atual com ttk e DateEntry)
pady_form_row = 5
padx_label_widget = 3
padx_widget_group = 8

ttk.Label(form_frame, text="Empresa:", font=fonte_label, style='TLabel').grid(row=0, column=0, sticky="e", padx=(0, padx_label_widget), pady=pady_form_row)
combo_ticker = ttk.Combobox(form_frame, values=lista_tickers, font=fonte_entry) # ttk.Combobox mantido
combo_ticker.grid(row=0, column=1, columnspan=3, sticky="ew", pady=pady_form_row)
combo_ticker.bind("<KeyRelease>", autocompletar)
if lista_tickers:
    combo_ticker.current(0)

ttk.Label(form_frame, text="Data de Início:", font=fonte_label, style='TLabel').grid(row=1, column=0, sticky="e", padx=(0, padx_label_widget), pady=pady_form_row)
entry_inicio = DateEntry(form_frame, font=fonte_entry, width=10, date_pattern='dd-mm-yyyy', locale='pt_BR', showweeknumbers=False, firstweekday='monday') # DateEntry mantido
entry_inicio.grid(row=1, column=1, sticky="ew", pady=pady_form_row)

ttk.Label(form_frame, text="Fim:", font=fonte_label, style='TLabel').grid(row=1, column=2, sticky="e", padx=(padx_widget_group, padx_label_widget), pady=pady_form_row)
entry_fim = DateEntry(form_frame, font=fonte_entry, width=10, date_pattern='dd-mm-yyyy', locale='pt_BR', showweeknumbers=False, firstweekday='monday') # DateEntry mantido
entry_fim.grid(row=1, column=3, sticky="ew", pady=pady_form_row)

ttk.Label(form_frame, text="Intervalo:", font=fonte_label, style='TLabel').grid(row=2, column=0, sticky="e", padx=(0, padx_label_widget), pady=pady_form_row)
var_intervalo = tk.StringVar(janela)
opcoes_intervalo = ["1d", "5d", "1wk", "1mo", "3mo"] # Opções do código mais recente, o antigo usava "1d", "1wk", "1mo"
var_intervalo.set(opcoes_intervalo[2]) # "1wk"
combo_intervalo = ttk.Combobox(form_frame, textvariable=var_intervalo, values=opcoes_intervalo, font=fonte_entry, state="readonly", width=9, style="Gray.TCombobox") # ttk.Combobox mantido
combo_intervalo.grid(row=2, column=1, sticky="ew", pady=pady_form_row)

ttk.Label(form_frame, text="Formato:", font=fonte_label, style='TLabel').grid(row=2, column=2, sticky="e", padx=(padx_widget_group, padx_label_widget), pady=pady_form_row)
var_formato = tk.StringVar(janela)
opcoes_formato = ["CSV", "XLSX"]
var_formato.set(opcoes_formato[0])
combo_formato = ttk.Combobox(form_frame, textvariable=var_formato, values=opcoes_formato, font=fonte_entry, state="readonly", width=9, style="Gray.TCombobox") # ttk.Combobox mantido
combo_formato.grid(row=2, column=3, sticky="ew", pady=pady_form_row)

button_area_frame = ttk.Frame(content_frame, style='TFrame')
button_area_frame.pack(pady=(10, 6))
button_frame_internal = ttk.Frame(button_area_frame, style='TFrame')
button_frame_internal.pack()

botao_buscar = ttk.Button(button_frame_internal, text="🔍 Buscar", command=iniciar_busca_thread, style="Icon.TButton") # Botão ttk mantido
botao_buscar.pack(side=tk.LEFT, padx=4)
botao_abrir = ttk.Button(button_frame_internal, text="📂 Abrir", command=abrir_pasta, style="Icon.TButton") # Botão ttk mantido
botao_abrir.pack(side=tk.LEFT, padx=4)

rodape_label = ttk.Label(content_frame, text="Powered by Victor Monteiro", font=fonte_rodape, foreground="gray", style='TLabel') # Rodapé ttk mantido
rodape_label.pack(pady=(6,2))

janela.mainloop()