import functools
from richard import app
from flask import redirect, url_for

def debug(func):
	@functools.wraps(func)
	def wrapped(*args, **kwargs):
		if app.debug:
			return func(*args, **kwargs)
		else:
			return redirect(url_for('home'))

	return wrapped