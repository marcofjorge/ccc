from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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

# Criar tabelas se não existirem
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

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/cadastro_devedor', methods=('GET', 'POST'))
def cadastro_devedor():
  if request.method == 'POST':
      nome = request.form['nome']
      if not nome:
          flash('O nome do devedor não pode estar vazio.')
      else:
          conn = get_db_connection()
          cursor = conn.cursor()
          cursor.execute('SELECT * FROM devedores WHERE nome = ?', (nome,))
          if cursor.fetchone():
              flash(f"Devedor {nome} já existe!")
          else:
              cursor.execute('INSERT INTO devedores (nome) VALUES (?)', (nome,))
              conn.commit()
              flash(f"Devedor {nome} cadastrado com sucesso!")
          conn.close()
      return redirect(url_for('cadastro_devedor'))
  return render_template('cadastro_devedor.html')

@app.route('/cadastro_cartao', methods=('GET', 'POST'))
def cadastro_cartao():
  if request.method == 'POST':
      nome = request.form['nome']
      if not nome:
          flash('O nome do cartão não pode estar vazio.')
      else:
          conn = get_db_connection()
          cursor = conn.cursor()
          cursor.execute('SELECT * FROM cartoes WHERE nome = ?', (nome,))
          if cursor.fetchone():
              flash(f"Cartão {nome} já existe!")
          else:
              cursor.execute('INSERT INTO cartoes (nome) VALUES (?)', (nome,))
              conn.commit()
              flash(f"Cartão {nome} cadastrado com sucesso!")
          conn.close()
      return redirect(url_for('cadastro_cartao'))
  return render_template('cadastro_cartao.html')

@app.route('/cadastro_despesa', methods=('GET', 'POST'))
def cadastro_despesa():
  conn = get_db_connection()
  cursor = conn.cursor()
  devedores = cursor.execute('SELECT nome FROM devedores').fetchall()
  cartoes = cursor.execute('SELECT nome FROM cartoes').fetchall()
  conn.close()

  if request.method == 'POST':
      devedor = request.form['devedor']
      cartao = request.form['cartao']
      local_compra = request.form['local_compra']
      valor_compra = request.form['valor_compra']
      data_compra = request.form['data_compra']
      tipo_pagamento = request.form['tipo_pagamento']
      parcelas = request.form['parcelas'] if tipo_pagamento == "Parcelado" else 1

      if not devedor or not cartao or not local_compra or not valor_compra or not data_compra:
          flash('Todos os campos devem ser preenchidos!')
      else:
          try:
              valor_compra = float(valor_compra)
          except ValueError:
              flash('Valor da compra deve ser um número.')
              return redirect(url_for('cadastro_despesa'))

          conn = get_db_connection()
          cursor = conn.cursor()
          cursor.execute('SELECT id FROM devedores WHERE nome = ?', (devedor,))
          devedor_id = cursor.fetchone()
          if not devedor_id:
              flash('Devedor não encontrado!')
              return redirect(url_for('cadastro_despesa'))

          cursor.execute('SELECT id FROM cartoes WHERE nome = ?', (cartao,))
          cartao_id = cursor.fetchone()
          if not cartao_id:
              flash('Cartão não encontrado!')
              return redirect(url_for('cadastro_despesa'))

          cursor.execute('''
              INSERT INTO despesas (devedor_id, cartao_id, local_compra, valor_compra, data_compra, tipo_pagamento, parcelas) 
              VALUES (?, ?, ?, ?, ?, ?, ?)
          ''', (devedor_id[0], cartao_id[0], local_compra, valor_compra, data_compra, tipo_pagamento, parcelas))
          conn.commit()
          conn.close()
          flash('Despesa cadastrada com sucesso!')
          return redirect(url_for('cadastro_despesa'))

  return render_template('cadastro_despesa.html', devedores=devedores, cartoes=cartoes)

@app.route('/listar_cartoes')
def listar_cartoes():
  conn = get_db_connection()
  cursor = conn.cursor()
  cartoes = cursor.execute('SELECT nome FROM cartoes').fetchall()
  conn.close()
  return render_template('listar_cartoes.html', cartoes=cartoes)

@app.route('/listar_despesas', methods=('GET', 'POST'))
def listar_despesas():
  conn = get_db_connection()
  cursor = conn.cursor()
  devedores = cursor.execute('SELECT nome FROM devedores').fetchall()
  conn.close()

  if request.method == 'POST':
      devedor = request.form['devedor']
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute('''
      SELECT id, local_compra, valor_compra, data_compra, tipo_pagamento, parcelas
      FROM despesas
      WHERE devedor_id = (
          SELECT id FROM devedores WHERE nome = ?
      )
      ORDER BY id
      ''', (devedor,))
      despesas = cursor.fetchall()
      conn.close()
      return render_template('listar_despesas.html', devedores=devedores, despesas=despesas, selected_devedor=devedor)

  return render_template('listar_despesas.html', devedores=devedores, despesas=[], selected_devedor=None)

@app.route('/excluir_devedor', methods=('GET', 'POST'))
def excluir_devedor():
  conn = get_db_connection()
  cursor = conn.cursor()
  devedores = cursor.execute('SELECT nome FROM devedores').fetchall()
  conn.close()

  if request.method == 'POST':
      devedor = request.form['devedor']
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute('DELETE FROM devedores WHERE nome = ?', (devedor,))
      conn.commit()
      conn.close()
      flash(f"Devedor '{devedor}' excluído com sucesso!")
      return redirect(url_for('excluir_devedor'))

  return render_template('excluir_devedor.html', devedores=devedores)

if __name__ == '__main__':
  app.run(debug=True)