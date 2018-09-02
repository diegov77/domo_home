//---user-index.js



function getUserList() {
	var options = {
		url: "getUserList",
		successFn: handleUserList
	}
	ajaxGetUsers(options);
}


function handleUserList(res) {
	var users = res;
	renderUsers(users);
}

function renderUsers(users) {
	var $lisUsers = $("#users-list-created");
	$lisUsers.empty();
	for (var i = 0; i < users.length; i++) {
		var user = users[i];
		var $tr = $('<tr class="user"></tr>');

		$tr.data("userId", user.id);
		$tr.append('<td class="user-name">' + user.name + '</td>');
		$tr.append('<td class="user-lastname">' + user.lasName + '</td>');
		$tr.append('<td class="user">' + user.user + '</td>');
		$tr.append('<td class="user-phone">' + user.phone + '</td>');
		$tr.append('<td class="user-email">' + user.email + '</td>');
		$tr.append('<td class="user-creation">' + user.creationDate + '</td>');
		$tr.append('<td class="user-birthday">' + user.birthday + '</td>');
		$tr.append('<td class="user-role" value="'+ user.role.id +'">' + user.role.name + '</td>');
		if (user.status == 1) {
			$tr.append('<td class="user-status">Si</td>');
		} else if (user.status == 0) {
			$tr.append('<td class="user-status">No</td>');
		}
		$tr.append('<td><a id="btn-edit-user ' + user.id + '" class="btn btn-primary btn-edit-user" href="/user_edit/' + user.id +'" role="button">Editar</a></td>');
		$lisUsers.append($tr);
	};
}