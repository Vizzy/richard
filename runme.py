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

def run_production():
	...

def run_debug(host, port, compile_coffee=True):
	app.config.from_object('config')
	load_app()
	app.run(debug=True, host=host, port=port)

def run():
	compile_coffee()
	if '-d' in sys.argv:
		run_debug('localhost', port=3000, compile_coffee=False)


if __name__ == '__main__':
	run()