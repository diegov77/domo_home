//task.js


function applianceByAreaIdHandler(data) {
	var $select = $('#appliance-taks');
	$select.html('');
	$select.append('<option value="0">Seleccione...</option>');
	for (var i = 0; i < data.length; i++) {
		$select.append('<option value="' + data[i].id + '">' + data[i].name + '</option>');
	}
}

function getAppliancesByAreaId(areaId) {

	$.ajax({
        url: "get_active_appliances_by_areaid?areaId=" + areaId,
        type: 'get',
        dataType: 'json',
    }).done(function (response) {
        if (response.length !== 0) {
        	applianceByAreaIdHandler(response);
        }
        else {
        	console.log("error");
        }
    });
};

$("#area-task").on('change', function () {
	var areaId = $("#area-task").val();
	getAppliancesByAreaId(areaId);
});

// function taskListHandler(data) {
// 	var $tbody = $('#task-list');
// 	$tbody.empty();
// 	for (var i = 0; i < data.length; i++) {
// 		var $tr = $('<tr class="task-row"></tr>');
// 		// $tr.append('<td class="task-name">' + data[i].name + '</td>');
// 		$tr.append('<td class="task-description">' + data[i].description + '</td>');
// 		$tr.append('<td class="task-creatio-date">' + data[i].creationDate + '</td>');
// 		$tr.append('<td class="taks-time">' + data[i].time + '</td>');
// 		if (data[i].status == 1) {
// 			$tr.append('<td class="task-status">Si</td>');
// 		}
// 		else {
// 			$tr.append('<td class="task-status">No</td>');
// 		}
// 		$tr.append('<td class="taks-area">' + data[i].area + '</td>');
// 		$tr.append('<td class="taks-appliance">' + data[i].appliance + '</td>');
// 		if (data[i].validRole == true) {
// 			if (data[i].status == 1) {
// 				$tr.append('<td><a id="btn-edit-task-status' + data[i].id + '" class="btn btn-warning btn-edit-task-status" data-status="' + data[i].status  + '" data-id="' + data[i].id + '" role="button">Desactivar</a></td>');
// 			}
// 			else {
// 				$tr.append('<td><a id="btn-edit-task-status' + data[i].id + '" class="btn btn-warning btn-edit-task-status" data-status="' + data[i].status  + '" data-id="' + data[i].id + '" role="button">Activar</a></td>');
// 			}
			
// 		}
// 		$tbody.append($tr);
// 	}
// }

// function getTaskList() {
	
// 	$.ajax({
//         url: "http://0.0.0.0:5000/task_list",
//         type: 'get',
//         dataType: 'json',
//     }).done(function (response) {
//         if (response.length !== 0) {
//         	taskListHandler(response);
//         }
//         else {
//         	console.log("error");
//         }
//     });	
// }

// function submitTask() {
// 	$.ajax({
//         url: 'http://0.0.0.0:5000/task_create',
//         /*url: 'http://192.168.1.50:5000/submit_area',*/
//         type: 'post',
//         dataType: 'json',
//         data: $("#form-new-task").serialize(),
//         success: function (response) {
//                 console.log(data);
//                 if(response.status === "success") {
//                     // do something with response.message or whatever other data on success
//                     url = "http://192.168.1.55:5000/dashboard"; //cambiar ruta por users; vista que lista usuarios creados.
//                         $( location ).attr("href", url);
//                 } else if(response.status === "error") {
//                     // do something with response.message or whatever other data on error. Redirigir a pantalla de eror en caso de error.
//                 }
//             }
//     }).done(function (response) {
//     	console.log(response);
//         if (response.status === 1) {
//             // var url = "http://0.0.0.0:5000/task_index";
//             // $( location ).attr("href", url);
//             $('#alert-new-task-success').removeClass('hidden');
//         } else {
//         	$('#alert-new-task-danger').removeClass('hidden');
//             // $('#respuesta').html(response.message);
//         }
//     });
// }

// function editStatusTask(status, taskId) {
//     // var status = $('#');
//     // var taskId = ;
//     var dataStatus = {
//     	id: taskId,
//     	status: status
//     };
// 	$.ajax({
//         url: 'http://0.0.0.0:5000/task_edit',
//         /*url: 'http://192.168.1.50:5000/submit_area',*/
//         type: 'post',
//         dataType: 'json',
//         data: dataStatus
//         /*success: function (response) {
//                 console.log(data);
//                 if(response.status === "success") {
//                     // do something with response.message or whatever other data on success
//                     url = "http://192.168.1.55:5000/dashboard"; //cambiar ruta por users; vista que lista usuarios creados.
//                         $( location ).attr("href", url);
//                 } else if(response.status === "error") {
//                     // do something with response.message or whatever other data on error. Redirigir a pantalla de eror en caso de error.
//                 }
//             }*/
//     }).done(function (response) {
//         if (response.status === 1) {
//             // var url = "http://0.0.0.0:5000/task_index";
//             // $( location ).attr("href", url);
//             $('#alert-edit-task-success').removeClass('hidden');
//         } else {
//         	$('#alert-edit-task-danger').removeClass('hidden');
//             // $('#respuesta').html(response.message);
//         }
//         getTaskList();
//     });
// }

// $('#save-new-task').click(function () {
// 	submitTask();
// 	getTaskList();
// });

// $('.btn-edit-task-status').on('click', function () {
// 	var $e = $(this);
// 	console.log("edit");
// 	var status = $e.data('status');
//     var taskId = $e.data('id');
//     editStatusTask(status, taskId);
	
// });


// $('document').ready(function () {
// 	$('#area-task').val(0);
// 	getTaskList();
// });