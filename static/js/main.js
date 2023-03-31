$(document).ready(function() {
	$("#profile-edit-btn").click(function(){
		alert('dd')
		$("#profile-edit-form").show();
	});

	$('#signup-form').on('submit', function(event) {
		$.ajax({
			url : '/signup',
			type : 'POST',
			contenttype: 'application/json', 
			data : {
				name : $('#name').val(),
				username : $('#username').val(),
				email : $('#email').val(),
				password : $('#password').val(),
			},
			success: function(response) {
				$("#uslabel").text(response);
			},
			error: function(XMLHttpRequest, textStatus, errorThrown) { 
                    $("#uslabel").html(response); 
                }  
		});
		event.preventDefault();
	});
});