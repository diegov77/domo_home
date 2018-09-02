
function loguear() {
	console.log("login");
    console.log($("#login-form").serialize());
	$.ajax({
        url: 'login',
        type: 'post',
        dataType: 'json',
        data: $("#login-form").serialize(),
    }).done(function (response) {
        console.log(response.status);
        if (response.status === 1) {
            var url = "dashboard";
            $( location ).attr("href", url);
        } else {
            $('.alert-danger').removeClass('hidden');
            $('.respuesta-error').html('');
            $('.respuesta-error').html(response.msg);
        }
    });
}
$('#login').click(function () {
	console.log("click");
	loguear();
});
