from flask import Flask, render_template, request, redirect, url_for, session
import os
import time
import threading
from utils import retrieve

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def background_process(question):
    data_path = os.path.join(app.config['UPLOAD_FOLDER'],"data.pdf")
    #perform RAG retrieval
    output_text = retrieve(question, data_path)

    return output_text


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'],"data.pdf")
            file.save(file_path)
            question = request.form.get('question')
            session['question'] = question
            # Start background process
            threading.Thread(target=background_process, args=(question,)).start()
            return redirect(url_for('ask_question'))
    return render_template('index.html')

@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    question = session.get('question', '')  # Retrieve question from session
    if request.method == 'POST':
        question = request.form.get('question')  # Retrieve question from form data
        output_text = background_process(question)
        return render_template('ask.html', question=question, output_text=output_text)
    return render_template('ask.html', question=question)

if __name__ == '__main__':
    app.run(debug=True)
