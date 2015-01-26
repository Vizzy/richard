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
					$results_div.append('<p> [' + r['pos'] + '] ' + r['text'] + '</div>')

				$results_div.fadeIn 200

		false

		



