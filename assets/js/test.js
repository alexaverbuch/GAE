function clearFunction(text) {
	// notice lack of "var"
	plus = " plus extra text " + Date();
	document.write(text + plus);
}

function alertFunction() {
	alert("I am an alert box!");
}

function confirmFunction() {
	message = confirm("Press a button") ? "You pressed OK!"
			: "You pressed Cancel!";
	alert(message);
}

function promptFunction() {
	var name = prompt("Please enter a value", "default value");
	if (name != null && name != "")
		document.write("<p>Value is " + name + "!</p>");
}

function checkInput() {
	var r = new RegExp("^[\\S]+@[\\S]+\\.[\\S]+$");
	if (r.test(document.getElementById("input").value)) {
		document.getElementById("input_error").color = "green";
		document.getElementById("input_error").innerHTML = "valid email";
	} else {
		document.getElementById("input_error").color = "red";
		document.getElementById("input_error").innerHTML = "invalid email";
	}
};

function exceptionMessage() {
	try {
		adddlert("Welcome guest!");
	} catch (err) {
		txt = "There was an error on this page.\n\n";
		txt += "Error description: " + err.message + "\n\n";
		txt += "Click OK to continue.\n\n";
		alert(txt);
	}
};

function throwException() {
	var x = prompt("Enter a number between 5 and 10:", "");
	try {
		if (x > 10) {
			throw "Err1";
		} else if (x < 5) {
			throw "Err2";
		} else if (isNaN(x)) {
			throw "Err3";
		}
	} catch (err) {
		if (err == "Err1") {
			document.write("Error! The value is too high.");
		}
		if (err == "Err2") {
			document.write("Error! The value is too low.");
		}
		if (err == "Err3") {
			document.write("Error! The value is not a number.");
		}
	}
};

function startTime() {
	var today = new Date();
	var h = today.getHours();
	var m = today.getMinutes();
	var s = today.getSeconds();
	// add a zero in front of numbers<10
	m = checkTime(m);
	s = checkTime(s);
	document.getElementById('txt').innerHTML = h + ":" + m + ":" + s;
	// t only needed if timer needs to be aborted/interrupted, i think
	// t = setTimeout('startTime()', 500);
	setTimeout('startTime()', 500);
};

function checkTime(i) {
	if (i < 10) {
		i = "0" + i;
	}
	return i;
};

function setCookie(c_name, value, exdays) {
	var exdate = new Date();
	exdate.setDate(exdate.getDate() + exdays);
	var c_value = escape(value)
			+ ((exdays == null) ? "" : "; expires=" + exdate.toUTCString());
	// alert(c_name + "=" + c_value);
	// Does not seem to work
	document.cookie = c_name + "=" + c_value;
	// alert(getCookie(c_name));
};

function getCookie(c_name) {
	var i, x, y, ARRcookies = document.cookie.split(";");
	for (i = 0; i < ARRcookies.length; i++) {
		x = ARRcookies[i].substr(0, ARRcookies[i].indexOf("="));
		y = ARRcookies[i].substr(ARRcookies[i].indexOf("=") + 1);
		x = x.replace(/^\s+|\s+$/g, "");
		if (x == c_name) {
			return unescape(y);
		}
	}
};

function checkCookie() {
	var username = getCookie("username");
	if (username != null && username != "") {
		alert("Welcome again " + username);
	} else {
		username = prompt("Please enter your name:", "");
		if (username != null && username != "") {
			setCookie("username", username, 365);
		}
	}
};
