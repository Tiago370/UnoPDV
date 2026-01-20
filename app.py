from flask import Flask,render_template,request,redirect,session
import sqlite3,os
from datetime import datetime
app=Flask(__name__)
app.secret_key="pdv"
def db():return sqlite3.connect("pdv.db")
if not os.path.exists("pdv.db"):
    conn=db();c=conn.cursor()
    c.execute("create table produto(id integer primary key,codigo text unique,descricao text,preco real)")
    c.execute("create table venda(id integer primary key,data text)")
    c.execute("create table item_venda(id integer primary key,venda_id integer,produto_id integer,quantidade real,preco_unit real)")
    conn.commit();conn.close()
@app.route("/")
def index():return redirect("/venda")
@app.route("/produtos",methods=["GET","POST"])
def produtos():
    conn=db();c=conn.cursor()
    if request.method=="POST":
        c.execute("insert into produto(codigo,descricao,preco) values(?,?,?)",(request.form["codigo"],request.form["descricao"],request.form["preco"]))
        conn.commit();conn.close();return redirect("/produtos")
    produtos=c.execute("select * from produto").fetchall();conn.close()
    return render_template("produtos.html",produtos=produtos)
@app.route("/venda",methods=["GET","POST"])
def venda():
    if "itens" not in session:session["itens"]=[]
    if request.method=="POST":
        conn=db();c=conn.cursor()
        p=c.execute("select id,descricao,preco from produto where codigo=?",(request.form["codigo"],)).fetchone();conn.close()
        if p:session["itens"].append({"id":p[0],"desc":p[1],"preco":p[2]});session.modified=True
    total=sum(i["preco"] for i in session["itens"])
    return render_template("venda.html",itens=session["itens"],total=total)
@app.route("/finalizar")
def finalizar():
    conn=db();c=conn.cursor()
    c.execute("insert into venda(data) values(?)",(datetime.now().isoformat(),));vid=c.lastrowid
    for i in session.get("itens",[]):c.execute("insert into item_venda(venda_id,produto_id,quantidade,preco_unit) values(?,?,?,?)",(vid,i["id"],1,i["preco"]))
    conn.commit();conn.close();session["itens"]=[]
    return redirect("/venda")
app.run(debug=True)
