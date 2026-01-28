import re
from flask import Flask,render_template,request,redirect,session
import sqlite3,os
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

app.run(debug=True)
