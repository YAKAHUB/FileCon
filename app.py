from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from converters import detect_file_type, convert_file, CONVERSION_OPTIONS

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB limit
ALLOWED_EXTENSIONS = {'zip', 'rar', '7z', 'mp3', 'wav', 'ogg', 'pdf', 'docx', 'txt', 'epub', 'mobi',
                      'png', 'jpg', 'ico', 'heic', 'pptx', 'xlsx', 'mp4', 'avi', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            flash('Invalid file')
            return redirect(request.url)

        input_category, input_ext = detect_file_type(file)
        if input_category == 'other':
            flash('Unsupported file type')
            return redirect(request.url)

        output_ext = request.form.get('conversion_type')
        if not output_ext or output_ext not in CONVERSION_OPTIONS.get(input_category, {}).get(input_ext, []):
            flash('Invalid conversion type')
            return redirect(request.url)

        converted_file, output_filename = convert_file(file, input_category, input_ext, output_ext)
        if converted_file:
            return send_file(
                converted_file,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/octet-stream'
            )
        else:
            flash('Conversion failed')
            return redirect(request.url)

    # Precompute the accept string
    accept_string = ','.join(['.' + ext for ext in ALLOWED_EXTENSIONS])
    return render_template('index.html', conversion_options=CONVERSION_OPTIONS, accept_string=accept_string)

