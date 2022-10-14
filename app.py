import time
import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from flask import Flask, request, jsonify
from flask_cors import CORS
from connectdb import ConnectDB

print('Libraries imported.')

model_checkpoint = os.environ['MODEL_CHECKPOINT']

tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)

model_save_name = os.environ['MODEL_SAVE_NAME']

path = f"model/{model_save_name}" 

model.load_state_dict(torch.load(path, map_location=torch.device('cpu')))
print('Model loaded.')

app = Flask(__name__)

api_cors_config = {
    "origins": "*",
    "methods": ["GET","POST"],
    "allow_headers": "*"
}

CORS(app, resources={r"/*": api_cors_config})

cnx = ConnectDB()
print('Database loaded.')

@app.route("/docs", methods=['GET'])
def docs():
    return "Predecir frase."

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    print(data)
    json_output = dict()
    try:
        if not data or 'message' not in data:
            json_output_code = 400
            json_output = {'response': 'El campo \'message\' es requerido.',
                            'api_response': {'code': json_output_code, 'message': 'Bad Request'}
                        }
        else:
            mensaje = data['message']
            print("Predecir frase: %s" % (mensaje),)
            
            t = time.time() # get execution time

            input_ids = tokenizer(mensaje, return_tensors='pt').input_ids
            outputs = model.generate(input_ids, max_length=512)
            outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            
            dt = time.time() - t
            print("Execution time: %0.02f seconds" % (dt))
            cnx.add_frase(dt, mensaje, outputs)
            
            json_output_code = 200
            json_output = {'response': outputs,
                            'api_response': {'code': json_output_code, 'message': 'OK'}
                        }
    except:
        json_output_code = 500
        json_output = {'response': 'Ha ocurrido un error.',
                            'api_response': {'code': json_output_code, 'message': 'Internal Server Error'}
                        }
    return jsonify(json_output), json_output_code

@app.errorhandler(404)
def handler_404(e):
    json_output_code = 404
    return jsonify({'response': 'Pagina no encontrada.',
                    'api_response': {'code': json_output_code, 'message': 'Page not found'}}), json_output_code

@app.errorhandler(405)
def handler_405(e):
    json_output_code = 405
    return jsonify({'response': 'The method is not allowed for the requested URL.',
                    'api_response': {'code': json_output_code, 'message': 'Method Not Allowed'}}), json_output_code

if __name__ == '__main__':
    app.run(host="0.0.0.0")
