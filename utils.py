import sqlite3,os
from flask import session

def db():return sqlite3.connect("pdv.db")

def init_db():
    caminho_base=os.path.dirname(os.path.abspath(__file__))
    caminho_schema=os.path.join(caminho_base,"schema.sql")
    caminho_db=os.path.join(caminho_base,"pdv.db")
    if not os.path.exists(caminho_db):
        conn=sqlite3.connect(caminho_db)
        c=conn.cursor()
        with open(caminho_schema,"r") as f:c.executescript(f.read())
        conn.commit()
        conn.close()


def calcular_total():
    return sum(i["sub_total"] for i in session["itens"])
