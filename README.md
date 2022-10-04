# SEA API REST
 API REST service to invoke Natural language processing (NLP) model text-to-text.

## Installation
### WINDOWS
#### Database variables
```sh
set DATABASE_USER=<USER_NAME>
set DATABASE_PASSWORD=<USER_PASSWORD>
set DATABASE_HOST=<DATABASE_HOSTNAME>
set DATABASE_NAME=<DATABASE_NAME>
```

#### Model variables
```sh
set MODEL_CHECKPOINT=<MODEL_CHCKPOINT_NAME>
set MODEL_SAVE_NAME=<MODEL_FILE_NAME>
```

### LINUX
#### Database variables
```sh
export DATABASE_USER=<USER_NAME>
export DATABASE_PASSWORD=<USER_PASSWORD>
export DATABASE_HOST=<DATABASE_HOSTNAME>
export DATABASE_NAME=<DATABASE_NAME>
```

#### Model variables
```sh
export MODEL_CHECKPOINT=<MODEL_CHCKPOINT_NAME>
export MODEL_SAVE_NAME=<MODEL_FILE_NAME>
```

## Run API
```sh
cd sea_apirest/
python3 app.py
```

## Development
### WINDOWS
```sh
python -m venv .\venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### LINUX
```sh
python3 -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt
```

## Testing from localhost
Example to invoke API REST.
```sh
curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d "{\"message\":\"Yo estoy jugando ajedrez.\"}"
```
