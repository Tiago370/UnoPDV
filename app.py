import re
from flask import Flask,render_template,request,redirect,session,current_app
import sqlite3,os,csv
from datetime import datetime
from utils import db, init_db, calcular_total
from pack import pack_bp
from produto import produto_bp
from venda import venda_bp
from pagamento import pagamento_bp

app=Flask(__name__)
app.secret_key="pdv8"

init_db()

app.register_blueprint(pack_bp)
app.register_blueprint(produto_bp)
app.register_blueprint(venda_bp)
app.register_blueprint(pagamento_bp)

@app.route("/")
def index():return redirect("/venda")
@app.route("/configuracoes",methods=["GET","POST"])
@app.route("/configuracoes/",methods=["GET","POST"])
def configuracoes():
    if request.method=="POST":
        acao=request.form["acao"]
        if acao == "load-data-demo":
            acao=request.form["acao"]
            pasta_demo=os.path.join(current_app.root_path,"demo")
            conn=sqlite3.connect("pdv.db")
            conn.row_factory=sqlite3.Row
            cur=conn.cursor()
            arquivos = os.listdir(pasta_demo)
            if not arquivos:
                return render_template("configuracoes.html")
            for arquivo in arquivos:
                if arquivo.endswith(".csv"):
                    tabela=os.path.splitext(arquivo)[0]
                    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?",(tabela,))
                    if not cur.fetchone():
                        continue
                    cur.execute(f"PRAGMA table_info({tabela})")
                    colunas_tabela=[c["name"] for c in cur.fetchall()]
                    cur.execute(f"PRAGMA foreign_key_list({tabela})")
                    fks=cur.fetchall()
                    mapa_fk={fk["from"]:(fk["table"],fk["to"]) for fk in fks}
                    caminho_csv=os.path.join(pasta_demo,arquivo)
                    with open(caminho_csv,newline='',encoding="utf-8") as f:
                        reader=csv.DictReader(f)
                        dados_processados=[]
                        for linha in reader:
                            dados={}
                            for col,val in linha.items():
                                if ":" in col:
                                    campo_fk,campo_busca=col.split(":")
                                    if campo_fk in mapa_fk and val:
                                        tabela_fk,col_fk=mapa_fk[campo_fk]
                                        cur.execute(f"SELECT {col_fk} FROM {tabela_fk} WHERE {campo_busca}=?",(val,))
                                        ref=cur.fetchone()
                                        if ref:
                                            dados[campo_fk]=ref[col_fk]
                                else:
                                    if col in colunas_tabela:
                                        dados[col]=val
                            if dados:
                                dados_processados.append(dados)
                        for dados in dados_processados:
                            campos=",".join(dados.keys())
                            placeholders=",".join(["?"]*len(dados))
                            valores=list(dados.values())
                            cur.execute(f"INSERT INTO {tabela} ({campos}) VALUES ({placeholders})",valores)
            conn.commit()
            conn.close()
    return render_template("configuracoes.html")

app.run(debug=True)
