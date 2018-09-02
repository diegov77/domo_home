// javascript user_edit


$("document").ready(function () {
	
	/*$.ajax({
	    url: "http://192.168.1.50:5000/getUserList",
	    type: 'GET',
	    success: function(results) {
		    var htmlStr = '';
		    $.each(results, function(k, v){
		        htmlStr += v.id + ' ' + v.name + '<br />';
		   	});
		   // $("#page").html(htmlStr);
		}
	});*/
	
	// $('#txt-birth-date-form').datetimepicker({
 //        format: 'DD/MM/YYYY'
 //    });
});


function editUser() {
    console.log($("#form-edit-user").serialize());
	$.ajax({
        url: 'user_edit',
        type: 'POST',
        dataType: 'json',
        data: $("#form-edit-user").serialize(),
    }).done(function (response) {
        console.log(response.status);
        if (response.status === 1) {
        	console.log("entro if");
        	var url = "user_index";
			$( location ).attr("href", url);
        } else {
        	$('#respuesta').html(response.message);
        }
    });
}



$('#save-form-user-edit').click(function () {
	var userid = $('#id-edit-user-form');
	console.log(userid);
	editUser();
});