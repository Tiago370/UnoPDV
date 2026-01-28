from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
from datetime import datetime

pagamento_bp = Blueprint("pagamento", __name__)

@pagamento_bp.route("/pagamento")
def finalizar():
    conn=db();c=conn.cursor()
    c.execute("insert into venda(data) values(?)",(datetime.now().isoformat(),))
    vid=c.lastrowid
    for i in session.get("itens",[]):
        c.execute("insert into item_venda(venda_id,produto_id,quantidade,preco_unit) values(?,?,?,?)",(vid,i["id"],1,i["preco"]))
    conn.commit();conn.close();
    total = calcular_total()
    session["itens"]=[]
    return render_template("pagamento.html",total=total)
