

$(function () {
    // $('#txt-birth-date-form').datetimepicker({
    //     format: 'DD/MM/YYYY'
    // });
});

function signUp() {
    console.log($("#form-new-user").serialize());
	$.ajax({
        url: 'create_user',
        type: 'post',
        dataType: 'json',
        data: $("#form-new-user").serialize(),
        /*success: function (response) {
                console.log(data);
                if(response.status === "success") {
                    // do something with response.message or whatever other data on success
                    url = "http://192.168.1.55:5000/dashboard"; //cambiar ruta por users; vista que lista usuarios creados.
                        $( location ).attr("href", url);
                } else if(response.status === "error") {
                    // do something with response.message or whatever other data on error. Redirigir a pantalla de eror en caso de error.
                }
            }*/
    }).done(function (response) {
        console.log(response);
        if (response.status === 1) {
        	console.log("entro if");
        	var url = "user_index";
			$( location ).attr("href", url);
        } else {
            $('.alert-danger').removeClass('hidden');
            $('.respuesta-error').html('');
        	$('.respuesta-error').html(response.msg);
        }
    });
}


$('#save-form-user').click(function () {
	console.log("click");
	signUp();
});