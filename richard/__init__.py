import importlib
import pathlib

from flask import Flask, json
from richard.lookup import CrossLookup

app = Flask('richard')
app_path = pathlib.Path(app.root_path)

with pathlib.Path(app.root_path, 'langs.json').open() as langsfile:
	lang_names = json.load(langsfile)

def load_app():
	global caw
	caw = CrossLookup(apikey=app.config['DICT_APIKEY'], 
				  translate_key=app.config['TRNSL_APIKEY'])

	importlib.import_module(app.name + '.views')

	viewspath = pathlib.Path(app.root_path, 'views')
	for file in viewspath.iterdir():
		if file.suffix == '.py':
			importlib.import_module('.{}'.format(file.stem),
									package=app.name + '.views')
