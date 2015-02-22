#!/usr/bin/env python3.4

from pathlib import Path

from richard import app, load_app
import coffeescript
import sys

def compile_coffee(coffee_path='scripts',
				 output_path='static'):
	path = Path(app.root_path, coffee_path)
	out_path = Path(app.root_path, output_path)
	for file in path.iterdir():
		if file.suffix == ('.coffee'):
			out_file = Path(out_path, file.stem + '.js')
			with file.open() as coffeefile:
				js_text = coffeescript.compile(coffeefile.read())
			with out_file.open('w') as outfile:
				outfile.write(js_text)

def run_production(host, port):
	app.config.from_object('config')
	compile_coffee()

	load_app()
	# rework to use with an actual production server
	app.run(host=host, port=port)

def run_debug(host, port, compile_coffee=True):
	app.config.from_object('config')
	if compile_coffee:
		compile_coffee()
	app.config['USE_COFFEE_DIRECTLY'] = not compile_coffee

	load_app()
	app.run(debug=True, host=host, port=port)

def run():
	compile_coffee()
	if '-d' in sys.argv:
		run_debug('localhost', port=3000, compile_coffee=False)
	else:
		run_production('localhost', port=8000)

if __name__ == '__main__':
	run()