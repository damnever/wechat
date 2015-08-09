// Flags
var usernameOk = false;
var emailOk = false;
var passwordOk = false;
var repasswdOk = false;
var fileOk = false;

function allowSignup() {
	$('[type="submit"]').click(function() {
		if (!(usernameOk && emailOk && passwordOk && repasswdOk && fileOk)) {
			showMessage("有未完成的表单项！");
			return false;
		}
	});
}


function allowLogin() {
	$('[type="submit"]').click(function() {
		if (!(emailOk && passwordOk)) {
			showMessage("有未完成的表单项！");
			return false;
		}
	});
}

function allowFindpw() {
	$('[type="submit"]').click(function() {
		if (!emailOk) {
			showMessage("有未完成的表单项！");
			return false;
		}
	});
}

function allowChangepw() {
	$('[type="submit"]').click(function() {
		if (!(passwordOk && repasswdOk)) {
			showMessage("有未完成的表单项！");
			return false;
		}
	});
}

function checkUsername(send) {
	$('[name="username"]').blur(function() {
  		var username = $('[name="username"]').val();
		if (showNullMessage(username, "用户名不能为空！")) return;
		hideMessage("用户名不能为空！");
		if (username.length < 3) {
			showMessage("用户名需要3~6个字符之间！");
			return;
		}
		hideMessage("用户名需要3~6个字符之间！");

		if (send) {
			// Send username and check if existed.
			var data = {"username": username};
			$.get("/checkusername", data, function(response) {
				console.log(response);
				if (response == "fail") {
					showMessage("用户名已经存在！");
				} else if (response == "ok") {
					usernameOk = true;
					hideMessage("用户名已经存在！");
				}
			});
		} else {
			usernameOk = true;
		}
	});	
}

function checkEmail(check) {
	$('[name="email"]').blur(function() {
  		var email = $('[name="email"]').val();
		if (showNullMessage(email, "邮箱不能为空！")) return;
		hideMessage("邮箱不能为空！");
		var reg = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
		if ( !reg.test(email) ) {
			showMessage("邮箱格式不正确！");
        	return;
    	}
    	hideMessage("邮箱格式不正确！");

		if (check) {
			// Send email and check if existed. For signup.
			var message = {"check": "yes", "email": email};
			$.postJSON("/checkemail", message, function(response) {
				console.log(response);
				if (response == "fail") {
					showMessage("邮件地址已经存在！");
				} else if (response == "ok") {
					emailOk = true;
					hideMessage("邮件地址已经存在！");
				}
			});
		} else {
			// Send email and check if illegal. For login.
			var message = {"email": email};
			$.postJSON("/checkemail", message, function(response) {
				if (response == "fail") {
					showMessage("邮件地址不存在！");
				} else if (response == "not") {
					showMessage("邮件地址还未验证，请查收邮件进行验证！");
				}else if (response == "ok") {
					emailOk = true;
					hideMessage("邮件地址不存在！");
					hideMessage("邮件地址还未验证，请查收邮件进行验证！");
				}
			});
		}
	});	
}

function checkPassword(send) {
	$('[name="password"]').blur(function() {
  		var password = $('[name="password"]').val();
		if (showNullMessage(password, "密码不能为空！")) return;
		hideMessage("密码不能为空！");
		if (password.length < 8) {
			showMessage("密码需要8~10个字符！");
			return;
		}
		hideMessage("密码需要8~10个字符！");
		if(send) {
			// check password
			var form = $("form");
			var message = form.formToDict();
			var disabled = form.find("input[type=submit]");
			disabled.disable();
			$.postJSON("/checkpassword", message, function(response) {
				console.log(response);
				if (response == "fail") {
					form.find("input[type=password]").val("").select();
					showMessage("密码错误！");
					disabled.enable();
				} else if (response == "ok") {
					passwordOk = true;
					hideMessage("密码错误！");
				}
			});
		} else {
			passwordOk = true;
		}
	});
}

function checkConfirmPw() {
	$('[name="repassword"]').blur(function() {
  		var repassword = $('[name="repassword"]').val();
		if (showNullMessage(repassword, "确认密码不能为空！")) return;
		hideMessage("确认密码不能为空！");

		checkPassword();
		var password = $('[name="password"]').val();
		if (password != repassword) {
			showMessage("两次密码不匹配！");
			return;
		}
		hideMessage("两次密码不匹配！");

		repasswdOk = true;
	});
}

function checkFile() {
	$('[name="avatar"]').blur(function() {
		var filename = $('[name="avatar"]').val();
		if (showNullMessage(filename, "请选择头像！")) return;
		hideMessage("请选择头像！");

		fileOk = true;
	});
}


// show message if value is null.
function showNullMessage(value, message) {
	if (value == null || value == "") {
		showMessage(message);
		return true;
	}
	return false;
}

// show message
function showMessage(message) {
	$("#error-message").text(message);
	$("#alert-warning .alert").show("slow");
}

// hide
function hideMessage(message) {
	if (message == $("#error-message").text()) {
		$("#alert-warning .alert").hide("slow");
	}
}