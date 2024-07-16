import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# Conectar ao banco de dados (ou criar se não existir)
conn = sqlite3.connect('cadastros.db')
cursor = conn.cursor()


# Função para verificar a existência de uma coluna em uma tabela
def coluna_existe(nome_tabela, nome_coluna):
    cursor.execute(f"PRAGMA table_info({nome_tabela})")
    colunas = [info[1] for info in cursor.fetchall()]
    return nome_coluna in colunas


# Criar tabelas se não existirem
cursor.execute('''
CREATE TABLE IF NOT EXISTS devedores (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS cartoes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
)
''')

# Verificar se a tabela 'despesas' possui as colunas 'cartao_id' e 'valor_compra'
if not coluna_existe('despesas', 'cartao_id') or not coluna_existe('despesas', 'valor_compra'):
    cursor.execute('DROP TABLE IF EXISTS despesas')
    cursor.execute('''
    CREATE TABLE despesas (
        id INTEGER PRIMARY KEY,
        devedor_id INTEGER NOT NULL,
        cartao_id INTEGER NOT NULL,
        local_compra TEXT NOT NULL,
        valor_compra REAL NOT NULL,
        data_compra TEXT NOT NULL,
        tipo_pagamento TEXT NOT NULL,
        parcelas INTEGER,
        FOREIGN KEY(devedor_id) REFERENCES devedores(id),
        FOREIGN KEY(cartao_id) REFERENCES cartoes(id)
    )
    ''')
conn.commit()


# Função para salvar o nome do devedor
def salvar_devedor():
    nome = entry_nome_devedor.get()
    if nome:
        cursor.execute('SELECT * FROM devedores WHERE nome = ?', (nome,))
        if cursor.fetchone():
            messagebox.showwarning("Erro", f"Devedor {nome} já existe!")
        else:
            cursor.execute('INSERT INTO devedores (nome) VALUES (?)', (nome,))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Devedor {nome} cadastrado com sucesso!")
            janela_devedor.destroy()  # Fecha a janela após salvar
    else:
        messagebox.showwarning("Erro", "O nome do devedor não pode estar vazio.")


# Função para abrir a tela de cadastro de devedor
def cadastro_devedor():
    global janela_devedor, entry_nome_devedor
    janela_devedor = tk.Toplevel(root)
    janela_devedor.title("Cadastro de Devedor")
    janela_devedor.geometry("360x640")  # Tamanho típico de smartphone

    tk.Label(janela_devedor, text="Nome do Devedor:").pack(pady=20)
    entry_nome_devedor = tk.Entry(janela_devedor)
    entry_nome_devedor.pack(pady=10)

    btn_salvar = tk.Button(janela_devedor, text="Salvar", command=salvar_devedor)
    btn_salvar.pack(pady=20)


# Função para excluir um devedor
def excluir_devedor():
    def confirmar_exclusao():
        devedor_selecionado = combo_devedores.get()
        if devedor_selecionado:
            confirmar = messagebox.askyesno("Confirmar Exclusão",
                                            f"Deseja realmente excluir o devedor '{devedor_selecionado}'?")
            if confirmar:
                cursor.execute('DELETE FROM devedores WHERE nome = ?', (devedor_selecionado,))
                conn.commit()
                messagebox.showinfo("Sucesso", f"Devedor '{devedor_selecionado}' excluído com sucesso!")
                janela_confirmar_exclusao.destroy()
        else:
            messagebox.showwarning("Erro", "Selecione um devedor para excluir.")

    janela_confirmar_exclusao = tk.Toplevel(root)
    janela_confirmar_exclusao.title("Excluir Devedor")
    janela_confirmar_exclusao.geometry("300x150")

    tk.Label(janela_confirmar_exclusao, text="Selecione o devedor a ser excluído:").pack(pady=10)
    devedores = cursor.execute('SELECT nome FROM devedores').fetchall()
    devedores = [devedor[0] for devedor in devedores]
    combo_devedores = ttk.Combobox(janela_confirmar_exclusao, values=devedores)
    combo_devedores.pack(pady=10)

    btn_confirmar = tk.Button(janela_confirmar_exclusao, text="Confirmar Exclusão", command=confirmar_exclusao)
    btn_confirmar.pack(pady=10)


