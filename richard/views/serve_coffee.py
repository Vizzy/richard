import pathlib

from richard import app
import richard.helpers as helpers
from flask import send_file


@app.route('/coffee/<filename>')
@helpers.debug
def serve_coffee(filename=None):
	filepath = str(pathlib.Path(app.root_path, 'scripts', filename))
	print(filepath)
	return send_file(filepath)