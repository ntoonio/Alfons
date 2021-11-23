function mqttPublish(topic, payload) {
	var xhr = new XMLHttpRequest()

	xhr.onreadystatechange = function () {
		if (this.readyState != 4) return

		if (this.status >= 200 && this.status < 300) {
			var data = JSON.parse(this.responseText)
			if (data["success"] === true) {
				document.body.classList.add("flash")
				setTimeout(() => {
					document.body.classList.remove("flash")
				}, 1000)
			}
		}
	}

	xhr.open("PUT", "/api/v1/mqtt_publish/", true)
	xhr.send(JSON.stringify({
		"topic": topic,
		"payload": payload,
		"username": localStorage.getItem("username"),
		"password": localStorage.getItem("password")
	}))
}

function createActionHTML(component) {
	if (component["type"] == "onoff") {
		return "<div class='action action-onoff'><button onclick='mqttPublish(\"" + component["topic"] + "\", \"ON\")'>On</button><button onclick='mqttPublish(\"" + component["topic"] + "\", \"OFF\")'>Off</button></div>"
	}
	else {
		return "<p>Error, unknown type</p>"
	}
}

function printComponents() {
	const componentList = document.getElementById("component-list")
	componentList.innerHTML = ""

	const components = localStorage.getItem("components")
	if (components == undefined) { return }

	var i = 0
	JSON.parse(components).forEach(component => {
		const row = "<div class='row'><div class='row-name col-xl-4 col-lg-4 col-md-6 col-sm-8 col-7'><p>" + component["name"] + "</p></div><div class='row-action col-xl-8 col-lg-8 col-md-6 col-sm-4 col-5'>" + createActionHTML(component) + "</div></div>"

		componentList.innerHTML += row

		i += 1
	})
}

if (!localStorage.getItem("username") || !localStorage.getItem("password")) {
	window.location.href += "credentials/"
}

if (JSON.parse(localStorage.getItem("components") || "[]").length == 0) {
	window.location.href += "setup/"
}

printComponents()
