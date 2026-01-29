from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
import re

venda_bp = Blueprint("venda", __name__)

def valida_instrucao_codigo(s):
    return bool(re.match(r'^\d+([*x]\d+)*$', s))

def classificar_instrucao(instr):
    instr=instr.strip().lower()
    if not re.fullmatch(r'[a-z0-9]+(\*[a-z0-9]+)*',instr):
        return ('INVALID',{})
    partes=instr.split('*')
    codigo=partes[-1]
    fatores=partes[:-1]
    if not fatores:
        return ('UNIT',{'codigo':codigo})
    so_numeros=all(p.isdigit() for p in fatores)
    tem_letra=any(p.isalpha() for p in fatores)
    if len(fatores)==1 and so_numeros:
        return ('MULT',{'quantidade':int(fatores[0]),'codigo':codigo})
    if so_numeros:
        return ('CHAIN',{'fatores':[int(p) for p in fatores],'codigo':codigo})
    if tem_letra:
        return ('MNEM',{'fatores':fatores,'codigo':codigo})
    return ('INVALID',{})


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
    qtd = False
    if request.method=="POST":
        conn=db();c=conn.cursor()
        codigo = request.form["codigo"]
        if codigo:
            tipo, termos = classificar_instrucao(codigo)
            if tipo:
                if tipo == "INVALID":
                    message_type = "danger"
                    message_text = "Instrução inválida: <strong>" + codigo + "</strong>"
                elif tipo == "UNIT":
                    qtd = 1
                    cod = termos["codigo"]
                    message_type = "success"
                    message_text = "Item registrado individualmente: <strong>" + codigo + "<strong>"
                elif tipo == "MULT":
                    qtd = termos["quantidade"]
                    cod = termos["codigo"]
                    message_type = "info"
                    message_text = str(qtd) + " unidades do produto <strong>" + cod + "</strong>"
                elif tipo == "CHAIN":
                    qtd = 1
                    for n in termos["fatores"]:qtd*=n
                    cod = termos["codigo"]
                if qtd:
                    p=c.execute("select id,descricao,preco from produto where codigo=?",(cod,)).fetchone();conn.close()
                    if not p:
                        message_type = "danger"
                        message_text = "Produto não cadastrado: <strong>" + codigo + "</strong>"
                    else:
                        preco = p[2]
                        sub_total = qtd * preco
                        session["itens"].append({"id":p[0],"desc":p[1],"preco":p[2],"qtd":qtd, "sub_total":sub_total});session.modified=True

   
    total = calcular_total()
    return render_template("venda.html",itens=session["itens"],total=total,cod=cod,message_type=message_type,message_text=message_text)
