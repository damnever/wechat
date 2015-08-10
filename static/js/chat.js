$(document).ready(function() {
	if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    online.poll();
    getAllUsers();

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


var ROBOT_AVATAR = (function () { /*
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
*/}).toString().split('\n').slice(1,-1).join('');
var TEMPLATE = (function () { /*
    <a id="{0}" href="javascript:;" class="list-group-item">
    <span class="badge">{1}</span>
    <span class="user-avatar">
    <img src="data:image/jpg;base64,{2}" class="img-rounded" width="25"/>
    </span><span class="username">{3}</span><span class="sex">({4})</span>
    </a>
    */}).toString().split('\n').slice(1,-1).join('');
var CURRENT_CHAT_USER = "";
var ALL_USERS = {"Robot": {sex: "不明", avatar: ROBOT_AVATAR}};
var CHAT_USERS = {};
var LIST_CLICKED = "all";


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
	$("#chat-img").on("click", function() {
		LIST_CLICKED = "chat";
		// Get current chat users
		var html = new Array();
		var i=0;
		for (var username in CHAT_USERS) {
			var each = String.format(TEMPLATE,
					username, CHAT_USERS[username], ALL_USERS[username].avatar,
					username, ALL_USERS[username].sex.replace("boy","男").replace("girl", "女"));
			html[i] = each;
			i++;
		}
		$("#other-list").html(html.join(""));
	});
	$("#users-img").on("click", function() {
		LIST_CLICKED = "all";
		getAllUsers();
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
                        var user;
                        if (username == 'Robot') {
                            user = {
                                username: username,
                                sex: "不明",
                                avatar: ROBOT_AVATAR,
                            };
                        } else {
            				user = {
            					username: username,
            					sex: ALL_USERS[username].sex,
            					avatar: ALL_USERS[username].avatar,
            				};
                        }
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

// Get all users.
function getAllUsers() {
    $.get("/user/list", {}, function(response) {
        //var userObj = eval("(" + response + ")"); // Convert JSON to a object
        var data = JSON.parse(response);
        console.log("DATA", data);
        var html = new Array();
        html[0] = String.format(TEMPLATE, "Robot", "",
                    ROBOT_AVATAR, "Robot", "不明");
        for(var i = 0; i < data.length; i++) {
            ALL_USERS[data[i].username] = {
                sex: data[i].sex,
                avatar: data[i].avatar
            };
            var each = String.format(TEMPLATE, data[i].username, "",
                    data[i].avatar, data[i].username,
                    data[i].sex.replace("boy","男").replace("girl", "女"));
            html[i+1] = each;
        }
        $("#other-list").html(html.join(""));
    });
}

// New message
function newMessage(form) {
    var text = form.find('input[name="text"]').val();
    var picture = $('#placeholder').text();
    $('#placeholder').text("");
    $(":file").filestyle('clear');
    if (text == "" && picture == "") return;
    var username = $(".title").text();
    var message = {"text": text, "picture": picture, "to": username};
    var url = "/messages";
    // Robot
    if (username == "Robot") {
        url = "/robot";
    }
    var disabled = form.find("input[type=submit]");
    disabled.disable();
    // show message
    showMessage(message, true);
    $.postJSON(url, message, function(response) {
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