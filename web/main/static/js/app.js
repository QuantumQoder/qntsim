var currentTab;
var pages = 9;
var nodes = [];

$(document).ready(function () {
	currentTab = 0; // Current tab is set to be the first tab (0)
	showTab(currentTab); // Display the current tab
	fixButtons(currentTab);
	fixStepIndicator(currentTab);
	// $("#prevBtn").hide();
	$(".addRow").click(function (e) { 
		e.preventDefault();
		addRow($(this.parentElement).children("table")[0].id);
	});
	// $("#submit").click(function () {
	//     var top_file = $('#topology').val();
	//     loadTopology(top_file);
	// });
});

function deleteRow(row) {
	$(row.parentElement.parentElement).remove();
}

function addRow(tableID) {
	console.log(`Adding row to table: ${tableID}`);
	// console.log(nodes);
	// var noOfCols = $(`#${tableID}`).find("th").length;
	var HTML = `<tr>`;
	var nodeOptsHTML = '';
	nodes.forEach(node => {
		nodeOptsHTML += `<option value="${node}">${node}</option>`;
	});
	
	switch(tableID){
		case "nodes":
			HTML += `<td><input type="text" name="nodeName"></td>
					<td><select name="nodeType"><option value="service" default>Service</option><option value="end">End</option></select></td>
					<td><input type="text" name="nodeNoMemories" value="50"></td>
					<td><input type="text" name="nodeMemoFreq" value="2e4"></td>
					<td><input type="text" name="nodeMemoExpiry" value="0"></td>
					<td><input type="text" name="nodeMemoEfficiency" value="1"></td>
					<td><input type="text" name="nodeMemoFidelity" value="0.93"></td>`;
			break;
		case "qc" :
			HTML += `<td><select name="qcNode1">${nodeOptsHTML}</select></td>
					<td><select name="qcNode2">${nodeOptsHTML}</select></td>
					<td><input type="text" name="qcAttenuation" value="1e-5"></td>
					<td><input type="text" name="qcDistance" value="70"></td>`;
				break;
		case "vc" :
			HTML += `<td><select name="vcNode1">${nodeOptsHTML}</select></td>
					<td><select name="vcNode2">${nodeOptsHTML}</select></td>
					<td><input type="text" name="vcDemandSize" value="50"></td>`
				break;
	}

	HTML += `<td><button type="button" class="deleteRow" onclick="deleteRow(this)">Delete Node</button></td></tr>`;

	$(`#${tableID}`).append(HTML);
}

function fetchTopologyGraph(){
	console.log("Fetching topology graph");
	var serviceNodes = [];
	var endNodes = [];

	console.log(`Visualising Topology`);
	// Selecting the iframe element
	// var frame = document.getElementById("topoGraphFrame");
          
	// // Adjusting the iframe height onload event
	// frame.onload = function()
	// // function execute while load the iframe
	// {
	//   // set the height of the iframe as 
	//   // the height of the iframe content
	//   frame.style.height = 
	//   frame.contentWindow.document.body.scrollHeight + 'px';
	   

	//  // set the width of the iframe as the 
	//  // width of the iframe content
	//  frame.style.width  = 
	//   frame.contentWindow.document.body.scrollWidth+'px';
		  
	// }
	// $("#topoGraph").load("graph");

	// $.ajax({
	// 	type: "GET",
	// 	url: "graph",
	// 	data: {
	// 		topology: "3node.json",
	// 	},
	// 	async: false,
	// 	success: function (response) {
	// 		$("#topoGraph").load(main/graph);
	// 	}
	// });

	// $(this.parentElement).children("table")[0]
	// console.log($(`#nodes select[name="nodeType"]`));
	// $(`#nodes select[name="nodeType"]`).each(function() {
	// 	if($(this).val() == "service"){
	// 		console.log($(this.parentElement.parentElement));
	// 		// serviceNodes.append();
	// 	} else if($(this).val() == "end"){
	// 		console.log($(this.parentElement));
	// 	} else {
	// 		console.log(`Error - Wrong type passed: ${$(this).val()}`);
	// 		$("#error").text(`Wrong type passed: ${$(this).val()}`);
	// 	}
	// });
	// var topologyConfig = {
	// 	"service_node": ,
	// 	"end_node":{"a":"s1",
	// 			"b":"s2"},
		
	// 	"qconnections": [
			
	// 		{
	// 			"node1": "a",
	// 			"node2": "s1",
	// 			"attenuation": 1e-5,
	// 			"distance": 70
	// 		},
	// 		{
	// 			"node1": "s1",
	// 			"node2": "s2",
	// 			"attenuation": 1e-5,
	// 			"distance": 70
	// 		},
	// 		{
	// 			"node1": "s2",
	// 			"node2": "b",
	// 			"attenuation": 1e-5,
	// 			"distance": 70
	// 		}             
	// 	],
	// 	"cchannels_table": {
	// 		"type": "RT",
	// 		"labels": ["a", "s1", "s2","b"],
	// 		"table": [[0,   1e9, 1e9,1e9],
	// 				  [1e9, 0,   1e9,1e9],
	// 				  [1e9, 1e9, 0,1e9],
	// 				  [1e9, 1e9, 1e9, 0]
	// 				  ]          
	// 	}
	// };
}

