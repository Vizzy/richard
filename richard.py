from flask import (Flask, request, render_template,
					 jsonify, abort, json)
from contextdict import CrossLookup

app = Flask('richard')
app.config.from_object('config')

caw = CrossLookup(apikey=app.config['DICT_APIKEY'], 
				  translate_key=app.config['TRNSL_APIKEY'])


def get_lang():
	# make it actually work out the language
	return 'en'

@app.context_processor
def inject_layout_defaults():
	return dict(app_name=app.name,
				author='anton osten')



@app.route('/')
def home():
	langs_from = caw.supported_directions.keys()
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
	return jsonify(caw.supported_directions)


