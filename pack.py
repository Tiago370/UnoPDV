from flask import Blueprint, render_template, redirect, request
from utils import db

pack_bp = Blueprint("pack", __name__)

def buscar_pack_por_id(id):
    conn=db();
    cur=conn.cursor()
    cur.execute("SELECT id, codigo, nome_sg, nome_pl, mnemonico, quantidade FROM pack WHERE id = ?", (id,))
    pack = cur.fetchone()
    conn.close()
    return pack

@pack_bp.route("/packs",methods=["GET","POST"])
@pack_bp.route("/packs/",methods=["GET","POST"])
def packs():
    conn=db();c=conn.cursor()
    editar_id=request.args.get("editar_id")
    pack_edicao=None
    if editar_id:
        pack_edicao=buscar_pack_por_id(editar_id)
    filtros=[];valores=[]
    if request.method=="POST":
        acao=request.form["acao"]
        codigo=request.form["codigo"]
        nome_sg=request.form["nome_sg"]
        nome_pl=request.form["nome_pl"]
        mnemonico=request.form.get("mnemonico")
        quantidade=request.form.get("quantidade")
        id = request.form.get("id")
        if acao=="salvar":
            c.execute("select id from pack where id=?",(id,))
            pack=c.fetchone()
            if pack:
                c.execute("update pack set codigo=?,nome_sg=?,nome_pl=?,mnemonico=?,quantidade=? where id=?",(codigo,nome_sg,nome_pl,mnemonico,quantidade,id))
            else:
                c.execute("insert into pack(codigo,nome_sg,nome_pl,mnemonico,quantidade) values(?,?,?,?,?)",(codigo,nome_sg,nome_pl,mnemonico,quantidade))
            conn.commit();conn.close();return redirect("/packs")

        elif acao=="consultar":
            if codigo:
                filtros.append("codigo LIKE ?");
                valores.append(f"%{codigo}%")

            elif acao=="deletar":
                c.execute("delete from pack where id=?", (id,))
                conn.commit();conn.close();return redirect("/packs")

    where=" where "+" and ".join(filtros) if filtros else ""
    packs=c.execute(f"select * from pack{where}",valores).fetchall()
    conn.close()
    return render_template("packs.html",packs=packs,pack_edicao=pack_edicao)
