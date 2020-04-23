import os
from flask import Flask, request, Response,redirect, url_for
from automatic_config_tool import AutomaticConfigTool
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'user_config_uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'json','conf'}

APP_CONFIG_FILE = None #Here our initial config will be loaded

def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _process_config(filename):
    tool = AutomaticConfigTool()
    return "CONFIG FILLED WITH CORRECT PARAMS"

@app.route('/',methods=['get','post'])
def results():
    """
    This will accept a json/conf testbed file in post call
    Eg: curl --location --request POST 'localhost:5000' --form 'file=@/Users/rahulchugh/Documents/workspace/borathon2020/test.json'
    """
    res = Response()
    res.content_type = 'application/json'
    res.status_code = 200
    res.data = 'SUCCESS'
    
    # If GET, communicate 'ALIVE' status
    if request.method == 'GET':
        res.data = 'ALIVE'
        app.logger.info("ALIVE")
        return res

    if request.method == 'POST':
        if 'file' not in request.files:
            res.data = 'FILE NOT FOUND'
            res.status_code = 500
            return res
        file = request.files['file']
        if file.filename == '':
            res.data= 'NO FILE SELECTED'
            res.status_code = 500
            return res
        if file and _allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_config = _process_config(filename)
            res.data = new_config
            res.status_code = 200
            return res
            
        




if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)