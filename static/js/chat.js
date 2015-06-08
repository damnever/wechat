$(document).ready(function() {
	if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    online.poll();

    $("#messageform").submit( function() {
        newMessage($(this));
        $("#message-content").animate({ scrollTop: 1E10 }, '100', "swing", function() {
        	$('#first-field').focus();
    	});
        return false;
    });
    $("#messageform").on("keypress", "", function(e) {
        if (e.keyCode == 13) {
            newMessage($(this));
            $("#message-content").animate({ scrollTop: 1E10 }, '100', "swing", function() {
        		$('#first-field').focus();
    		});
            return false;
        }
    });

    $("input[type=file]").change( function () {
    	readImage(this);
    });

    updater.poll();

    switchList();
    clickUser();
});


var CURRENT_CHAT_USER = "";
var ALL_USERS = {};
var CHAT_USERS = {};
var LIST_CLICKED = "chat";


// Click user to chat.
var clickUser = function() {
	$("#other-list").on("dblclick", "a",function() {
		CURRENT_CHAT_USER = $(this).attr("id");
		console.log(CURRENT_CHAT_USER);
		var chatDialog = $("#chat-dialog");
		var chatTitle = $($("#chat-dialog div")[0]);
		if (chatTitle.text() == CURRENT_CHAT_USER) {
			return;
		}
		$("#message-content").html("");
		chatDialog.hide("slow", function() {
			chatTitle.text(CURRENT_CHAT_USER);
			chatDialog.show("slow", function() {
				if (CURRENT_CHAT_USER in CHAT_USERS) {
					CHAT_USERS[CURRENT_CHAT_USER] = 0;
					refreshUnreadNum();
				}
				// Fetch all messages
				var message = {"username": CURRENT_CHAT_USER};
				$.getJSON("/messages", message, function(response) {
					var msgs = response;
					console.log("ALL MSG: ", msgs);
					for (var i=0; i < msgs.length; i++) {
						if (msgs[i].self) {
							showMessage(msgs[i], true);
						} else {
							showMessage(msgs[i], false);
						}
					}
					$("#message-content").animate({ scrollTop: 1E10 }, '100', "swing", function() {
        				$('#first-field').focus();
    				});
				});
			});
		});
	});
}

// Switch user list.
// Multiple line string: http://javascript.ruanyifeng.com/grammar/string.html
var switchList = function() {
	var template = (function () { /*
	<a id="{0}" href="javascript:;" class="list-group-item">
	<span class="badge">{1}</span>
	<span class="user-avatar">
	<img src="data:image/jpg;base64,{2}" class="img-rounded" width="25"/>
	</span><span class="username">{3}</span><span class="sex">({4})</span>
	</a>
	*/}).toString().split('\n').slice(1,-1).join('');
	$("#chat-img").on("click", function() {
		LIST_CLICKED = "chat";
		// Get current chat users
		var html = new Array();
		var i=0;
		for (var username in CHAT_USERS) {
			var each = String.format(template,
					username, CHAT_USERS[username], ALL_USERS[username].avatar,
					username, ALL_USERS[username].sex.replace("boy","男").replace("girl", "女"));
			html[i] = each;
			i++;
		}
		$("#other-list").html(html.join(""));
	});
	$("#users-img").on("click", function() {
		LIST_CLICKED = "all";
		// get all users
		$.postJSON("/user/list", {}, function(response) {
			//var userObj = eval("(" + response + ")"); // Convert JSON to a object
			var data = JSON.parse(response);
			console.log("DATA", data);
			var html = new Array();
			for(var i = 0; i < data.length; i++) {
				var each = String.format(template, data[i].username, "",
						data[i].avatar, data[i].username,
						data[i].sex.replace("boy","男").replace("girl", "女"));
				html[i] = each;
			}
		  	$("#other-list").html(html.join(""));
		});
	});
}

