from flask import Flask
from db_init import db
from flask_migrate import Migrate

app = Flask(__name__)
@app.route('/')
def index():
  return render_template('index.html')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meubanco.db'  # Exemplo de configuração do banco de dados
db.init_app(app)
Migrate = Migrate(app, db)
if __name__ == '__main__':
    app.run()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vendas.db'
db.init_app(app)


@app.errorhandler(400)
def bad_request(error):
    return render_template('400.html'), 400

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            cliente = request.form["cliente"]
            produto_id = int(request.form["produto"])
            quantidade = int(request.form["quantidade"])
            pedido = Pedido(cliente=cliente, produto_id=produto_id, quantidade=quantidade)
            db.session.add(pedido)
            db.session.commit()
            return redirect(url_for('lista_pedidos'))
        except (KeyError, ValueError):
            abort(400)

    produtos = Produto.query.all()
    return render_template("index.html", produtos=produtos)

@app.route("/produtos")
def produtos():
    produtos = Produto.query.all()
    return render_template("produtos.html", produtos=produtos)

@app.route("/adicionar_produto", methods=["GET", "POST"])
def adicionar_produto():
    if request.method == "POST":
        try:
            nome = request.form["nome"]
            preco = float(request.form["preco"])
            produto = Produto(nome=nome, preco=preco)
            db.session.add(produto)
            db.session.commit()
            return redirect(url_for('produtos'))
        except (KeyError, ValueError):
            abort(400)
    return render_template("adicionar_produto.html")

@app.route("/lista_pedidos")
def lista_pedidos():
    pedidos = Pedido.query.all()
    total = sum(pedido.produto.preco * pedido.quantidade for pedido in pedidos)
    total_por_cliente = {}
    for pedido in pedidos:
        cliente = pedido.cliente
        if cliente not in total_por_cliente:
            total_por_cliente[cliente] = {
                "total": 0,
                "pago": True  # Inicialmente, consideramos que todos os pedidos estão pagos
            }
        total_por_cliente[cliente]["total"] += pedido.produto.preco * pedido.quantidade
        if not pedido.pago:
            total_por_cliente[cliente]["pago"] = False  # Se encontrar um pedido não pago, marca como False

    return render_template("lista_pedidos.html", pedidos=pedidos, total=total, total_por_cliente=total_por_cliente)

@app.route("/editar_produto/<int:id>", methods=["GET", "POST"])
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    if request.method == "POST":
        try:
            produto.nome = request.form["nome"]
            produto.preco = float(request.form["preco"])
            db.session.commit()
            return redirect(url_for('produtos'))
        except (KeyError, ValueError):
            abort(400)
    return render_template("editar_produto.html", produto=produto)

@app.route("/pagar/<int:id>")
def pagar(id):
    pedido = Pedido.query.get_or_404(id)
    pedido.pago = True
    db.session.commit()
    return redirect(url_for('lista_pedidos'))
 

@app.route("/apagar_todos")
def apagar_todos():
    Pedido.query.delete()
    db.session.commit()
    return redirect(url_for('lista_pedidos'))

@app.route("/imprimir/<cliente>")

def imprimir(cliente):
    pedidos = Pedido.query.filter_by(cliente=cliente).all()
    total_cliente = sum(pedido.produto.preco * pedido.quantidade for pedido in pedidos) # Calcula o total para o cliente
    return render_template("imprimir.html", cliente=cliente, pedidos=pedidos, total_cliente=total_cliente) # Passa o total_cliente para o template

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)