from flask import Flask, json, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin

from config import config

app = Flask(__name__)
cors = CORS(app)
conexion = MySQL(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/api/productos', methods=['GET'])
@cross_origin()
def listar_productos():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * from producto"
        cursor.execute(sql)
        datos=cursor.fetchall()
        productos = []
        for fila in datos:
            producto = {'idproducto':fila[0], 'categoria':fila[1], 'nombre':fila[2], 'url_imagen':fila[3], 'descripcion':fila[4], 'stock':fila[5], 'precio':fila[6]}
            productos.append(producto)
        return jsonify({'productos':productos, 'mensaje':"Productos listados."})
    except Exception as ex:
        return jsonify({'mensaje':"Error"})

@app.route('/api/producto/<codigo>', methods=['GET'])
@cross_origin()
def leer_producto(codigo):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM producto WHERE idproducto = '{0}'".format(codigo)
        cursor.execute(sql)
        datos = cursor.fetchone()
        if datos != None:
            producto = {'idproducto':datos[0], 'categoria':datos[1], 'nombre':datos[2], 'url_imagen':datos[3], 'descripcion':datos[4], 'stock':datos[5], 'precio':datos[6]}
            return jsonify({'producto': producto, 'mensaje': "Producto encontrado."})
        else:
            return jsonify({'mensaje': "Producto no encontrado."})
    except Exception as ex:
        return json({'mensaje': "Error"})

@app.route('/api/categorias', methods=['GET'])
@cross_origin()
def listar_categorias():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * from categoria"
        cursor.execute(sql)
        datos=cursor.fetchall()
        categorias = []
        for fila in datos:
            categoria = {'idcategoria':fila[0], 'nombre':fila[1]}
            categorias.append(categoria)
        return jsonify({'categoria':categorias, 'mensaje':"Categorias listadas."})
    except Exception as ex:
        return jsonify({'mensaje':"Error"})

@app.route('/api/productos/<categoria>', methods=['GET'])
@cross_origin()
def listar_producto_por_categoria(categoria):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM producto WHERE categoria = '{0}'".format(categoria)
        cursor.execute(sql)
        datos = cursor.fetchall()
        productos = []
        if datos != None:
            for fila in datos:
                producto = {'idproducto':fila[0], 'categoria':fila[1], 'nombre':fila[2], 'url_imagen':fila[3], 'descripcion':fila[4], 'stock':fila[5], 'precio':fila[6]}
                productos.append(producto)
            return jsonify({'productos':productos, 'mensaje':"Productos listados."})
        else:
            return jsonify({'mensaje': "Producto no encontrado."})
    except Exception as ex:
        return json({'mensaje': "Error"})



@app.route('/api/reservar', methods=['PUT'])
@cross_origin()
def reservar():
    try:
       if request.json != {}:
            cursor = conexion.connection.cursor()
            for reserv in request.json['reservas']:
                sql = """SELECT stock - '{0}' AS nuevostock FROM producto WHERE idproducto = '{1}'""".format(reserv['cantidad'], reserv['idproducto'])
                cursor.execute(sql)
                datos = cursor.fetchone()
                if datos != None: 
                    stock = {'nuevostock':datos[0]}
                    nuevostock = int(stock['nuevostock'])
                    if nuevostock >= 0:
                        sql = """UPDATE producto SET stock = '{0}' WHERE idproducto = '{1}'""".format(nuevostock, reserv['idproducto'])
                        cursor.execute(sql)
                        conexion.connection.commit()
                    else:
                        return jsonify({'mensaje': "No hay stock suficiente."})
                else:
                    return jsonify({'mensaje': "Producto no encontrado."})            
            return jsonify({'mensaje': "Reserva realizada."})
       else:
           return jsonify({'mensaje': "No ha solicitado nada para reservar."})
    except Exception as ex:
        return json({'mensaje': "Error"})

@app.route('/api/verificar', methods=['POST'])
@cross_origin()
def verificar():
    try:
       if request.json != {}:
            cursor = conexion.connection.cursor()            
            sql = """SELECT stock - '{0}' AS nuevostock FROM producto WHERE idproducto = '{1}'""".format(request.json['cantidad'], request.json['idproducto'])
            cursor.execute(sql)
            datos = cursor.fetchone()
            if datos != None: 
                stock = {'nuevostock':datos[0]}
                nuevostock = int(stock['nuevostock'])
                if nuevostock >= 0:                                
                    return jsonify({'mensaje': "Stock Disponible."})
                else:
                    return jsonify({'mensaje': "No hay stock suficiente."})
            else:
                return jsonify({'mensaje': "Producto no encontrado."})
       else:
           return jsonify({'mensaje': "No ha solicitado nada para verificar."})
    except Exception as ex:
        return json({'mensaje': "Error"})

def pagina_no_encontrada(error):
        return "<h1>La página que intentas buscar no existe ... </h1>"

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(port="5000")