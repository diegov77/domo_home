

function submitAppliance() {
	$.ajax({
        /*url: 'http://192.168.1.51:5000/submit_appliance',*/
        url: 'appliance_create',
        type: 'post',
        dataType: 'json',
        data: $("#form-appliance-register").serialize(),
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
            var url = "appliance_index";
            $( location ).attr("href", url);
        } else {
            $('#respuesta').html(response.message);
        }
    });
}

$('#save-form-appliance').click(function () {
	console.log("click");
	submitAppliance();
});