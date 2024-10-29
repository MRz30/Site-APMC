from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///seu_arquivo_banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    
    try:
        novo_usuario = Usuario(nome=nome, email=email, senha=senha)
        db.session.add(novo_usuario)
        db.session.commit()
        print(f"Usuário {nome} cadastrado com sucesso!")
        return jsonify({"message": "Usuário cadastrado com sucesso!"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao cadastrar usuário: {e}")
        return jsonify({"message": "Erro ao cadastrar usuário."}), 500

if __name__ == '__main__':
    db.create_all()  # Certifique-se de que a tabela seja criada ao iniciar o app
    app.run(debug=True)
