from flask import Blueprint, render_template, redirect, request
from utils import db

produto_bp = Blueprint("produto", __name__)

def buscar_produto_por_id(id):
    conn=db();cur=conn.cursor()
    cur.execute("SELECT id, codigo, descricao, preco FROM produto WHERE id = ?", (id,))
    produto = cur.fetchone()
    conn.close()
    return produto

@produto_bp.route("/produtos",methods=["GET","POST"])
@produto_bp.route("/produtos/",methods=["GET","POST"])
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

        elif acao=="deletar":
            c.execute("delete from produto where codigo=?", (codigo,))

            conn.commit();conn.close();return redirect("/produtos")
    page=int(request.args.get("page",1));per_page=1000;offset=(page-1)*per_page
    where=" where "+" and ".join(filtros) if filtros else ""
    total=c.execute(f"select count(*) from produto{where}",valores).fetchone()[0]
    produtos=c.execute(f"select * from produto{where} limit ? offset ?",valores+[per_page,offset]).fetchall()
    conn.close()
    total_pages=(total+per_page-1)//per_page
    return render_template("produtos.html",produtos=produtos,page=page,total_pages=total_pages,produto_edicao=produto_edicao)
