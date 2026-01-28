import re
from flask import Flask,render_template,request,redirect,session
import sqlite3,os
from datetime import datetime
from utils import db, init_db, calcular_total
from pack import pack_bp
from produto import produto_bp
from venda import venda_bp

app=Flask(__name__)
app.secret_key="pdv8"

init_db()

app.register_blueprint(pack_bp)
app.register_blueprint(produto_bp)
app.register_blueprint(venda_bp)

@app.route("/")
def index():return redirect("/venda")

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
