import sqlite3
from datetime import datetime

# Conectar ao banco de dados (ou criar se não existir)
def get_db_connection():
    conn = sqlite3.connect('cadastros.db')
    conn.row_factory = sqlite3.Row
    return conn

# Função para verificar a existência de uma coluna em uma tabela
def coluna_existe(nome_tabela, nome_coluna):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({nome_tabela})")
    colunas = [info[1] for info in cursor.fetchall()]
    conn.close()
    return nome_coluna in colunas

# Função para criar as tabelas se não existirem
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

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
    conn.close()

# Funções CRUD para devedores
def salvar_devedor(nome):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO devedores (nome) VALUES (?)', (nome,))
    conn.commit()
    conn.close()

def listar_devedores():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM devedores')
    devedores = cursor.fetchall()
    conn.close()
    return devedores

def excluir_devedor(nome):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM devedores WHERE nome = ?', (nome,))
    conn.commit()
    conn.close()

# Funções CRUD para cartoes
def salvar_cartao(nome):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO cartoes (nome) VALUES (?)', (nome,))
    conn.commit()
    conn.close()

def listar_cartoes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cartoes')
    cartoes = cursor.fetchall()
    conn.close()
    return cartoes

def excluir_cartao(nome):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cartoes WHERE nome = ?', (nome,))
    conn.commit()
    conn.close()

# Função para validar a data no formato dd-mm-aaaa
def validar_data(data_text):
    try:
        datetime.strptime(data_text, '%d-%m-%Y')
        return True
    except ValueError:
        return False

# Funções CRUD para despesas
def salvar_despesa(devedor_id, cartao_id, local_compra, valor_compra, data_compra, tipo_pagamento, parcelas):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO despesas (devedor_id, cartao_id, local_compra, valor_compra, data_compra, tipo_pagamento, parcelas) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (devedor_id, cartao_id, local_compra, valor_compra, data_compra, tipo_pagamento, parcelas))
    conn.commit()
    conn.close()

def listar_despesas(devedor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM despesas
    WHERE devedor_id = ?
    ''', (devedor_id,))
    despesas = cursor.fetchall()
    conn.close()
    return despesas

def excluir_despesa(id_despesa):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM despesas WHERE id = ?', (id_despesa,))
    conn.commit()
    conn.close()

create_tables()  # Criar as tabelas ao importar este módulo
