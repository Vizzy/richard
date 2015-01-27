update_available_langs = ->
	selected_lang = $('#langfrom_selector option:selected').text()
	$('#langto_selector').empty()

	lang_pairs = JSON.parse localStorage.getItem 'langs'

	for lang in lang_pairs[selected_lang]
		$new_lang_option = $('<option></option>')
		$new_lang_option.attr('value', lang)
		$new_lang_option.text lang

		$('#langto_selector').append $new_lang_option

$(document).ready =>
	$.getJSON 'get_lang_pairs', (data) =>
		localStorage.setItem('langs', JSON.stringify data)
		update_available_langs()

	$('#langfrom_selector').change =>
		update_available_langs()

	$('#lookup_form').submit (event) =>

		lang_from = $('#langfrom_selector option:selected').text()
		lang_to = $('#langto_selector option:selected').text()
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
									console.log key, value

							$results_div.append $results_line

				$results_div.fadeIn 200

		false

		



