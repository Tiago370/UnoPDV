from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
import re

venda_bp = Blueprint("venda", __name__)

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

@venda_bp.route("/venda",methods=["GET","POST"])
@venda_bp.route("/venda/",methods=["GET","POST"])
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
