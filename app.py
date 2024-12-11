from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import pandas as pd

from preprocesamiento_sheets import GoogleDrive, GoogleSheet, InsertData
from coordenadas import ApiAddress
from precios import Precios
import os

clase_google_drive = GoogleDrive()
sheets = clase_google_drive.obtener_sheets()

precios = sheets["precios"]

clase_precios = Precios(precios)
producto_bebidas = clase_precios.obtener_precios("bebida")
producto_alimentos = clase_precios.obtener_precios("alimento")
producto_promociones = clase_precios.obtener_precios("promociones")


app = Flask(__name__)


app.secret_key = os.environ.get("SECRET_KEY")


def personalizaciones_bebidas(cantidad, nombre):
        list_ = []
        for i in range(cantidad):
            dicc = {
                'categoria': request.form.get(f"categoria_bebida_{i}"),
                'subcategoria': request.form.get(f"subcategoria_bebida_{i}"),
                'tipo_leche': request.form.get(f"tipo_leche_{i}"),
                'azucar': request.form.get(f"azucar_{i}"),
                'consideraciones': request.form.get(f"consideraciones_{i}")
            }
            list_.append(dicc)

        session[nombre] = list_

def personalizaciones(cantidad, nombre):
        list_ = []
        singular = nombre[:-1]
        if nombre == 'promociones':
            singular = nombre[:-2]
        for i in range(cantidad):
            dicc = {
                'categoria': request.form.get(f"categoria_{singular}_{i}"),
                'subcategoria': request.form.get(f"subcategoria_{singular}_{i}"),
                'consideraciones': request.form.get(f"consideraciones_{nombre}_{i}")
            }
            list_.append(dicc)

        session[nombre] = list_


@app.route("/<token>", methods=["GET", "POST"])
def registrar_pedido(token):
    session['token'] = token

    if request.method == "POST":
        nombre = request.form.get("nombre")
        cantidad_bebidas = int(request.form.get("cantidad_bebidas"))
        cantidad_alimentos = int(request.form.get("cantidad_alimentos"))
        cantidad_promociones = int(request.form.get("cantidad_promociones"))

        session['nombre'] = nombre

        personalizaciones_bebidas(cantidad_bebidas, "bebidas")
        personalizaciones(cantidad_alimentos, "alimentos")
        personalizaciones(cantidad_promociones, "promociones")
    


        return redirect(url_for("resumen_pedido", token=token))

    return render_template("home.html", token=token, categorias_bebidas=producto_bebidas, categorias_alimentos=producto_alimentos, categorias_promociones=producto_promociones)



