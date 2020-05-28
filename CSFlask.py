#pip install Flask
from flask import Flask, render_template, url_for, redirect, request
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['MAX_CONTENT_LENGTH'] = 150 * 1024 * 1024 #max file size 150mb
UPLOAD_FOLDER = os.getcwd() # TODO: CHANGE TO TEMPDIR
print(os.getcwd())
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'} #TODO: Change when initial tests are done

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('home.html')
from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about") #TODO: CHANGE TO "OUT OF ORDER" page and sign in case costs get too high that month
def about():
    return render_template('about.html', title='About')

if __name__ == "__main__": #only true is script is run directly
    app.run(debug=True) #changes are live with debug on