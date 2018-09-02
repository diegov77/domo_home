// javascript area_edit


$("document").ready(function () {
	
});


function editArea() {
    console.log($("#form-edit-area").serialize());
	$.ajax({
        url: 'area_edit',
        type: 'POST',
        dataType: 'json',
        data: $("#form-edit-area").serialize(),
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
        	var url = "area_index";
			$( location ).attr("href", url);
        } else {
        	$('#respuesta').html(response.message);
        }
    });
}

// function signUp() {
//     var options = {
//         var url = "http://192.168.1.50:5000/user_index";

//     }
// }

//$('#botonera-form-area-edit').click(function () {
$('#btn-save-area-edit').click(function () {    
	var areaId = $('#id-edit-area-form');
	console.log(areaId);
	editArea();
});