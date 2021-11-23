function update() {
	document.getElementById("components-list-table").innerHTML = ""

	const columns = ["name", "topic", "type", "remove"]
	const headerRow = document.createElement("tr")
	columns.forEach(k => {
		const th = document.createElement("th")
		const p = document.createElement("p")
		
		p.innerText = k.charAt(0).toUpperCase() + k.slice(1).toLowerCase()

		th.appendChild(p)
		headerRow.appendChild(th)
	})
	const th = document.createElement("th")
	document.getElementById("components-list-table").appendChild(headerRow)

	// Remove "remove" :)
	columns.pop()

	const components = localStorage.getItem("components")
	
	if (components == undefined) { return }

	function createRow(component, i) {
		const tr = document.createElement("tr")
		
		columns.forEach(k => {
			const td = document.createElement("td")
			const p = document.createElement("p")
			
			p.innerText = component[k]

			td.appendChild(p)
			tr.appendChild(td)
		})

		const removeTd = document.createElement("td")
		const removeButton = document.createElement("button")

		removeButton.innerText = "Remove"
		removeButton.name
		removeButton.onclick = function () {remove(i)}

		removeTd.appendChild(removeButton)
		tr.appendChild(removeTd)
		
		return tr
	}

	var i = 0
	JSON.parse(components).forEach(component => {
		document.getElementById("components-list-table").appendChild(createRow(component, i))

		i += 1
	})
}

function remove(index) {
	const components = JSON.parse(localStorage.getItem("components"))
	components.splice(index, 1)

	localStorage.setItem("components", JSON.stringify(components))

	update()
}

function add() {
	const name = document.getElementById("name-input").value
	const topic = document.getElementById("topic-input").value
	const type = document.getElementById("type-input").value

	document.getElementById("name-input").value = ""
	document.getElementById("topic-input").value = ""

	var componentsRaw = localStorage.getItem("components")

	if (componentsRaw == undefined) { componentsRaw = "[]" }

	const components = JSON.parse(componentsRaw)
	components.push({"name": name, "topic": topic, "type": type})
	localStorage.setItem("components", JSON.stringify(components))
	
	update()
}

update()