function createCCTable() {
	$(`#cc`).empty();
	console.log("Create Classical Connections Table");
	var HTML = `<tr><td></td>`;
	nodes.forEach(node => {
		HTML += `<td>${node}</td>`;
	});
	HTML += `</tr>`;
	nodes.forEach(node => {
		HTML += `<tr><td>${node}</td>`;
		nodes.forEach(node2 => {
			if(node == node2){
				HTML += `<td>0</td>`;
			} else {
				HTML += `<td><input type="text" name="ccDelay" value="0.5"></td>`;
			}
		});
		HTML += `</tr>`;
	});
	$(`#cc`).html(HTML);
}

function fetchAppOptions() {
	var HTML = ``;
	nodes.forEach(node => {
		HTML += `<option value="${node}">${node}</option>`;
	});
	$("#sender").html(HTML);
	$("#receiver").html(HTML);
}

function fetchLogs(){
	var last_response_len = false;
	$.ajax('appLog', {
		xhrFields: {
			onprogress: function(e)
			{
				var this_response, response = e.currentTarget.response;
				if(last_response_len === false)
				{
					this_response = response;
					last_response_len = response.length;
				}
				else
				{
					this_response = response.substring(last_response_len);
					last_response_len = response.length;
				}
				$("#appLogs").append(this_response);
			}
		}
	})
	.done(function(data)
	{
		console.log('Complete response = ' + data);
	})
	.fail(function(data)
	{
		console.log('Error: ', data);
	});
	console.log('Request Sent');
}

function showTab(n) {
	$(`div.tab:nth-child(${n+1})`).show();
	
	switch(n) {
		case 0:
			
			break;
		case 1:
			nodes = $(`#nodes input[name=nodeName]`).map(function() {
				console.log($(this).val());
				return $(this).val();
			}).get();
			break;
		case 2:
			break;
		case 3:
			createCCTable();
			break;
		case 4:
			fetchTopologyGraph();
			break;
		case 5:
			fetchAppOptions();
			break;
		case 6:
			fetchLogs();
			break;
		case 7:
			
			break;
	}
}

function validate(currentTab){
	return true;

	// TODO: Check if empty
	// var x, y, i, valid = true;
	// x = document.getElementsByClassName("tab");
	// y = x[currentTab].getElementsByTagName("input");
	// // A loop that checks every input field in the current tab:
	// for (i = 0; i < y.length; i++) {
	//   // If a field is empty...
	//   if (y[i].value == "") {
	// 	// add an "invalid" class to the field:
	// 	y[i].className += " invalid";
	// 	// and set the current valid status to false:
	// 	valid = false;
	//   }
	// }
	// // If the valid status is true, mark the step as finished and valid:
	// if (valid) {
	//   document.getElementsByClassName("step")[currentTab].className += " finish";
	// }
	// return valid; // return the valid status

	// switch(currentTab) {
	// 	case 0:
	// 		var tempNodes = [];
	// 		$("#nodes input[name='nodeName']").each(function (index, element) { 
	// 			tempNodes.push($(element).val());
	// 		});
	// 		//Nodes cannot be null
	// 		nodes = tempNodes;
	// 		break;
	// 	case 1:
	// 		break;
	// 	case 2:
	// 		break;
	// 	case 3:
	// 		break;
	// 	case 4:
	// 		break;
	// 	case 5:
	// 		break;
	// 	case 6:
	// 		break;
	// }
}

function nextPrev(n) {
	var validation = validate(currentTab);
	// Validate if we can proceed to next tab
	if(validation === true){
		// Hide previous tab and show next one
		$(`div.tab:nth-child(${currentTab+1})`).hide();
		currentTab = currentTab + n;
		console.log("New Tab: " + currentTab);
		showTab(currentTab);

		// ... and run a function that displays the correct step indicator:
		fixStepIndicator(currentTab)
		fixButtons(currentTab);	
	}else{
		// Display error message if validations fail
		$("#error").text = validation;
		return ;
	}
}
 
function fixStepIndicator(n) {
	console.log(`Fixing Step Indicator: ${n}`);

	  // This function removes the "active" class of all steps...
	  var i, x = document.getElementsByClassName("step");
	//   console.log(x);
	//   console.log(n);
	for (i = 0; i < x.length; i++) {
	  x[i].className = x[i].className.replace(" active", "");
	}
	//... and adds the "active" class to the current step:
	x[n].className += " active";
}

function fixButtons(n){
	console.log(`Fixing Buttons ${n}`);
	//Set the Buttons
	if (n == 0) {
		$("#prevBtn").hide();
	} else {
		$("#prevBtn").show();
	}
	if (n == (pages - 1)) {
		$("#nextBtn").hide();
	} else {
		$("#nextBtn").show();
	}
}