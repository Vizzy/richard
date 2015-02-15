import urllib.parse as urlparse
from itertools import filterfalse, chain, starmap
from collections import defaultdict
from multiprocessing.pool import Pool
from concurrent import futures
import asyncio
import os
from difflib import SequenceMatcher

import requests
import simplejson as json

class UnsupportedLanguageException(ValueError):
    pass

class CrossLookup:
    def __init__(self, apikey, translate_key=None):
        self._base_url = 'https://dictionary.yandex.net/api/v1/dicservice.json/'
        self.apikey = apikey
        self.translate_key = translate_key
        self.supported_directions = defaultdict(list)
        self.supported_langs = []
        self.loop = asyncio.get_event_loop()

        self.loop.run_in_executor(None, self.__get_languages)


    def __get_languages(self):
        r = requests.get(urlparse.urljoin(self._base_url, 'getLangs'),
                params=dict(key=self.apikey))
        self.supported_langs = json.loads(r.text)

        for pair in self.supported_langs:
            split_pair = pair.split('-')
            self.supported_directions[split_pair[0]].append(split_pair[1])

    @staticmethod
    def num_workers(queries):
        return len(queries) if len(queries) <= os.cpu_count() else os.cpu_count()


    def lookup(self, query, lang_from, lang_to, interface_lang='en'):
        lang = lang_from + '-' + lang_to
        #if lang not in self.supported_langs:
        #    raise UnsupportedLanguageException

        payload = {'key': self.apikey, 'lang': lang,
                    'text': query, 'ui': interface_lang}
        r = requests.get(urlparse.urljoin(self._base_url, 'lookup'),
                params=payload)
        result = json.loads(r.text)
        return result

    def lookup_translate(self, query, lang_from, lang_to):
        lang = lang_from + '-' + lang_to
        #if lang not in self.supported_langs:
        #   raise UnsupportedLanguageException

        payload = {'key': self.translate_key, 'lang': lang,
                    'text': query}
        r = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate',
                params=payload)
        result = json.loads(r.text)
        return result



    def partially_in(self, iterable, query, threshold=0.8):
        seqmatcher = SequenceMatcher(isjunk=None, b=query)

        for e in iterable:
            seqmatcher.set_seq1(e)
            if seqmatcher.quick_ratio() >= threshold:
                return True
        else:
            return False


    def meaning_overlaps(self, queries, translations):
        overlaps = []
        num_workers = self.num_workers(queries)

        with futures.ProcessPoolExecutor(max_workers=num_workers) as e:
            for t in translations:
                meanings = [m['text'] for m in t.get('mean', [])]
                examples = [ex['text'] for ex in t.get('ex', [])]
                for query in queries:
                    partial_matches = e.map(self.partially_in,
                                            (meanings, examples),
                                            (query, query))

                    if True in partial_matches:
                        # there is a partial match
                        overlaps.append(t)
            else:
                # there are no overlaps between query results
                pass

        return overlaps

    @staticmethod
    def translation_overlaps(strings):
        narrow = []

        # work out the average occurrence of each translation
        occs = set((strings.count(s)/len(strings) for s in strings))
        avg_occ = sum(occs)/len(occs)

        # are there any overlaps at all?
        if avg_occ <= 1/len(strings):
            return narrow

        for s in strings:

            # does it occur a lot (i.e. above average)?
            if strings.count(s)/len(strings) >= avg_occ:
                narrow.append(s)

        return narrow


    def crossword_lookup(self, queries, lang_from, lang_to, 
                        interface_lang='en', pos=(), unique=True):

        queries = list(queries)

        translations = []
        clever_translations = []

        workers = self.num_workers(queries)
        with futures.ThreadPoolExecutor(max_workers=len(queries)) as e:
                results = e.map(self.lookup,
                            queries, (lang_from for x in range(len(queries))),
                            (lang_to for x in range(len(queries))))
                results = list(results)
            
        translations_by_pos = chain.from_iterable((r['def'] for r in results))

        # filter by part of speech
        if list(iter(pos)) != []:
            translations_by_pos = filter(
                                        lambda x: x['pos'] in pos, 
                                        translations_by_pos)


        # goodbye, laziness
        translations_by_pos = list(translations_by_pos)

        if len(translations_by_pos) is 0:
            # no translations were found
            return [], False

        # filter by meanings and examples
        for tbps in translations_by_pos:
            remaining_queries = queries[:]
            try:
                remaining_queries.remove(tbps['text'].casefold())
            except ValueError:
                # work this out later (accents etc.)
                ...
            overlaps = self.meaning_overlaps(remaining_queries, tbps['tr'])
            if len(overlaps) > 0:
                tbps['tr'] = overlaps
                clever_translations.append(tbps)

        all_translations = chain.from_iterable([tbps['tr'] 
                            for tbps in translations_by_pos])

        translation_strings = [s['text'] for s in all_translations]
        narrow = self.translation_overlaps(translation_strings)

        if len(narrow) > 0:
            for tbps in translations_by_pos:
                overlapping_translations = [translation 
                            for translation in tbps['tr']
                            if translation['text'] in narrow]
                tbps['tr'] = overlapping_translations
                clever_translations.append(tbps)

        if len(clever_translations) > 0:

            # filter 'empty' translations
            # i.e. those which have been filtered out above
            clever_translations = list(filter(lambda x: len(x['tr']) > 0,
                                                clever_translations))
            if unique:
                unique_translations = []
                keys = []
                examples = []

                for transs in clever_translations:
                    for t in transs['tr']:
                        if t['text'] not in keys:
                            keys.append(t['text'])
                            unique_translations.append(t)
                        example = t.get('ex')
                        if example:
                            examples.append(example)

                unique_translations[-1]['ex'] = examples

                clever_translations = unique_translations

            return {'tr': clever_translations}, True
        else:
            return results[0]['def'][0], False

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
