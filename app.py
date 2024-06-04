from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS  # Importe o módulo CORS

app = Flask(__name__)
CORS(app)


# Configure MySQL connection
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="school_facial_recognition"
    )
    if db.is_connected():
        print("Successfully connected to the database")
except Error as e:
    print(f"Error connecting to MySQL: {e}")
    db = None


@app.route('/')
def index():
    return "Hello, world!"



@app.route('/Insert', methods=['POST'])
def insert():
    if db is None or not db.is_connected():
        return jsonify({'error': 'MySQL connection is not initialized or lost'}), 500
    
    try:

        data = request.json

        if not isinstance(data, list) or len(data) != 1:
            return jsonify({'error': 'Dados inválidos. Esperava-se uma lista contendo um único objeto JSON'}), 400
           
  
        aluno = data[0]
        idtb_aluno = aluno.get('idtb_aluno')
        nome_aluno = aluno.get('nome_aluno')
        senha_aluno = aluno.get('senha_aluno')
        tb_professor_idtb_professor = aluno.get('tb_professor_idtb_professor')

        # Executa a inserção na tabela tb_aluno
        cursor = db.cursor()
        cursor.execute("INSERT INTO tb_aluno (idtb_aluno, tb_professor_idtb_professor, nome_aluno, senha_aluno) VALUES (%s, %s, %s, %s)", (idtb_aluno, tb_professor_idtb_professor, nome_aluno, senha_aluno))
        db.commit()
        cursor.close()

        return jsonify({'message': 'Aluno inserido com sucesso'}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500



@app.route('/Professores')
def read():
    if db is None or not db.is_connected():
        return "MySQL connection is not initialized or lost", 500
    
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM tb_professor')
        users = cursor.fetchall()
        cursor.close()
        return jsonify(users)
    except Error as e:
        return str(e), 500



@app.route('/login', methods=['POST'])
def login():
    if db is None or not db.is_connected():
        return "MySQL connection is not initialized or lost", 500

    if request.method == 'POST':
        data = request.json
        if 'id' not in data or 'senha' not in data:
            return jsonify({'error': 'ID and senha are required'}), 400

        user_id = data['id']
        senha = data['senha']

        try:
            cursor = db.cursor(dictionary=True)

            cursor.execute("SELECT * FROM tb_aluno WHERE idtb_aluno=%s AND senha_aluno=%s", (user_id, senha))
            aluno = cursor.fetchone()
            if aluno:
                nome = aluno['nome'] 
                cursor.close()
                return jsonify({'message': 'Login successful', 'user_type': 'aluno', 'nome': nome}), 200

            cursor.execute("SELECT * FROM tb_professor WHERE id=%s AND senha=%s", (user_id, senha))
            professor = cursor.fetchone()
            cursor.close()
            if professor:
                return jsonify({'message': 'Login successful', 'user_type': 'professor'}), 200

            return jsonify({'error': 'Invalid ID or senha'}), 401
        except Error as e:
            return str(e), 500
    else:
        return jsonify({'error': 'Method Not Allowed'}), 405

if __name__ == '__main__':
    app.run(debug=True)
