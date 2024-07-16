from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import locale

# Configurar a localidade para o formato brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_db_connection():
  conn = sqlite3.connect('cadastros.db')
  conn.row_factory = sqlite3.Row
  return conn

@app.route('/')
def index():
  conn = get_db_connection()
  devedores = conn.execute('SELECT * FROM devedores').fetchall()
  cartoes = conn.execute('SELECT * FROM cartoes').fetchall()
  despesas = conn.execute('''
      SELECT despesas.*, devedores.nome as devedor_nome, cartoes.nome as cartao_nome
      FROM despesas
      JOIN devedores ON despesas.devedor_id = devedores.id
      JOIN cartoes ON despesas.cartao_id = cartoes.id
  ''').fetchall()
  conn.close()
  return render_template('index.html', devedores=devedores, cartoes=cartoes, despesas=despesas)

@app.route('/cadastro_devedor', methods=['POST'])
def cadastro_devedor():
  if request.method == 'POST':
      nome = request.form['nome']
      conn = get_db_connection()
      conn.execute('INSERT INTO devedores (nome) VALUES (?)', (nome,))
      conn.commit()
      conn.close()
      flash('Devedor cadastrado com sucesso!')
  return redirect(url_for('index'))

@app.route('/cadastro_cartao', methods=['POST'])
def cadastro_cartao():
  if request.method == 'POST':
      nome = request.form['nome']
      conn = get_db_connection()
      conn.execute('INSERT INTO cartoes (nome) VALUES (?)', (nome,))
      conn.commit()
      conn.close()
      flash('Cartão cadastrado com sucesso!')
  return redirect(url_for('index'))

@app.route('/cadastro_despesa', methods=['POST'])
def cadastro_despesa():
  if request.method == 'POST':
      devedor_id = request.form['devedor']
      cartao_id = request.form['cartao']
      local_compra = request.form['local_compra']
      valor_compra = request.form['valor_compra']
      data_compra = request.form['data_compra']
      tipo_pagamento = request.form['tipo_pagamento']
      parcelas = request.form['parcelas'] if tipo_pagamento == 'Parcelado' else 1

      # Formatar o valor da compra
      try:
          valor_compra = locale.atof(valor_compra)
      except ValueError:
          flash('Valor da compra inválido. Use o formato 100,00.')
          return redirect(url_for('index'))

      conn = get_db_connection()
      conn.execute('''
          INSERT INTO despesas (devedor_id, cartao_id, local_compra, valor_compra, data_compra, tipo_pagamento, parcelas) 
          VALUES (?, ?, ?, ?, ?, ?, ?)
      ''', (devedor_id, cartao_id, local_compra, valor_compra, data_compra, tipo_pagamento, parcelas))
      conn.commit()
      conn.close()
      flash('Despesa cadastrada com sucesso!')
  return redirect(url_for('index'))

@app.route('/listar_despesas')
def listar_despesas():
  devedor_id = request.args.get('devedor_id')
  conn = get_db_connection()
  if devedor_id:
      despesas = conn.execute('''
          SELECT despesas.*, devedores.nome as devedor_nome, cartoes.nome as cartao_nome
          FROM despesas
          JOIN devedores ON despesas.devedor_id = devedores.id
          JOIN cartoes ON despesas.cartao_id = cartoes.id
          WHERE devedor_id = ?
      ''', (devedor_id,)).fetchall()
  else:
      despesas = conn.execute('''
          SELECT despesas.*, devedores.nome as devedor_nome, cartoes.nome as cartao_nome
          FROM despesas
          JOIN devedores ON despesas.devedor_id = devedores.id
          JOIN cartoes ON despesas.cartao_id = cartoes.id
      ''').fetchall()
  devedores = conn.execute('SELECT * FROM devedores').fetchall()
  conn.close()
  return render_template('index.html', despesas=despesas, devedores=devedores)

@app.route('/excluir_despesa/<int:id>', methods=['POST'])
def excluir_despesa(id):
  conn = get_db_connection()
  conn.execute('DELETE FROM despesas WHERE id = ?', (id,))
  conn.commit()
  conn.close()
  flash('Despesa excluída com sucesso!')
  return redirect(url_for('index'))

@app.route('/excluir_cartao/<int:id>', methods=['POST'])
def excluir_cartao(id):
  conn = get_db_connection()
  conn.execute('DELETE FROM cartoes WHERE id = ?', (id,))
  conn.commit()
  conn.close()
  flash('Cartão excluído com sucesso!')
  return redirect(url_for('index'))

@app.route('/excluir_devedor', methods=['POST'])
def excluir_devedor():
  if request.method == 'POST':
      devedor_id = request.form['devedor']
      conn = get_db_connection()
      conn.execute('DELETE FROM devedores WHERE id = ?', (devedor_id,))
      conn.commit()
      conn.close()
      flash('Devedor excluído com sucesso!')
  return redirect(url_for('index'))

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)