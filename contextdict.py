#!/usr/bin/env python3.4

import urllib.parse as urlparse
from itertools import filterfalse, chain
from collections import defaultdict
from multiprocessing.pool import Pool

import requests
import simplejson as json

class UnsupportedLanguageException(ValueError):
	pass

class CrossLookup:
	def __init__(self, apikey, translate_key=None):
		self._base_url = 'https://dictionary.yandex.net/api/v1/dicservice.json/'
		self.apikey = apikey
		self.translate_key = translate_key
		r = requests.get(urlparse.urljoin(self._base_url, 'getLangs'),
				params=dict(key=apikey))
		self.supported_langs = json.loads(r.text)

		self.supported_directions = defaultdict(list)
		for pair in self.supported_langs:
			split_pair = pair.split('-')
			self.supported_directions[split_pair[0]].append(split_pair[1])


	def lookup(self, query, lang_from, lang_to, interface_lang='en'):
		lang = lang_from + '-' + lang_to
		if lang not in self.supported_langs:
			raise UnsupportedLanguageException

		payload = {'key': self.apikey, 'lang': lang,
					'text': query, 'ui': interface_lang}
		r = requests.get(urlparse.urljoin(self._base_url, 'lookup'),
				params=payload)
		result = json.loads(r.text)
		return result

	def lookup_translate(self, query, lang_from, lang_to):
		lang = lang_from + '-' + lang_to
		#if lang not in self.supported_langs:
		#	raise UnsupportedLanguageException

		payload = {'key': self.translate_key, 'lang': lang,
					'text': query}
		r = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate',
				params=payload)
		result = json.loads(r.text)
		return result


	def crossword_lookup(self, synonyms, lang_from, lang_to, 
						interface_lang, pos=()):

		translations = []
		smarter_translations = []
		
		p = Pool()
		results = p.starmap(self.lookup,
						 ((s, lang_from, lang_to) for s in synonyms))
		translations_by_pos = chain.from_iterable((r['def'] for r in results))

		# filter by part of speech
		if list(iter(pos)) != []:
			translations_by_pos = filter(
										lambda x: x['pos'] in pos, 
										translations_by_pos)

		# filter by additional meanings

		for tps in translations_by_pos:
			for translation in tps['tr']:
				try:
					meanings = [m['text'] for m in translation['mean']]
					for s in synonyms:
						remaining_synonyms = synonyms[:]
						remaining_synonyms.remove(s)
						intersection = set(meanings).intersection(remaining_synonyms)
						# see if there are any intersections between synonyms and meanings
						if len(intersection) is not 0:
							smarter_translations.append(translation)
				except KeyError:
					# there are no meanings provided in the results
					pass
				finally:
					translations.append(translation)


		# check for overlaps between translations
		texts = [t['text'] for t in translations]
		synonyms = [syn['text'] for syn in
					 [t.get('synonyms') for t in translations]
					 if syn]

		words = texts + synonyms

		multiple_occurences = filter(lambda t: words.count(t['text']) > 1,
					 				translations + smarter_translations)

		smarter_translations += list(multiple_occurences)

		if len(smarter_translations) > 0:
			keys = []
			results = []
			for t in smarter_translations:
				if t['text'] not in keys:
					results.append(t)
					keys.append(t['text'])
		else:
			results = translations
		
		return results

	def cross_lang_lookup(self, queries, lang_to, pos=()):
		p = Pool()
		try:
			results = p.starmap(self.lookup,
						((q[0], q[1], lang_to) for q in queries))
			translations_by_pos = chain.from_iterable((r['def'] for r in results))
		except UnsupportedLanguageException:
			results = p.starmap(self.lookup_translate,
						((q[0], q[1], lang_to) for q in queries))
			translations_by_pos = chain.from_iterable(results)

		

		# filter by part of speech
		if list(iter(pos)) != []:
			translations_by_pos = filter(
										lambda x: x['pos'] in pos, 
										translations_by_pos)

		translations = []

		for tps in translations_by_pos:
			for translation in tps['tr']:
				translations.append(translation)

		# check for overlaps between translations
		texts = [t['text'] for t in translations]

		multiple_occurences = filter(lambda t: texts.count(t['text']) > 1,
					 				translations)

		keys = []
		results = []
		for t in multiple_occurences:
			if t['text'] not in keys:
				results.append(t)
				keys.append(t['text'])

		return results
