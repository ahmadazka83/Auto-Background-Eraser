from flask import Flask, render_template, request, jsonify, send_file
import requests
import os
import tempfile
import uuid
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('REMOVE_BG_API_KEY')
print(f"Loaded API Key: {api_key}")

app = Flask(__name__, static_folder='assets')

if not os.path.exists('hasil'):
    os.makedirs('hasil')

def remove_background(image_path, api_key):
    api_url = 'https://api.remove.bg/v1.0/removebg'
    response = requests.post(api_url, files={'image_file': 
    open(image_path, 'rb')}, data={'size': 'auto'}, headers={'X-Api-Key': api_key})
    if response.status_code == requests.codes.ok:
        result_filename = f'hasil/result_{uuid.uuid4().hex}.png'
        with open(result_filename, 'wb') as out:
            out.write(response.content)
        return result_filename
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                file.save(temp_file.name)
                result_filename = remove_background(temp_file.name, api_key)
            
            if result_filename:
                return jsonify({'result': result_filename})
            else:
                return jsonify({'error': 'Background removal failed'})
        except Exception as e:
            return jsonify({'error': str(e)})

@app.route('/result/<filename>')
def result_image(filename):
    return send_file(os.path.join('hasil', filename), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
