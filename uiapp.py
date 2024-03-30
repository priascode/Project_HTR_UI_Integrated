from flask import Flask, render_template, request, redirect, send_file, url_for
import subprocess
import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'data/page'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

COPY_FOLDER = 'static/uploads'
app.config['COPY_FOLDER'] = COPY_FOLDER

# Ensure the upload folder exists
os.makedirs(COPY_FOLDER, exist_ok=True)

# Define the static folder# Replace 'static_folder_name' with your desired folder name


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            copy_path = os.path.join(app.config['COPY_FOLDER'], filename)
            file.save(file_path)
            shutil.copy(file_path,copy_path)
            return redirect(url_for('gallery', filename=filename))
    return render_template('index.html')

@app.route('/gallery/<filename>')
def gallery(filename):
    return render_template('gallery.html', filename=filename)

@app.route('/digitalize', methods=['POST'])
def digitalize():
    # Get the filename from the form data
    filename = request.form['filename']
    
    # Run external Python script passing the filename as an argument
    subprocess.run(['python', 'app.py', filename])
    
    # Redirect back to the index page or any other page you want
    return render_template('outputgallery.html', filename=filename)

@app.route('/show_text/<filename>', methods=['POST'])
def show_text(filename):
  
    # Read the content of the text file
    with open('digitized_output.txt', 'r') as file:
        content = file.read()
    return render_template('Digitalizedcontent.html', content=content, filename=filename)

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    filename = 'digitized_output.txt'
    # content = request.form['content']
      # Create PDF file dynamically
    pdf_filename = filename.replace('.txt', '.pdf')
    pdf_file_path = f'static/pdf/{pdf_filename}'
  
    with open('digitized_output.txt', 'r') as file:
        lines = file.readlines()

    # Create PDF file dynamically using reportlab
    c = canvas.Canvas(pdf_file_path, pagesize=letter)
    y = 750  # Initial y-coordinate for text

    # Write each line to the PDF canvas
    for line in lines:
        c.drawString(100, y, line.strip())  # Adjust the position as needed
        y -= 12  # Move to the next line (adjust line spacing as needed)

    c.save()

    # Return PDF file for download
    return send_file(pdf_file_path, as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def back_to_home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
