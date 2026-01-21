from flask import Flask,render_template,request,redirect,session
import sqlite3,os
from datetime import datetime
app=Flask(__name__)
app.secret_key="pdv4"
def db():return sqlite3.connect("pdv.db")
if not os.path.exists("pdv.db"):
    conn=db();c=conn.cursor()
    with open("schema.sql","r") as f:c.executescript(f.read())
    conn.commit();conn.close()
@app.route("/")
def index():return redirect("/venda")
@app.route("/produtos",methods=["GET","POST"])
def produtos():
    conn=db();c=conn.cursor()
    if request.method=="POST":
        c.execute("insert into produto(codigo,descricao,preco) values(?,?,?)",(request.form["codigo"],request.form["descricao"],request.form["preco"].replace(",",".")))
        conn.commit();conn.close();return redirect("/produtos")
    produtos=c.execute("select * from produto").fetchall();conn.close()
    return render_template("produtos.html",produtos=produtos)
def calcular_total():
    return sum(i["sub_total"] for i in session["itens"])
@app.route("/venda",methods=["GET","POST"])
def venda():
    if "itens" not in session:session["itens"]=[]
    item_inexistente = False
    cod = False
    if request.method=="POST":
        conn=db();c=conn.cursor()
        codigo = request.form["codigo"]
        if "*" in codigo:
            qtd = float(codigo.split("*")[0])
            cod = codigo.split("*")[1]
        else:
            qtd = 1.0
            cod = codigo 
        p=c.execute("select id,descricao,preco from produto where codigo=?",(cod,)).fetchone();conn.close()
        if not p:
            item_inexistente = True
        else:
            preco = p[2]
            sub_total = qtd * preco
            session["itens"].append({"id":p[0],"desc":p[1],"preco":p[2],"qtd":qtd, "sub_total":sub_total});session.modified=True

    total = calcular_total()
    return render_template("venda.html",itens=session["itens"],total=total,item_inexistente=item_inexistente,cod=cod)
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
