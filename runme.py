#!/usr/bin/env python3.4

from pathlib import Path

from richard import app
import coffeescript

def compile_coffee(coffee_path='scripts', output_path='static'):
	path = Path(coffee_path)
	out_path = Path(output_path)
	for file in path.iterdir():
		if file.suffix == ('.coffee'):
			out_file = Path(out_path, file.stem + '.js')
			with file.open() as coffeefile:
				js_text = coffeescript.compile(coffeefile.read())
			with out_file.open('w') as outfile:
				outfile.write(js_text)

if __name__ == '__main__':
	compile_coffee()
	app.run(debug=True, host='localhost', port=3000)