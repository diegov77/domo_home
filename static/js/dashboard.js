//dashboard.js


window.chartColors = [
	'rgb(255, 99, 132)',
	'rgb(255, 159, 64)',
	'rgb(255, 205, 86)',
	'rgb(75, 192, 192)',
	'rgb(54, 162, 235)',
	'rgb(153, 102, 255)',
	'rgb(201, 203, 207)',
	'rgb(38, 174, 187)',
	'rgb(188, 38, 83)',
	'rgb(151, 200, 0)'
];

function controlAlarma() {
	$("#alarm-switch-dashboard").bootstrapSwitch();
	alarmStatus = $('#alarm-status-dashboard').data("status");
	if (alarmStatus == "1") {
		$('#alarm-switch-dashboard').bootstrapSwitch('state', true);
	}
	else if (alarmStatus == "0") {
		$('#alarm-switch-dashboard').bootstrapSwitch('state', false);
	}
}

$('#alarm-switch-dashboard').on('switchChange.bootstrapSwitch', function (event, state){
	var route = "";
	if (state) {
		//route = "arduino/alarm?action=alarm_mov_on"
		// alert("Alarma activa.");
	}
	else if (!state) {
		//route = "arduino/alarm?action=alarm_mov_off"
		// alert(state);
	}
	
	//$.ajax({
        //url: route,
        //type: 'get',
    //}).done(function () {
        
    //});
});


//-------------------------- chart area section ------------------------
function loadChartArea(selectMonth) {
	var route = "get_monthly_expense_by_area"
	if (selectMonth !== undefined ){//|| selectMonth !== "0") {
		route = route + "?month=" + selectMonth;
	}
	
	$.ajax({
        
        url: route,
        type: 'get',
        dataType: 'json',
    }).done(function (response) {
        
        
        if (response.length !== 0) {
        	$('#alert-chart-area').addClass('hidden');
        	var data = areaHandler(response);
        	chartArea(data);
        }
        else {
        	if (window.myPieArea) {
        		window.myPieArea.destroy();
        	}
        	$('#alert-chart-area').removeClass('hidden');
        }
        
    });
}

function areaHandler(dataArea) {
	
	var labels = [];
	var expenses = [];
	var colors = [];
	for (var i = 0; i < dataArea.expense_list.length; i++) {
		labels.push(dataArea.expense_list[i].area_name);
		if (dataArea.expense_list[i].expense < 1 && dataArea.expense_list[i].expense > 0) {
			expenses.push(Math.ceil(dataArea.expense_list[i].expense));
		} else {
			expenses.push(dataArea.expense_list[i].expense.toFixed(0));	
		}
		colors.push(window.chartColors[i]);
	}

	var data = {
		labels: labels,
		expenses: expenses,
		colors: colors
	};
	
	return data;
}

function chartArea(data) {
	var labels = data.labels;
	
	var expenses = data.expenses;
	var ctx = $("#chart-area");
	if (window.myPieArea) {
		window.myPieArea.destroy();
	}
	window.myPieArea = new Chart(ctx,{
	    type: 'pie',
	    
	    data: {
	    	datasets: [{
		        data: expenses,
		        backgroundColor: data.colors
		    }],
	    	labels: data.labels
	    },
	    options: {
	    	animation: {animateScale: true},
	    	responsive: true
	    }
	});
}

$('#select-mes-area').on('change', function () {
	var month = $(this).val();
	loadChartArea(month);
});
//-------------------------- end chart area section ------------------------

//-------------------------- chart appliance section -----------------------
function loadChartAppliance(selectMonth) {
	var route = "get_monthly_expense_by_appliance"
	if (selectMonth !== undefined) {
		route = route + "?month=" + selectMonth;
		console.log(route);
	}
	
	$.ajax({
        
        url: route,
        type: 'get',
        dataType: 'json',
    }).done(function (response) {
        
        if (response.length !== 0) {
        	$('#alert-chart-appliance').addClass('hidden');
        	var data = applianceHandler(response);
        	chartAppliance(data);
        }
        else {
        	if (window.myPieAppliance) {
        		window.myPieAppliance.destroy();
        	}
        	$('#alert-chart-appliance').removeClass('hidden');
        }
        
    });	
}

function applianceHandler(dataApp) {
	
	var labels = [];
	var expenses = [];
	var colors = [];
	for (var i = 0; i < dataApp.length; i++) {
		labels.push(dataApp[i].appliance_name);
		if (dataApp[i].expense < 1 && dataApp[i].expense > 0) {
			expenses.push(Math.ceil(dataApp[i].expense));
		} else {
			expenses.push(dataApp[i].expense.toFixed(0));	
		}
		colors.push(window.chartColors[i]);
	}
	var data = {
		labels: labels,
		expenses: expenses,
		colors: colors
	};
	return data;
}

function chartAppliance(data) {
	var labels = data.labels;
	var expenses = data.expenses;
	var ctx = $("#chart-appliance");
	if (window.myPieAppliance) {
		window.myPieAppliance.destroy();
	}
	window.myPieAppliance = new Chart(ctx,{
	    type: 'pie',
	    
	    data: {
	    	datasets: [{
		        data: expenses,
		        backgroundColor: data.colors
		    }],
	    	labels: data.labels
	    },
	    options: {
	    	animation: {animateScale: true},
	    	responsive: true
	    }
	});
}

$('#select-mes-appliance').on('change', function () {
	var month = $(this).val();
	loadChartAppliance(month);
});
//-------------------------- end chart appliance section ------------------------