@app.route("/resumen/<token>", methods=["GET", "POST"])
def resumen_pedido(token):

    dicc_personalizaciones = {'bebidas': session.get("bebidas", []),
                              'alimentos': session.get("alimentos", []),
                              'promociones': session.get("promociones", [])}


    if request.method == "POST":
        if 'confirmar_pedido' in request.form:
            # ---------------------------------------------------------
            # Guardar datos solo al confirmar el pedido
            sheet_personalizaciones = sheets["registro_personalizaciones"]
            clase_insert_data = InsertData(sheet_personalizaciones)
            registro_personalizaciones = GoogleSheet(sheet_personalizaciones)


            # dicc_personalizaciones = {'bebidas': session.get("bebidas", []),
            #                           'alimentos': session.get("alimentos", []),
            #                           'promociones': session.get("promociones", [])}
            
            nombre = session.get('nombre')
            total=0
            j=1
            registro_ventas = sheets["registro_ventas"]
            data = registro_ventas.get_all_records()
            data = pd.DataFrame(data)[["token_sesion", "status_confirmacion"]]
            data = data[data["token_sesion"] == token]
            status=1
            try:
                status = data['status_confirmacion'].iloc[0]
            except:
                status = 0

            if len(data) == 1 and status != 1:
                for productos, sesiones in dicc_personalizaciones.items():

                    cantidad_producto = len(sesiones)
                
                    for i in range(cantidad_producto):
                        dicc = sesiones[i]
                        print(dicc)
                        subcategoria = dicc["subcategoria"].split('-')[0]
                        precio = float(dicc["subcategoria"].split('-')[1].replace('MXN', '').strip())
                        print(f"Precio: {precio}")
                        new_token = token + '_' + str(j)

                        tipo_leche = 'No Aplica'
                        azucar_extra = "No Aplica"
                        if productos == "bebidas":
                            tipo_leche = dicc["tipo_leche"]
                            azucar_extra = dicc["azucar"]

                        dicc = {"nombre": nombre,
                                'producto': productos,
                                "categoria": dicc["categoria"],
                                "subcategoria": subcategoria,
                                "tipo_leche": tipo_leche,
                                "azucar_extra": azucar_extra,
                                "consideraciones": dicc["consideraciones"],
                                "precio": precio}

                        clase_insert_data.insert_data(new_token, j)
                        registro_personalizaciones.update_multiple_cells_by_id(new_token, dicc)

                        j += 1
                        total += precio

                latitud = session.get('latitud')
                longitud = session.get('longitud')
                clase_api_adress = ApiAddress()
                session["total"] = total

                direccion = clase_api_adress.api_request_object_1(latitud, longitud)
                _, radio, distancia = clase_api_adress.bola_cerrada(latitud, longitud)
                session["direccion"] = direccion

                
                dicc2 = {'nombre': nombre,
                        "cantidad_bebidas": len(dicc_personalizaciones["bebidas"]),
                        "cantidad_alimentos": len(dicc_personalizaciones["alimentos"]),
                        "cantidad_promociones": len(dicc_personalizaciones["promociones"]),
                        "direccion": direccion,
                        "cobertura": "DENTRO DEL RADIO",
                        "radio_km": radio,
                        "distancia": distancia,
                        "total": total}
                
                registro_ventas = GoogleSheet(sheets["registro_ventas"])
                registro_ventas.update_multiple_cells_by_id(token, dicc2)
                    
                session['pedido_confirmado'] = True
                return redirect(url_for("pedido_confirmado", token=token))
            else:
                session['pedido_confirmado'] = False
                return redirect(url_for("error"))

        elif 'reiniciar' in request.form:
            session.clear()  # Limpiar la sesión para reiniciar el formulario
            return redirect(url_for("registrar_pedido", token=token))

    latitud = session.get('latitud')
    longitud = session.get('longitud')

    clase_api_adress = ApiAddress()
    direccion = clase_api_adress.api_request_object_1(latitud, longitud)

    bebidas = dicc_personalizaciones["bebidas"]
    alimentos = dicc_personalizaciones["alimentos"]
    promociones = dicc_personalizaciones["promociones"]

    u = [bebidas, alimentos, promociones]
    u_new=[]
    for i in u:
        if len(i) > 0:
            u_new.append(i[0])


    nombre = session.get('nombre')


    total = sum([float(dicc["subcategoria"].split('-')[1].replace('MXN', '').strip())  for dicc in u_new])
    # except:
    #     total=0

    return render_template("resumen.html", nombre=nombre, direccion=direccion, bebidas=bebidas, alimentos=alimentos, promociones=promociones, total=total, token=token)



@app.route("/pedido_confirmado/<token>")
def pedido_confirmado(token):
    return "¡Gracias! Tu pedido ha sido confirmado exitosamente."

@app.route('/guardar_ubicacion', methods=['POST'])
def guardar_ubicacion():
    clase_api_adress = ApiAddress()

    data = request.json
    latitud = data.get("latitud")
    longitud = data.get("longitud")

    result, _, _ = clase_api_adress.bola_cerrada(latitud, longitud)

    if result == 1:
        session['latitud'] = latitud
        session['longitud'] = longitud
        return jsonify({"message": "Ubicación recibida correctamente"})
    else:
        return jsonify({"message": "Localmente NO tenemos cobertura hasta tu direccion, favor de pedir por Uber Eats, gracias!"})

# Nueva ruta para guardar el token y generar el enlace único
@app.route('/guardar_token', methods=['POST'])
def guardar_token():
    data = request.json
    token_sesion = data.get('token_sesion')

    enlace = f"https://e8d2-2806-2a0-1220-8638-25b9-50eb-73c6-6af6.ngrok-free.app/{token_sesion}"

    return jsonify({"enlace": enlace})


# Página de error si el token no es válido
@app.route('/error')
def error():
    return "Token inválido o ya ha sido usado."


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5056)

