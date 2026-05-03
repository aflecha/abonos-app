from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def conectar():
    return sqlite3.connect("datos.db")

def crear_tablas():
    con = conectar()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        abono REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        fecha TEXT,
        importe REAL,
        persona TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descripcion TEXT,
        fecha TEXT,
        importe REAL,
        persona TEXT
    )
    """)

    con.commit()
    con.close()

from datetime import datetime
@app.route("/", methods=["GET", "POST"])
def index():
    con = conectar()
    cur = con.cursor()

    mes = request.args.get("mes")

    filtro = ""
    params = ()

    if mes:
        filtro = "WHERE substr(fecha,1,7) = ?"
        params = (mes,)

    # ingresos
    cur.execute(f"""
        SELECT persona, SUM(importe)
        FROM pagos
        {filtro}
        GROUP BY persona
    """, params)

    ingresos = {row[0]: row[1] for row in cur.fetchall()}

    # gastos
    cur.execute(f"""
        SELECT persona, SUM(importe)
        FROM gastos
        {filtro}
        GROUP BY persona
    """, params)

    gastos = {row[0]: row[1] for row in cur.fetchall()}

    abel_ing = ingresos.get("Abel", 0)
    vale_ing = ingresos.get("Valeria", 0)

    abel_gas = gastos.get("Abel", 0)
    vale_gas = gastos.get("Valeria", 0)

    neto_abel = abel_ing - abel_gas
    neto_vale = vale_ing - vale_gas

    total = neto_abel + neto_vale
    mitad = total / 2 if total else 0

    balance = neto_abel - mitad

    if balance > 0:
        mensaje = f"Valeria debe transferir a Abel: ${round(balance,2)}"
    elif balance < 0:
        mensaje = f"Abel debe transferir a Valeria: ${round(abs(balance),2)}"
    else:
        mensaje = "Cuentas saldadas"

    con.close()

    return render_template("index.html",
        abel_ing=abel_ing,
        vale_ing=vale_ing,
        abel_gas=abel_gas,
        vale_gas=vale_gas,
        mensaje=mensaje,
        mes=mes
    )
    
@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        abono = request.form["abono"]
        cur.execute("INSERT INTO clientes (nombre, abono) VALUES (?, ?)", (nombre, abono))
        con.commit()

    cur.execute("SELECT * FROM clientes")
    clientes = cur.fetchall()

    con.close()
    return render_template("clientes.html", clientes=clientes)

@app.route("/cobros", methods=["GET", "POST"])
def pagos():
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        cliente_id = request.form["cliente_id"]
        importe = request.form["importe"]
        fecha = request.form["fecha"]
        persona = request.form["persona"]

        cur.execute("""
        INSERT INTO pagos (cliente_id, fecha, importe, persona)
        VALUES (?, ?, ?, ?)
        """, (cliente_id, fecha, importe, persona))
        con.commit()

    cur.execute("""
    SELECT pagos.id, clientes.nombre, pagos.fecha, pagos.importe, pagos.persona
    FROM pagos
    JOIN clientes ON clientes.id = pagos.cliente_id
    ORDER BY pagos.fecha DESC
    """)

    pagos = cur.fetchall()

    cur.execute("SELECT * FROM clientes")
    clientes = cur.fetchall()

    con.close()
    return render_template("cobros.html", pagos=pagos, clientes=clientes)

@app.route("/gastos", methods=["GET", "POST"])
def gastos():
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        descripcion = request.form["descripcion"]
        fecha = request.form["fecha"]
        importe = request.form["importe"]
        persona = request.form["persona"]

        cur.execute("""
        INSERT INTO gastos (descripcion, fecha, importe, persona)
        VALUES (?, ?, ?, ?)
        """, (descripcion, fecha, importe, persona))
        con.commit()

    cur.execute("SELECT * FROM gastos ORDER BY fecha DESC")
    gastos = cur.fetchall()

    con.close()
    return render_template("gastos.html", gastos=gastos)

@app.route("/eliminar_cliente/<int:id>")
def eliminar_cliente(id):
    con = conectar()
    cur = con.cursor()

    # borrar pagos asociados
    cur.execute("DELETE FROM pagos WHERE cliente_id = ?", (id,))
    
    # borrar cliente
    cur.execute("DELETE FROM clientes WHERE id = ?", (id,))

    con.commit()
    con.close()

    return redirect("/clientes")

@app.route("/informe")
def informe():
    con = conectar()
    cur = con.cursor()

    # pagos
    cur.execute("""
    SELECT fecha, clientes.nombre, importe, 'PAGO', persona
    FROM pagos
    JOIN clientes ON clientes.id = pagos.cliente_id
    """)

    pagos = cur.fetchall()

    # gastos
    cur.execute("""
    SELECT fecha, descripcion, importe, 'GASTO', persona
    FROM gastos
    """)

    gastos = cur.fetchall()

    datos = pagos + gastos

    # ordenar por fecha
    datos.sort(key=lambda x: x[0], reverse=True)

    con.close()

    return render_template("informe.html", datos=datos)

@app.route("/eliminar_pago/<int:id>")
def eliminar_pago(id):
    con = conectar()
    cur = con.cursor()

    cur.execute("DELETE FROM pagos WHERE id = ?", (id,))

    con.commit()
    con.close()

    return redirect("/cobros")

@app.route("/eliminar_gasto/<int:id>")
def eliminar_gasto(id):
    con = conectar()
    cur = con.cursor()

    cur.execute("DELETE FROM gastos WHERE id = ?", (id,))

    con.commit()
    con.close()

    return redirect("/gastos")    
    
import os

if __name__ == "__main__":
    crear_tablas()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)   
    
    