//-------------------------- chart Line section ---------------------------------
function loadChartLine(selectedYear) {
	var route = "get_monthly_expenses"
	if (selectedYear !== undefined) {
		route = route + "?year=" + selectedYear;
	} else {
		selectedYear = new Date().getFullYear();
	}

	$.ajax({
        // url: "http://192.168.1.50:5000/" + route,
        url: route,
        type: 'get',
        dataType: 'json',
    }).done(function (response) {
        
        if (response.length !== 0) {
        	
        	var data = lineDataHandler(response);
        	chartLine(data,selectedYear);
        }
        else {
        	if (window.myLine) {
        		window.myLine.destroy();
        	}
        	
        }    
    });
}

function lineDataHandler(dataApp) {
	
	var labels = [];
	var expenses = [];
	for (var i = 0; i < dataApp.length; i++) {
		labels.push(dataApp[i].month);
		if (dataApp[i].expense < 1 && dataApp[i].expense > 0) {
			expenses.push(Math.ceil(dataApp[i].expense));
		} else {
			expenses.push(dataApp[i].expense.toFixed(0));	
		}
	}
	var data = {
		labels: labels,
		expenses: expenses
	};
	return data;
}

function chartLine(data, year) {
    var labels = data.labels;
	var expenses = data.expenses;
	var labelYear = year;
    var ctx = $("#line-chart");

    if (year !== undefined) {
    	labelYear = year;
    }

    if (window.myLine) {
		window.myLine.destroy();
	}
    window.myLine = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Gastos año ' + labelYear,
                    data: expenses,
                    fill: false,
                    backgroundColor: window.chartColors[4],
                    borderColor: window.chartColors[4]
                },
            ]
        },
        options: {
            responsive: true,
            title:{
                display:true,
                
            },
            tooltips: {
                mode: 'nearest',
                intersect: false,
                
                callbacks: {
	                labelColor: function(tooltipItem, chart) {
	                    return {
	                        borderColor: window.chartColors[4],
	                        backgroundColor: window.chartColors[4]
	                    }
	                },
	                
	            }
            },
           	point: {
           		backgroundColor: 'rgba(38,174,187,0.2)',
           		borderColor: 'rgba(38,174,187,1)' 
           	},
            hover: {
                    mode: 'nearest',
                    intersect: true
                },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Mes'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Valor en Gs.'
                    }
                }]
            }
        }
    });
}

$('#select-year-line').on('change', function () {
	var year = $(this).val();
	loadChartLine(year);
});

//-------------------------- end chart Line section ---------------------------------


function loadTableTotalExpenseYear() {

	$.ajax({
        url: "get_all_expenses",
        // url: "http://192.168.1.50:5000/get_all_expenses",
        type: 'get',
        dataType: 'json',
    }).done(function (response) {
        
        if (response.length !== 0) {
        	//$('#alert-chart-line').addClass('hidden');
        	//var data = lineDataHandler(response);
        	// chartLine(data,selectedYear);
        	tableExpensesHandler(response);
        	loadDataTable();
        }
        // else {
        // 	if (window.myLine) {
        // 		window.myLine.destroy();
        // 	}
        // 	//$('#alert-chart-line').removeClass('hidden');
        // }    
    });
}

function tableExpensesHandler(data) {
	var $tbody = $('#table-total-expenses-list');
	$tbody.empty();
	for (var i = 0; i < data.length; i++) {
		var $tr = $('<tr class="expenses-row"></tr>');
		$tr.append('<td class="area-name">' + data[i].area_name + '</td>');
		$tr.append('<td class="appliance-name">' + data[i].appliance_name + '</td>');
		$tr.append('<td class="datetime-on">' + data[i].datetime_on + '</td>');
		$tr.append('<td class="datetime-off">' + data[i].datetime_off + '</td>');
		$tr.append('<td class="duration">' + data[i].duration + '</td>');
		$tr.append('<td class="expense">' + data[i].expense + '</td>');
		$tbody.append($tr);
	}
}

function loadDataTable() {
	$('#table-total-expenses').DataTable({
		"bDestroy": true,
	    "order": [0, 'desc'],
	    "language": {
	        "sProcessing": "Procesando...",
	        "sLengthMenu": "Mostrar _MENU_ registros",
	        "sZeroRecords": "No se encontraron resultados",
	        "sEmptyTable": "Ningún dato disponible en esta tabla",
	        "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
	        "sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
	        "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
	        "sInfoPostFix": "",
	        "sSearch": "Buscar:",
	        "sUrl": "",
	        "sInfoThousands": ",",
	        "sLoadingRecords": "Cargando...",
	        "oPaginate": {
	            "sFirst": "Primero",
	            "sLast": "Último",
	            "sNext": "Siguiente",
	            "sPrevious": "Anterior"
	        },
	        "oAria": {
	            "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
	            "sSortDescending": ": Activar para ordenar la columna de manera descendente"
	        }
	    },
	    
	});	
}



function setDefaultValSelectCharts() {
	var currentMonth = new Date().getMonth()+1;
	var currentYear = new Date().getFullYear();
	$('#select-mes-area').val(currentMonth);
	$('#select-mes-appliance').val(currentMonth);
	$('#select-year-line').val(currentYear);
}

$('document').ready(function () {
	controlAlarma();
	loadChartArea();
	loadChartAppliance();
	loadChartLine();
	setDefaultValSelectCharts();
	loadTableTotalExpenseYear();
});