# Função para salvar o nome do cartão
def salvar_cartao():
    nome = entry_nome_cartao.get()
    if nome:
        cursor.execute('SELECT * FROM cartoes WHERE nome = ?', (nome,))
        if cursor.fetchone():
            messagebox.showwarning("Erro", f"Cartão {nome} já existe!")
        else:
            cursor.execute('INSERT INTO cartoes (nome) VALUES (?)', (nome,))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Cartão {nome} cadastrado com sucesso!")
            janela_cartao.destroy()  # Fecha a janela após salvar
    else:
        messagebox.showwarning("Erro", "O nome do cartão não pode estar vazio.")


# Função para abrir a tela de cadastro de cartões
def cadastro_cartoes():
    global janela_cartao, entry_nome_cartao
    janela_cartao = tk.Toplevel(root)
    janela_cartao.title("Cadastro de Cartão")
    janela_cartao.geometry("360x640")  # Tamanho típico de smartphone

    tk.Label(janela_cartao, text="Nome do Cartão:").pack(pady=20)
    entry_nome_cartao = tk.Entry(janela_cartao)
    entry_nome_cartao.pack(pady=10)

    btn_salvar = tk.Button(janela_cartao, text="Salvar", command=salvar_cartao)
    btn_salvar.pack(pady=20)


# Função para validar a data no formato dd-mm-aaaa
def validar_data(data_text):
    try:
        datetime.strptime(data_text, '%d-%m-%Y')
        return True
    except ValueError:
        return False


