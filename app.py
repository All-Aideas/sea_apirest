import time
import os
import torch
from transformers import AutoTokenizer
from transformers import AutoModelForSeq2SeqLM
from flask import Flask, request, jsonify
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

cnx = ConnectDB()
print('Database loaded.')

@app.route("/")
def hello():
    return "Predecir frase."

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    print(data)
    json_output = dict()
    try:
        mensaje = data['message']
        print("Predecir frase: %s" % (mensaje),)
        
        if not mensaje:
            json_output = {'response': 'El campo message es requerido.',
                            'api_response': {'code': 400, 'message': 'Bad Request'}
                        }
        else:
            t = time.time() # get execution time

            input_ids = tokenizer(mensaje, return_tensors='pt').input_ids
            outputs = model.generate(input_ids, max_length=512)
            outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            
            dt = time.time() - t
            print("Execution time: %0.02f seconds" % (dt))
            cnx.add_frase(dt, mensaje, outputs)
            
            json_output = {'response': outputs,
                            'api_response': {'code': 200, 'message': 'OK'}
                        }
    except:
        json_output = {'response': 'Ha ocurrido un error.',
                            'api_response': {'code': 500, 'message': 'Internal Server Error'}
                        }
    return jsonify(json_output)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
