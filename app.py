import re
from flask import Flask,render_template,request,redirect,session
import sqlite3,os
from datetime import datetime
app=Flask(__name__)
app.secret_key="pdv7"
def db():return sqlite3.connect("pdv.db")
if not os.path.exists("pdv.db"):
    conn=db();c=conn.cursor()
    with open("schema.sql","r") as f:c.executescript(f.read())
    conn.commit();conn.close()
@app.route("/")
def index():return redirect("/venda")

def buscar_produto_por_id(id):
    conn=db();cur=conn.cursor()
    cur.execute("SELECT id, codigo, descricao, preco FROM produto WHERE id = ?", (id,))
    produto = cur.fetchone()
    conn.close()
    return produto

@app.route("/produtos",methods=["GET","POST"])
def produtos():
    conn=db();c=conn.cursor()
    editar_id=request.args.get("editar_id")
    produto_edicao=None
    if editar_id:
        produto_edicao=buscar_produto_por_id(editar_id)
    filtros=[];valores=[]
    if request.method=="POST":
        acao=request.form["acao"]
        codigo=request.form["codigo"]
        descricao=request.form["descricao"]
        preco=request.form.get("preco")
        if acao=="consultar":
            if codigo:
                filtros.append("codigo LIKE ?");valores.append(f"%{codigo}%")
            if descricao:
                filtros.append("descricao LIKE ?");valores.append(f"%{descricao}%")
        elif acao=="salvar":
            c.execute("select id from produto where codigo=?",(codigo,))
            produto=c.fetchone()
            if produto:
                c.execute("update produto set descricao=?,preco=? where codigo=?",(descricao,preco,codigo))
            else:
                c.execute("insert into produto(codigo,descricao,preco) values(?,?,?)",(codigo,descricao,preco))
            conn.commit();conn.close();return redirect("/produtos")
    page=int(request.args.get("page",1));per_page=1000;offset=(page-1)*per_page
    where=" where "+" and ".join(filtros) if filtros else ""
    total=c.execute(f"select count(*) from produto{where}",valores).fetchone()[0]
    produtos=c.execute(f"select * from produto{where} limit ? offset ?",valores+[per_page,offset]).fetchall()
    conn.close()
    total_pages=(total+per_page-1)//per_page
    return render_template("produtos.html",produtos=produtos,page=page,total_pages=total_pages,produto_edicao=produto_edicao)


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
