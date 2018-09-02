//ajax.js

const SERVER = '';

function ajaxGetUsers(getOptions) {
	console.log("ajaxGetUsers");
	getOptions.type = 'GET';

	$.ajax({
        url: getOptions.url,
        type: getOptions.type,
        dataType: 'json',
    }).done(function (response) {
        getOptions.successFn(response);
    });
}