# Função para salvar a despesa
def salvar_despesa():
    devedor = combo_devedores.get()
    cartao = combo_cartoes.get()
    local_compra = entry_local_compra.get()
    valor_compra = entry_valor_compra.get()
    data_compra = entry_data_compra.get()
    tipo_pagamento = var_tipo_pagamento.get()
    parcelas = entry_parcelas.get() if tipo_pagamento == "Parcelado" else 1

    if not devedor or not cartao or not local_compra or not valor_compra or not data_compra:
        messagebox.showwarning("Erro", "Todos os campos devem ser preenchidos!")
        return

    if not validar_data(data_compra):
        messagebox.showwarning("Erro", "Data inválida! Use o formato DD-MM-AAAA.")
        return

    try:
        valor_compra = float(valor_compra)
    except ValueError:
        messagebox.showwarning("Erro", "Valor da compra deve ser um número.")
        return

    cursor.execute('SELECT id FROM devedores WHERE nome = ?', (devedor,))
    devedor_id = cursor.fetchone()
    if not devedor_id:
        messagebox.showwarning("Erro", "Devedor não encontrado!")
        return

    cursor.execute('SELECT id FROM cartoes WHERE nome = ?', (cartao,))
    cartao_id = cursor.fetchone()
    if not cartao_id:
        messagebox.showwarning("Erro", "Cartão não encontrado!")
        return

    cursor.execute('''
        INSERT INTO despesas (devedor_id, cartao_id, local_compra, valor_compra, data_compra, tipo_pagamento, parcelas) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (devedor_id[0], cartao_id[0], local_compra, valor_compra, data_compra, tipo_pagamento, parcelas))

    conn.commit()
    messagebox.showinfo("Sucesso", "Despesa cadastrada com sucesso!")
    janela_despesa.destroy()


# Função para mostrar ou esconder o campo de parcelas
def mostrar_parcelas():
    if var_tipo_pagamento.get() == "Parcelado":
        label_parcelas.pack(pady=10)
        entry_parcelas.pack(pady=10)
        btn_salvar.pack(pady=10)  # Reposicionar o botão de salvar
    else:
        label_parcelas.pack_forget()
        entry_parcelas.pack_forget()
        btn_salvar.pack(pady=20)  # Reposicionar o botão de salvar


# Função para abrir a tela de cadastro de despesas
def cadastro_despesas():
    global janela_despesa, combo_devedores, combo_cartoes, label_parcelas, entry_parcelas, btn_salvar

    janela_despesa = tk.Toplevel(root)
    janela_despesa.title("Cadastro de Despesas")
    janela_despesa.geometry("360x640")  # Tamanho típico de smartphone

    tk.Label(janela_despesa, text="Selecione o Devedor:").pack(pady=10)
    devedores = cursor.execute('SELECT nome FROM devedores').fetchall()
    devedores = [devedor[0] for devedor in devedores]
    combo_devedores = ttk.Combobox(janela_despesa, values=devedores)
    combo_devedores.pack(pady=10)

    tk.Label(janela_despesa, text="Selecione o Cartão:").pack(pady=10)
    cartoes = cursor.execute('SELECT nome FROM cartoes').fetchall()
    cartoes = [cartao[0] for cartao in cartoes]
    combo_cartoes = ttk.Combobox(janela_despesa, values=cartoes)
    combo_cartoes.pack(pady=10)

    tk.Label(janela_despesa, text="Local da Compra:").pack(pady=10)
    entry_local_compra = tk.Entry(janela_despesa)
    entry_local_compra.pack(pady=10)

    tk.Label(janela_despesa, text="Valor da Compra:").pack(pady=10)
    entry_valor_compra = tk.Entry(janela_despesa)
    entry_valor_compra.pack(pady=10)

    tk.Label(janela_despesa, text="Data da Compra (DD-MM-AAAA):").pack(pady=10)
    entry_data_compra = tk.Entry(janela_despesa)
    entry_data_compra.pack(pady=10)
    entry_data_compra.bind('<KeyRelease>', formatar_data)  # Formatar enquanto digita

    var_tipo_pagamento = tk.StringVar(value="À Vista")
    tk.Label(janela_despesa, text="Tipo de Pagamento:").pack(pady=10)
    tk.Radiobutton(janela_despesa, text="À Vista", variable=var_tipo_pagamento, value="À Vista",
                   command=mostrar_parcelas).pack()
    tk.Radiobutton(janela_despesa, text="Parcelado", variable=var_tipo_pagamento, value="Parcelado",
                   command=mostrar_parcelas).pack()

    label_parcelas = tk.Label(janela_despesa, text="Parcelas:")
    entry_parcelas = tk.Entry(janela_despesa)

    btn_salvar = tk.Button(janela_despesa, text="Salvar", command=salvar_despesa)
    mostrar_parcelas()  # Mostrar inicialmente os campos conforme o tipo de pagamento


# Função para listar os cartões cadastrados
def listar_cartoes():
    janela_listagem_cartoes = tk.Toplevel(root)
    janela_listagem_cartoes.title("Listagem de Cartões")
    janela_listagem_cartoes.geometry("360x640")  # Tamanho típico de smartphone

    scrollbar = tk.Scrollbar(janela_listagem_cartoes)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    lista_cartoes = tk.Listbox(janela_listagem_cartoes, yscrollcommand=scrollbar.set, width=80)
    lista_cartoes.pack(padx=10, pady=10)

    cursor.execute('SELECT nome FROM cartoes')
    cartoes = cursor.fetchall()

    for cartao in cartoes:
        lista_cartoes.insert(tk.END, cartao[0])

    scrollbar.config(command=lista_cartoes.yview)

    # Botão para excluir cartão selecionado
    def excluir_cartao():
        selecionado = lista_cartoes.curselection()
        if selecionado:
            cartao_selecionado = cartoes[selecionado[0]][0]
            confirmar = messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir o cartão '{cartao_selecionado}'?")
            if confirmar:
                cursor.execute('DELETE FROM cartoes WHERE nome = ?', (cartao_selecionado,))
                conn.commit()
                messagebox.showinfo("Sucesso", f"Cartão '{cartao_selecionado}' excluído com sucesso!")
                janela_listagem_cartoes.destroy()
        else:
            messagebox.showwarning("Erro", "Selecione um cartão para excluir.")

    btn_excluir = tk.Button(janela_listagem_cartoes, text="Excluir Cartão Selecionado", command=excluir_cartao)
    btn_excluir.pack(pady=10)


# Função para listar as despesas cadastradas de um devedor
def listar_despesas_devedor():
    devedor = combo_devedores_excluir.get()
    if devedor:
        janela_listagem = tk.Toplevel(root)
        janela_listagem.title(f"Despesas de {devedor}")
        janela_listagem.geometry("600x400")  # Tamanho da janela de listagem

        scrollbar = tk.Scrollbar(janela_listagem)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        lista_despesas = tk.Listbox(janela_listagem, yscrollcommand=scrollbar.set, width=80)
        lista_despesas.pack(padx=10, pady=10)

        cursor.execute('''
        SELECT id, local_compra, valor_compra, data_compra, tipo_pagamento, parcelas
        FROM despesas
        WHERE devedor_id = (
            SELECT id FROM devedores WHERE nome = ?
        )
        ORDER BY id
        ''', (devedor,))
        despesas = cursor.fetchall()

        for despesa in despesas:
            lista_despesas.insert(tk.END,
                                  f"ID: {despesa[0]} | Local: {despesa[1]} | Valor: R${despesa[2]:.2f} | Data: {despesa[3]} | Pagamento: {despesa[4]} | Parcelas: {despesa[5]}")

        scrollbar.config(command=lista_despesas.yview)

        # Botão para excluir despesa selecionada
        def excluir_despesa():
            selecionado = lista_despesas.curselection()
            if selecionado:
                id_despesa = despesas[selecionado[0]][0]
                confirmar = messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir esta despesa?")
                if confirmar:
                    cursor.execute('DELETE FROM despesas WHERE id = ?', (id_despesa,))
                    conn.commit()
                    messagebox.showinfo("Sucesso", "Despesa excluída com sucesso!")
                    janela_listagem.destroy()
                    listar_despesas_devedor()  # Atualiza a lista após a exclusão

        btn_excluir = tk.Button(janela_listagem, text="Excluir Despesa Selecionada", command=excluir_despesa)
        btn_excluir.pack(pady=10)

    else:
        messagebox.showwarning("Erro", "Selecione um devedor!")


# Função para abrir a tela de listagem de despesas por devedor
def listagem_despesas():
    global janela_listar_despesas, combo_devedores_excluir
    janela_listar_despesas = tk.Toplevel(root)
    janela_listar_despesas.title("Listagem de Despesas por Devedor")
    janela_listar_despesas.geometry("360x640")  # Tamanho típico de smartphone

    tk.Label(janela_listar_despesas, text="Selecione o Devedor:").pack(pady=10)
    devedores = cursor.execute('SELECT nome FROM devedores').fetchall()
    devedores = [devedor[0] for devedor in devedores]
    combo_devedores_excluir = ttk.Combobox(janela_listar_despesas, values=devedores)
    combo_devedores_excluir.pack(pady=10)

    btn_listar = tk.Button(janela_listar_despesas, text="Listar Despesas", command=listar_despesas_devedor)
    btn_listar.pack(pady=20)


# Função para mostrar os botões de cadastro
def mostrar_botoes_cadastro():
    btn_devedor.pack(pady=5)
    btn_cartoes.pack(pady=5)
    btn_despesas.pack(pady=5)
    btn_listar_despesas.pack(pady=5)
    btn_excluir_despesa.pack(pady=5)
    btn_excluir_devedor.pack(pady=5)  # Adicionando o botão de excluir devedor
    btn_listar_cartoes.pack(pady=5)  # Adicionando o botão de listar cartões


# Criar a janela principal
root = tk.Tk()
root.title("Cadastro")
root.geometry("360x640")  # Tamanho típico de smartphone

# Criar o botão principal de cadastro
btn_cadastro = tk.Button(root, text="Cadastro", command=mostrar_botoes_cadastro)
btn_cadastro.pack(pady=20)

# Criar os botões de cadastro, inicialmente escondidos
btn_devedor = tk.Button(root, text="Cadastro de Devedor", command=cadastro_devedor)
btn_cartoes = tk.Button(root, text="Cadastro de Cartões", command=cadastro_cartoes)
btn_despesas = tk.Button(root, text="Cadastrar Despesas", command=cadastro_despesas)
btn_listar_despesas = tk.Button(root, text="Listar Despesas por Devedor", command=listagem_despesas)
btn_excluir_despesa = tk.Button(root, text="Excluir Despesa de Devedor", command=listagem_despesas)
btn_excluir_devedor = tk.Button(root, text="Excluir Devedor", command=excluir_devedor)  # Botão para excluir devedor
btn_listar_cartoes = tk.Button(root, text="Listar Cartões", command=listar_cartoes)  # Botão para listar cartões

# Iniciar o loop principal da interface
root.mainloop()

# Fechar a conexão com o banco de dados ao fechar a aplicação
conn.close()
