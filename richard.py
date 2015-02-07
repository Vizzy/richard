from flask import (Flask, request, render_template,
					 jsonify, abort, json)
from lookup import CrossLookup
from collections import defaultdict

app = Flask('richard')
app.config.from_object('config')

caw = CrossLookup(apikey=app.config['DICT_APIKEY'], 
				  translate_key=app.config['TRNSL_APIKEY'])

with open('langs.json') as langsfile:
	lang_names = json.load(langsfile)

def get_lang():
	# make it actually work out the language
	return request.args.get('lang', 'en')

def humanise_lang_name(lang_code, interface_lang):
	for ln in lang_names:
		if lang_code == ln['iso_code']:
			return ln[interface_lang]


@app.context_processor
def inject_layout_defaults():
	return dict(app_name=app.name,
				author='anton osten')


@app.route('/')
def home():
	langs_from = sorted([(code, humanise_lang_name(code, get_lang())) 
						for code in caw.supported_directions.keys()],
						key=lambda x: x[1])
	return render_template('index.jinja2', langs_from=langs_from)

@app.route('/lookup/', methods=('POST',))
def lookup():
	queries = [q.strip().casefold() 
				for q in request.form['query'].split(',')]
	lang_from = request.form['lang_from']
	lang_to = request.form['lang_to']
	as_json = request.form.get('as_json')
	interface_lang = get_lang()

	result = caw.crossword_lookup(queries, lang_from, lang_to, 
									interface_lang)

	if as_json:
		# for some reason flask's jsonify dies on this
		return json.dumps(result[0], ensure_ascii=False)
	else:
		return abort(501)


@app.route('/get_lang_pairs/')
def get_lang_pairs():
	directions = caw.supported_directions
	lang = get_lang()
	lang_pairs = {key: {
						'name': humanise_lang_name(key, lang), 
						'targets': 
							sorted(
								value, 
								key=lambda code: humanise_lang_name(code, lang))
						}
					for key, value in 
					sorted(
						directions.items(), 
						key=lambda item: humanise_lang_name(item[0], lang))
					}
					

	return jsonify(lang_pairs)

@app.route('/get_lang_names/')
def get_lang_names():
	return jsonify(lang_names)