var updater = {
	errorSleepTime: 500,

	poll: function() {
        var args = {"_xsrf": getCookie("_xsrf")};
        $.ajax({url: "/chat", type: "POST", dataType: "text",
                data: $.param(args), success: updater.onSuccess,
                error: updater.onError});
    },

    onSuccess: function(response) {
        try {
        	var msg = JSON.parse(response);
        	if (msg.type == "online") {
        		var user = msg.message;
        		ALL_USERS[user.username] = {sex: user.sex, avatar: user.avatar};
        		if (LIST_CLICKED == "all") {
        			appendUser(user);
        		}
        	} else if (msg.type == "outline") {
        		var username = msg.message;
        		$("#"+username).slideUp();
        		$("#"+username).remove();
        		delete ALL_USERS[username];
        		if (username in CHAT_USERS) {
        			delete CHAT_USERS[username];
        		}
        	} else if (msg.type == "message") {
        		var username = msg.message.from;
        		if (!(username in CHAT_USERS)) {
        			CHAT_USERS[username] = 0;
        		}
        		if (username != CURRENT_CHAT_USER) {
        			// If user not CURRENT_CHAT_USER, add user to CHAT_USERS
        			if (!(username in CHAT_USERS)) {
        				CHAT_USERS[username] = 1;
        			} else {
        				CHAT_USERS[username] += 1;
        			}
        			if (LIST_CLICKED == "chat") {
        				var user = {
        					username: username,
        					sex: ALL_USERS[username].sex,
        					avatar: ALL_USERS[username].avatar,
        				};
        				appendUser(user);
        			}
        			// Refresh unread num
        			refreshUnreadNum();
        		} else {
        			// Show message
        			showMessage(msg.message, false);
        		}
        	}
        } catch (e) {
            updater.onError();
            return;
        }
        updater.errorSleepTime = 500;
        window.setTimeout(updater.poll, 0);
    },

    onError: function(response) {
        updater.errorSleepTime *= 2;
        console.log("Poll error; sleeping ", updater.errorSleepTime, "ms");
        window.setTimeout(updater.poll, updater.errorSleepTime);
    },
}

// User online poll
var online = {
    errorSleepTime: 500,

    poll: function() {
        var args = {"_xsrf": getCookie("_xsrf")};
        $.ajax({url: "/user/live", type: "POST", dataType: "text",
            data: $.param(args), success: online.onSuccess,
            error: online.onError
        });
    },

    onSuccess: function(response) {
        online.errorSleepTime = 500;
        // window.setTimeout(online.poll, 0);
    },

    onError: function(response) {
        online.errorSleepTime *= 2;
        window.setTimeout(online.poll, online.errorSleepTime);
    }
};

// New message
function newMessage(form) {
    var text = form.find('input[name="text"]').val();
    var picture = $('#placeholder').text();
    $('#placeholder').text("");
    $(":file").filestyle('clear');
    if (text == "" && picture == "") return;
    var username = $(".title").text();
    var message = {"text": text, "picture": picture, "to": username};
    console.log("MESSAGE:", message);
    var disabled = form.find("input[type=submit]");
    disabled.disable();
    // show message
    showMessage(message, true);
    $.postJSON("/messages", message, function(response) {
        console.log("MSG RESP:", response);
        form.find('input[name="text"]').val("").select();
        disabled.enable();
    });
}

// Show message
function showMessage(message, self) {
	var tpl = "";
	if (self) {
		tpl = "<div class=\"message self\">{0}</div>";
	} else {
		tpl = "<div class=\"message other\">{0}</div>";
	}
	var content = $("#message-content");
	if (message.text != "") {
		var node = $(String.format(tpl, message.text));
		node.hide();
		content.append(node);
		node.slideDown();
	}
	if (message.picture != "") {
		var node = $(String.format(tpl, "<img src=\"" + message.picture + "\" width=\"200\"/>"));
		node.hide();
		content.append(node);
		node.slideDown();
	}
	//content.scrollTop = content.scrollHeight;
}

// Append user
function appendUser(user) {
	var template = (function () { /*
	<a id="{0}" href="javascript:;" class="list-group-item">
	<span class="badge">{1}</span>
	<span class="user-avatar">
	<img src="data:image/jpg;base64,{2}" class="img-rounded" width="25"/>
	</span><span class="username">{3}</span><span class="sex">({4})</span>
	</a>
	*/}).toString().split('\n').slice(1,-1).join('');
	var append = true;
	$("#other-list a").each(function() {
		if ($(this).attr("id") == user.username) {
			append = false;
		}
	});
	if (append) {
		var node = $(String.format(template,
				user.username, "", user.avatar, user.username,
				user.sex.replace("boy","男").replace("girl", "女")));
		node.hide();
		$("#other-list").append(node);
		node.slideDown();
	}
}

function refreshUnreadNum() {
	$("#other-list a").each(function( index ) {
		var username = $(this).attr("id");
		if ((username in CHAT_USERS && CHAT_USERS[username] != 0)) {
			$(this).find('[class="badge"]').text(CHAT_USERS[username]);
		} else {
			$(this).find('[class="badge"]').text("");
		}
	});
}

// Encode image to base64 string
// http://jsbin.com/ayazin/2/edit?html,css,js,output
function readImage(input) {
    if ( input.files && input.files[0] ) {
        var fr = new FileReader();
        fr.onload = function(e) {
        	$('#placeholder').text( e.target.result );
        };       
        fr.readAsDataURL( input.files[0] );
    }
}

// Format string
// http://witmax.cn/js-function-string-format.html
String.format = function(src){
    if (arguments.length == 0) return null;
    var args = Array.prototype.slice.call(arguments, 1);
    return src.replace(/\{(\d+)\}/g, function(m, i){
        return args[i];
    });
};