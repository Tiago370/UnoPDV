import sqlite3,re
conn=sqlite3.connect("pdv.db")
c=conn.cursor()
with open("produtos.txt","r",encoding="latin-1") as f:
    dados=f.read()
for codigo,descricao,preco in re.findall(r'(\d+)\|([^|]+)\|([\d\.]+)',dados):
    try:c.execute("insert into produto(codigo,descricao,preco) values(?,?,?)",(codigo.strip(),descricao.strip(),float(preco)))
    except:pass
conn.commit()
conn.close()

