import flask
import os
import sys
sys.path.append('./src')
import run_service
from run_service import *

from flask import render_template, url_for, request, abort, redirect, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['COMPRESS_EXTENSIONS'] = ['.png']
app.config['DECOMPRESS_EXTENSIONS'] = ['.pkl']
app.config['UPLOAD_PATH'] = './input'
app.config['COMPRESSED_PATH'] = './compressed_file'
app.config['DECOMPRESSED_PATH'] = './static'
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def getData():
    print(request.files)
    if request.files['file'] != None and secure_filename(request.files['file'].filename) != '':
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        print(filename)
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['COMPRESS_EXTENSIONS'] and file_ext not in app.config['DECOMPRESS_EXTENSIONS']:
            abort(400)
        # CHOOSE FLAG ALGO AND SAVE FILE
        flag_alg = request.form.get('flagAlg')
        flag_alg = int(flag_alg)
        file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
        uploaded_file.save(file_path)
        # COMPRESS
        if file_ext in app.config['COMPRESS_EXTENSIONS']:
            path_compressed = run_service.compress(file_path,flag_alg)
            filename_compressed = path_compressed.split('/')[-1]
            print(filename_compressed)
            # return  render_template('index.html', compressed_path=path_file_compressed)
            return jsonify(filePath = url_for('uploadPkl', filename=filename_compressed))
        # DECOMPRESS
        elif file_ext in app.config['DECOMPRESS_EXTENSIONS']:
            path_decompressed, _ = run_service.decompress(file_path, flag_alg)
            print(path_decompressed)
            filename_decompressed = path_decompressed.split('/')[-1]
            return jsonify(filePath = url_for('static', filename=filename_decompressed))
    return redirect(url_for('index'))

@app.route('/compressed/<filename>')
def uploadPkl(filename):
    print(filename)
    return send_from_directory(app.config['COMPRESSED_PATH'], filename, as_attachment=True)

@app.route('/decompressed/<filename>')
def uploadPNG(filename):
    print(filename)
    return send_from_directory(app.config['DECOMPRESSED_PATH'], filename, as_attachment=True)
    
if __name__ == '__main__':
    app.run()