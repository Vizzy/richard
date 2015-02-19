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

textify = (value) ->
	'<p>' + value + '</p>'

$(document).on 'click', 'span.entry', (event) =>
	console.log 'clicked'
	entry = $(this).data 'entry'
	div = $('div[data-entry=' + entry + ']')
	console.log div.class
	div.show()


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

			# make this choose it according to language
			$EXAMPLE_WORD = 'example'

			$results_div = $('#results')

			$results_div.hide 200, () ->
				$results_div.empty()
				if results['tr'] isnt undefined			
					for t in results['tr']
						$result_line = $('<div class="result"></div>')
						entry = ''

						if $DEBUG
							console.log t['text'] + ' ' + t

						for key, value of t

							if key is 'pos'
								entry += '[' + value + '] '
							else if key is 'text'
								entry += value
							else if key is 'ex' and value isnt undefined
								$example_div = $('<div class="usage_example"></div>')
								$example_div.attr("data-entry", t['text'])
								$example_div.hide()
								for ex in value
									$example_div.append textify ex['text']
									$example_div.append textify ex['tr']

						$entry_span = $('<span class="entry"></span>')
						$entry_span.attr 'data-entry', t['text']
						$entry_span.append textify entry
						$result_line.append $entry_span
						$result_line.append $example_div

						$results_div.append $result_line

				$results_div.fadeIn 200

		false

		



