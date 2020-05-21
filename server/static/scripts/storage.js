$(document).ready(function() {
	$('#new-button').click(function() {
		$('#form-wrapper').css('opacity', '1');
		$('#form-wrapper').css('z-index', '2');
	});
	$('#x').click(function() {
		$('#form-wrapper').css('opacity', '0');
		$('#form-wrapper').css('z-index', '-1');
	});
	$('#upload-button').click(function() {
		$('#upload-wrapper').css('opacity', '1');
		$('#upload-wrapper').css('z-index', '2');
	});
	$('#x2').click(function() {
		$('#upload-wrapper').css('opacity', '0');
		$('#upload-wrapper').css('z-index', '-1');
	});
	var count = 0;

	$('.dots').click(function() {
		if (count % 2 == 0) {
			$('.menu-button .menu').css('opacity', '1');
			$('.menu-button .menu').css('z-index', '1');
		} else {
			$('.menu-button .menu').css('opacity', '0');
			$('.menu-button .menu').css('z-index', '-1');
		}
		count += 1;	
	});

});