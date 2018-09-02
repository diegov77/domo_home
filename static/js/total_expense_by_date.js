//Total expense by date

function controlCategoria() {
	$areaGroup = $("#area-group-dashboard-expense");
	$applianceGroup = $("#appliance-group-dashboard-expense");
	categoriaVal = $("#category-expense").val();
	
	if (categoriaVal == 0) {
		$areaGroup.addClass("hidden");
		$applianceGroup.addClass("hidden");
	}
	else if (categoriaVal == 1) {
		$areaGroup.removeClass("hidden");
		$applianceGroup.addClass("hidden");
	}
	else if (categoriaVal == 2) {
		$applianceGroup.removeClass("hidden");
		$areaGroup.addClass("hidden");
	}

	// if (!$areaGroup.hasClass("hidden")) {
	// 	$areaGroup.addClass("hidden");
	// };

	// if (!$applianceGroup.hasClass("hidden")) {
	// 	$applianceGroup.addClass("hidden");
	// };
};

$("#category-expense").on('change', function () {
	controlCategoria();
});

function queryExpense() {
    
    var selectCategoryExpenseVal = $("#category-expense").val();
    var selectAreaVal = $("#area-total-expense").val();
    var selectApplianceVal = $("#appliance-total-expense").val();
    var route = "";

    if (selectCategoryExpenseVal === "0") {
    	route = "get_total_expense";
    } else if (selectCategoryExpenseVal === "1" && selectAreaVal !== "0") {
    	route = "get_expense_by_area";
    } else if (selectCategoryExpenseVal === "2" && selectApplianceVal !== "0") {
    	route = "get_expense_by_appliance";
    } else {
    	$("#alert-total-expense").append("<span>Debe seleccionar un valor para Dispositivo/Area</span>");
    	$("#alert-total-expense").removeClass('hidden');
    	return 0;
    }

    $.ajax({
        //url: "http://192.168.1.62:5000/" + route,
        url: route,
        type: 'post',
        dataType: 'json',
        data: $("#form-total-expense").serialize(),

    }).done(function (response) {
        
        if (response.status === 1) {
            
            $("#total-expense").html(response.result.toFixed(0) + ' Gs');
        } else {
            $("#total-expense").html(response.result);
        }
    });
}


$('#query-total-expense').click(function () {
    queryExpense();
});

$("document").ready(function () {
    controlCategoria();
});
