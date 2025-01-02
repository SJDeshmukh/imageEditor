from flask import Flask, request, send_file
from PIL import Image
import io

app = Flask(__name__)

@app.route('/compress', methods=['POST'])
def compress_image():
    try:
        file = request.files['file']
        compression_level = int(request.form['compression_level'])

        # Process the image
        image = Image.open(file)
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=compression_level)
        output.seek(0)

        return send_file(output, mimetype='image/jpeg', as_attachment=True, download_name='compressed_image.jpg')
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
