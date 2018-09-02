function editAppliance() {
    console.log($("#form-appliance-edit").serialize());
    $.ajax({
        /*url: 'http://192.168.1.51:5000/submit_appliance',*/
        url: 'appliance_edit',
        type: 'post',
        dataType: 'json',
        data: $("#form-appliance-edit").serialize(),
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

$('#save-form-appliance-edit').click(function () {
    console.log("click");
    editAppliance();
});