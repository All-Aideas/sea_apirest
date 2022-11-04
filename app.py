"""API REST SEA

This script allows the user to deploy API REST.
"""
import time
from datetime import datetime
import io
import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from connectdb import ConnectDB

print("Libraries imported.")

model_checkpoint = os.environ["MODEL_CHECKPOINT"]

tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)

model_save_name = os.environ["MODEL_SAVE_NAME"]

path = f"model/{model_save_name}"

model.load_state_dict(torch.load(path, map_location=torch.device("cpu")))
print("Model loaded.")

app = Flask(__name__)

api_cors_config = {"origins": "*", "methods": ["GET", "POST"], "allow_headers": "*"}

CORS(app, resources={r"/*": api_cors_config})

cnx = ConnectDB()
print("Database loaded.")


@app.route("/docs", methods=["GET"])
def docs():
    return "Predecir frase."


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    print(data)
    json_output = {}
    try:
        headers = request.headers
        if headers.get("X-Api-Key") is None:
            json_output_code = 401
            json_output = {
                "response": "Ud. no se encuentra autorizado para ejecutar esta operación.",
                "api_response": {"code": json_output_code, "message": "Unauthorized"},
            }
        else:
            auth = headers.get("X-Api-Key")
            if auth != os.environ["API_KEY_SEA"]:
                json_output_code = 401
                json_output = {
                    "response": "Token no válido.",
                    "api_response": {
                        "code": json_output_code,
                        "message": "Invalid Token",
                    },
                }
            else:
                if not data or "message" not in data:
                    json_output_code = 400
                    json_output = {
                        "response": "El campo 'message' es requerido.",
                        "api_response": {
                            "code": json_output_code,
                            "message": "Bad Request",
                        },
                    }
                else:
                    mensaje = data["message"]
                    print(f"Predecir frase: {mensaje}")

                    initial_time = time.time()  # get execution time

                    input_ids = tokenizer(mensaje, return_tensors="pt").input_ids
                    outputs = model.generate(input_ids, max_length=512)
                    outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True)[
                        0
                    ]

                    execution_time = float(f"{(time.time() - initial_time):.06f}")
                    print(f"Execution time: {execution_time:.06f} seconds")
                    remote_addr = request.remote_addr
                    user_agent = obtener_header(headers)
                    cnx.add_frase(
                        execution_time, remote_addr, user_agent, mensaje, outputs
                    )

                    json_output_code = 200
                    json_output = {
                        "response": outputs,
                        "api_response": {"code": json_output_code, "message": "OK"},
                    }
    except Exception as exception_error:
        print(exception_error)
        json_output_code = 500
        json_output = {
            "response": "Ha ocurrido un error.",
            "api_response": {
                "code": json_output_code,
                "message": "Internal Server Error",
            },
        }
    return jsonify(json_output), json_output_code


@app.route("/data", methods=["GET"])
def download_database():
    file_name_temp = cnx.get_predicciones()
    return_data = io.BytesIO()
    with open(file_name_temp, 'rb') as fo:
        return_data.write(fo.read())
    return_data.seek(0)

    os.remove(file_name_temp)
    now = datetime.now()
    attachment_filename = f'sea_predicciones_{now.strftime("%Y-%m-%d %H%M%S")}.xlsx'
    
    return send_file(
        return_data,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        attachment_filename=attachment_filename,
        as_attachment=True,
    )


@app.errorhandler(404)
def handler_404(exception_error):
    print(exception_error)
    json_output_code = 404
    return (
        jsonify(
            {
                "response": "Pagina no encontrada.",
                "api_response": {"code": json_output_code, "message": "Page not found"},
            }
        ),
        json_output_code,
    )


@app.errorhandler(405)
def handler_405(exception_error):
    print(exception_error)
    json_output_code = 405
    return (
        jsonify(
            {
                "response": "The method is not allowed for the requested URL.",
                "api_response": {
                    "code": json_output_code,
                    "message": "Method Not Allowed",
                },
            }
        ),
        json_output_code,
    )


def obtener_header(request_headers):
    user_agent = None
    if "User-Agent" in request_headers:
        user_agent = request_headers["User-Agent"]
    return user_agent


if __name__ == "__main__":
    app.run(host="0.0.0.0")
