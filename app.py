import re
from flask import Flask,render_template,request,redirect,session
import sqlite3,os
from datetime import datetime
from utils import db, init_db
from pack import pack_bp
from produto import produto_bp

app=Flask(__name__)
app.secret_key="pdv7"

init_db()

app.register_blueprint(pack_bp)
app.register_blueprint(produto_bp)

@app.route("/")
def index():return redirect("/venda")

def calcular_total():
    return sum(i["sub_total"] for i in session["itens"])

def valida_instrucao_codigo(s):
    return bool(re.match(r'^\d+([*x]\d+)*$', s))

def extrair_qtd_cod(codigo_str):
    if not valida_instrucao_codigo(codigo_str):
        return False, False
    codigo_str = codigo_str.replace("x", "*")
    partes = codigo_str.split("*")
    qtd = 1.0
    for p in partes[:-1]: qtd *= float(p)
    return qtd, partes[-1]

@app.route("/venda",methods=["GET","POST"])
def venda():
    message_type = False
    message_text = False
    if "itens" not in session:session["itens"]=[]
    cod = False
    if request.method=="POST":
        conn=db();c=conn.cursor()
        codigo = request.form["codigo"]
        if codigo:
            qtd, cod = extrair_qtd_cod(codigo)
            if qtd:
                p=c.execute("select id,descricao,preco from produto where codigo=?",(cod,)).fetchone();conn.close()
                if not p:
                    message_type = "danger"
                    message_text = "Produto não cadastrado: <strong>" + codigo + "</strong>"

                else:
                    preco = p[2]
                    sub_total = qtd * preco
                    session["itens"].append({"id":p[0],"desc":p[1],"preco":p[2],"qtd":qtd, "sub_total":sub_total});session.modified=True

            else:
                message_type = "danger"
                message_text = "Instrução inválida: <strong>" + codigo + "</strong>"
    total = calcular_total()
    return render_template("venda.html",itens=session["itens"],total=total,cod=cod,message_type=message_type,message_text=message_text)

@app.route("/finalizar")
def finalizar():
    conn=db();c=conn.cursor()
    c.execute("insert into venda(data) values(?)",(datetime.now().isoformat(),));vid=c.lastrowid
    for i in session.get("itens",[]):c.execute("insert into item_venda(venda_id,produto_id,quantidade,preco_unit) values(?,?,?,?)",(vid,i["id"],1,i["preco"]))
    conn.commit();conn.close();
    total = calcular_total()
    session["itens"]=[]
    return render_template("pagamento.html",total=total)

app.run(debug=True)
