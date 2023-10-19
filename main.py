import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import os


def baixar(numero, session):
    # Remover pontos do número da fatura
    numero_sem_pontos = numero.replace('.', '')

    fatura_url = f"https://areadocliente.alfatransportes.com.br/fatura.php?fatura={numero_sem_pontos}"
    response = session.get(fatura_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar todos os links para download
    links = soup.select('a[href*="pdf.php?chv="]')

    for link in links:
        url = link['href']
        if url.startswith('https://areadocliente.alfatransportes.com.br/cte/pdf.php?chv='):
            nome_arquivo = os.path.join(f'fatura_{numero_sem_pontos}', url.split('=')[-1] + '.pdf')
            # Crie o diretório se não existir
            os.makedirs(os.path.dirname(nome_arquivo), exist_ok=True)
            response = session.get(url)
            with open(nome_arquivo, 'wb') as arquivo_pdf:
                arquivo_pdf.write(response.content)
                print(f'{nome_arquivo} baixado com sucesso.')

def mostrar_faturas_disponiveis(faturas, session):
    fatura_janela = tk.Toplevel(root)
    fatura_janela.title("Faturas Disponíveis")
    fatura_janela.geometry("400x600")

    canvas = tk.Canvas(fatura_janela)
    scrollbar = ttk.Scrollbar(fatura_janela, orient="vertical", command=canvas.yview)
    frame = ttk.Frame(canvas)

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    for fatura_info in faturas:
        ttk.Label(frame, text=f'Fatura: {fatura_info["Numero"]}').pack(pady=5)
        ttk.Label(frame, text=f'Data Emissão: {fatura_info["Emissao"]}').pack(pady=5)
        ttk.Label(frame, text=f'Data Vencimento: {fatura_info["Vencimento"]}').pack(pady=5)
        ttk.Label(frame, text=f'Valor: {fatura_info["Valor"]}').pack(pady=5)
        ttk.Label(frame, text=f'Nosso Número: {fatura_info["NossoNumero"]}').pack(pady=5)
        
        btn_baixar = ttk.Button(frame, text="Baixar", command=lambda num=fatura_info["Numero"].replace('.', ''): baixar(num, session))
        btn_baixar.pack(pady=5)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def fazer_login():
    # Obter os valores de login e senha dos campos de entrada
    login = entry_login.get()
    senha = entry_senha.get()
    login_url = "https://areadocliente.alfatransportes.com.br//login-sistema.php"

    login_data = {
        "login": login,
        "senha": senha
    }

    session = requests.Session()
    response = session.post(login_url, data=login_data)

    if response.status_code == 200:

        if "bem_vindo" in response.text.lower():
            try:
                faturas = []
                faturas_url = "https://areadocliente.alfatransportes.com.br/lista_faturas.php"
                faturas_page = session.get(faturas_url)
                soup = BeautifulSoup(faturas_page.content, 'html.parser')
                linhas_faturas = soup.find_all('tr', class_=['even', 'odd'])

                for linha in linhas_faturas:
                    colunas = linha.find_all('td')
                    numero_fatura = colunas[0].find('a').text
                    data_emissao = colunas[1].text.strip()
                    data_vencimento = colunas[2].text.strip()
                    valor = colunas[3].text.strip()
                    nosso_numero = colunas[4].text.strip()

                    faturas.append({
                        "Numero": numero_fatura,
                        "Emissao": data_emissao,
                        "Vencimento": data_vencimento,
                        "Valor": valor,
                        "NossoNumero": nosso_numero
                    })

                mostrar_faturas_disponiveis(faturas, session)
            
            except Exception as e:
                messagebox.showerror("Erro ao Obter Faturas", f"Ocorreu um erro ao obter as faturas: {e}")
        else:
            messagebox.showerror("Erro de Login", "Login ou senha inválidos.")
    else:
        messagebox.showerror("Erro de Conexão", "Não foi possível conectar ao servidor.")


root = tk.Tk()
root.title("Login")
root.geometry("400x400")

style = ttk.Style()

style.configure('TButton', font=('Arial', 14))
style.configure('TLabel', font=('Arial', 14), foreground='red')  

# Adicione um espaço vazio na parte superior para centralizar os elementos verticalmente
ttk.Label(root, text="").pack(pady=10)  

frame = ttk.Frame(root)
frame.pack(pady=10)

label_login = ttk.Label(frame, text="Login",justify="center")
label_login.grid(column=0, row=0, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
entry_login = ttk.Entry(frame)
entry_login.grid(column=0, row=1, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

label_senha = ttk.Label(frame, text="Senha")
label_senha.grid(column=0, row=2, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
entry_senha = ttk.Entry(frame, show="*")
entry_senha.grid(column=0, row=3, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

botao_login = ttk.Button(frame, text="Entrar", command=fazer_login)
botao_login.grid(column=0, row=4, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

# Adicione um espaço vazio na parte inferior para centralizar os elementos verticalmente
ttk.Label(root, text="").pack(pady=10)  
root.mainloop()