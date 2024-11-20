from flask import Flask, request, send_file, render_template
import fitz 
import os
import zipfile
from io import BytesIO

app = Flask(__name__)


UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf' not in request.files:
        print("No file uploaded.")
        return {"error": "No file uploaded"}, 400

    
    pdf_file = request.files['pdf']
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
    pdf_file.save(pdf_path)
    print(f"Uploaded file saved at: {pdf_path}")

    
    output_dir = os.path.join(UPLOAD_FOLDER, 'output_images')
    os.makedirs(output_dir, exist_ok=True)
    images = []
    try:
        with fitz.open(pdf_path) as doc:
            print(f"Number of pages in PDF: {len(doc)}")

            
            for page in doc:
                print(f"Processing page {page.number + 1}")
                pix = page.get_pixmap()
                image_path = os.path.join(output_dir, f"page{page.number + 1}.png")
                pix.save(image_path)
                print(f"Saved image: {image_path}")
                images.append(image_path)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for image in images:
                zip_file.write(image, os.path.basename(image))
                os.remove(image) 

        os.remove(pdf_path) 
        os.rmdir(output_dir)  

        zip_buffer.seek(0)
        print(f"Successfully created ZIP file with {len(images)} images.")
        return send_file(zip_buffer, mimetype='application/zip', download_name='images.zip')

    except Exception as e:
        print(f"Error during processing: {e}")
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
