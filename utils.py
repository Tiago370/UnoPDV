import sqlite3,os
def db():return sqlite3.connect("pdv.db")

def init_db():
    if not os.path.exists("pdv.db"):
        conn=db();c=conn.cursor()
        with open("schema.sql","r") as f:c.executescript(f.read())
        conn.commit();conn.close()
