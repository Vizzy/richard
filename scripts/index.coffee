humanise_lang_name = (lang_code) ->
	lang_pairs = JSON.parse localStorage.getItem 'langs'

	for lang of lang_pairs
		if lang is lang_code
			return lang_pairs[lang_code]['name']

get_langs = ->
	$.getJSON 'get_lang_pairs', (data) =>
		localStorage.setItem('langs', JSON.stringify data)
		update_available_langs()


update_available_langs = ->
	selected_lang = $('#langfrom_selector option:selected').val()
	$('#langto_selector').empty()

	lang_pairs = JSON.parse localStorage.getItem 'langs'

	for lang in lang_pairs[selected_lang]['targets']
		$new_lang_option = $('<option></option>')
		$new_lang_option.attr('value', lang)
		$new_lang_option.text(humanise_lang_name lang)

		$('#langto_selector').append $new_lang_option

$(document).ready =>

	get_langs()

	$('#langfrom_selector').change =>
		update_available_langs()

	$('#lookup_form').submit (event) =>

		lang_from = $('#langfrom_selector option:selected').val()
		lang_to = $('#langto_selector option:selected').val()
		query = $('#query_entry').val()

		payload =
			lang_from: lang_from
			lang_to: lang_to
			query: query
			as_json: true

		$.post('lookup/', payload).done (data) =>
			results = JSON.parse data

			$results_div = $('#results')

			$results_div.hide 200, () ->
				$results_div.empty()
				for r in results
					if r['tr'] isnt undefined			
						for t in r['tr']
							$results_line = $('<p></p>')

							for key, value of t

								if key is 'pos'
									$results_line.append '[' + value + '] '
								else if key is 'text'
									$results_line.append value
								else
									if $DEBUG
										console.log key, value

							$results_div.append $results_line

				$results_div.fadeIn 200

		false

		



