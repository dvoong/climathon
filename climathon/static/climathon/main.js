console.log("main.js");

submit_form = function(type){
    console.log("type: " + type);
    var max_dist = $("#parameters-form input[name='max-dist']").val();
    var n_days = $("#parameters-form input[name='n-days']").val();
    if(type == "postcode"){
	var url = 'postcode-search';
	var postcode = $("#postcode-form input[name='postcode']").val();
	var data = 'postcode=' + postcode + '&max-dist=' + max_dist + '&n-days=' + n_days;
    }
    else if(type == "lng-lat"){
	var url = 'lng-lat-search';
	var lng = $("#lng-lat-form input[name='lng']").val();
	var lat = $("#lng-lat-form input[name='lat']").val();
	var data = 'lng=' + lng + '&lat=' + lat + '&max-dist=' + max_dist + '&n-days=' + n_days;
    }
    
    // Get data
    $.ajax({type: 'GET',
	    url: url,
	    data: data,
	    async: false,
	    success: function(response){
		console.log("got some data");
		console.log(response);
		var data = response.avg_data.avg_no2;
		var postcode = response.location.postcode;
		var latitude = response.location.latitude;
		var longitude = response.location.longitude;
		var dates = []
		for(i=0; i<data.length; i++){
		    dates.push(data[i].date);
		}

		$(".chart").remove();
		$("h2").remove();
		$('ul').remove();
		$('h3').remove();

		var h2 = $(document.createElement("h2"));
		$("body").append(h2);
		if(postcode != undefined)
		    h2.text("Postcode: " + postcode + " (lng: " + longitude + ", lat: " + latitude + ")");
		else
		    h2.text("lng: " + longitude + ", lat: " + latitude);
		var extra_info = $(document.createElement("h3"));
		extra_info.text("Nearby air quality sites (Within " + max_dist + " km)");
		extra_info.insertAfter($("h2"));
		var list = $(document.createElement("ul"));
		for(i=0; i<response.sites.length; i++){
		    var item = $(document.createElement("li"));
		    item.text(response.sites[i].site_name);
		    list.append(item);
		}
		list.insertAfter(extra_info);
		
		var margin = {top: 20, right: 30, bottom: 100, left: 40},
		width = 960 - margin.left - margin.right,
		height = 500 - margin.top - margin.bottom;		
		
		console.log(dates);
		var x = d3.scale.ordinal()
		    .domain(dates)
		    .rangeRoundBands([0, width], .1);
		
		var y = d3.scale.linear()
		    .domain([0, d3.max(data, function(d) { return d.avg_no2; })])
		    .range([height, 0]);
		
		var xAxis = d3.svg.axis()
		    .scale(x)
		    .orient("bottom");
		
		var yAxis = d3.svg.axis()
		    .scale(y)
		    .orient("left")
		    .ticks(10);
		
		var chart = d3.select("body").append("svg")
		    .attr("class", "chart")
		    .attr("width", width + margin.left + margin.right)
		    .attr("height", height + margin.top + margin.bottom)
		    .append("g")
		    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

		chart.append("g")
		    .attr("class", "x axis")
		    .attr("transform", "translate(0," + height + ")")
		    .call(xAxis)
		    .selectAll("text")
		    .attr("y", 0)
		    .attr("x", 9)
		    .attr("dy", ".35em")
		    .attr("transform", "rotate(90)")
		    .style("text-anchor", "start");
		
		chart.append("g")
		    .attr("class", "y axis")
		    .call(yAxis)
		    .append("text")
		    .attr("transform", "rotate(-90)")
		    .attr("y", 6)
		    .attr("dy", ".71em")
		    // .attr("dx", "15em")
		    .style("text-anchor", "end")
		    .text("Average NO2 Air Quality Index");

		chart.selectAll(".bar")
		    .data(data)
		    .enter().append("rect")
		    .attr("class", "bar")
		    .attr("x", function(d) { return x(d.date); })
		    .attr("y", function(d) { return y(d.avg_no2); })
		    .attr("height", function(d) { return height - y(d.avg_no2); })
		    .attr("width", x.rangeBand());
		
		var chart_j = $("svg:last");
		var bars = chart_j.find(".bar").filter(function(){
		    return $(this).attr("height") <= height - y(2);
		});
		bars.css("fill", "#00CC00");
		
		var bars = chart_j.find(".bar").filter(function(){
		    return $(this).attr("height") > height - y(2) && $(this).attr("height") <= height - y(3);
		});
		bars.css("fill", "#FFCC00");
		
		var bars = chart_j.find(".bar").filter(function(){
		    return $(this).attr("height") > height - y(3);
		});
		bars.css("fill", "red");

		for(i=0; i<response.sites.length; i++){
		    var data = response.sites[i].daily_no2_index;
		    var h2 = $(document.createElement("h2"));
		    h2.text(response.sites[i].site_name + " (" + response.sites[i].site_distance + " km, Lng: " + response.sites[i].site_longitude + ", Lat: " + response.sites[i].site_latitude + ")");
		    $("body").append(h2)
		    var y = d3.scale.linear()
			.domain([0, d3.max(data, function(d) { return d.no2_index; })])
			.range([height, 0]);
		    var yAxis = d3.svg.axis()
			.scale(y)
			.orient("left")
			.ticks(10);
		    var chart = d3.select("body").append("svg")
			.attr("class", "chart")
			.attr("width", width + margin.left + margin.right)
			.attr("height", height + margin.top + margin.bottom)
			.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
		    chart.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height + ")")
			.call(xAxis)
			.selectAll("text")
			.attr("y", 0)
			.attr("x", 9)
			.attr("dy", ".35em")
			.attr("transform", "rotate(90)")
			.style("text-anchor", "start");
		    
		chart.append("g")
			.attr("class", "y axis")
			.call(yAxis)
			.append("text")
			.attr("transform", "rotate(-90)")
			.attr("y", 6)
			.attr("dy", ".71em")
		    // .attr("dx", "15em")
			.style("text-anchor", "end")
			.text("NO2 Air Quality Index");

		    chart.selectAll(".bar")
		    	.data(data)
		    	.enter().append("rect")
		    	.attr("class", "bar")
		    	.attr("x", function(d) { return x(d.date); })
		    	.attr("y", function(d) { return d.no2_index != undefined ? y(d.no2_index) : undefined; })
		    	.attr("height", function(d) { return d.no2_index != undefined ? height - y(d.no2_index) : undefined; })
		    	.attr("width", x.rangeBand());

		    var chart = $("svg:last");
		    var bars = chart.find(".bar").filter(function(){
		    	return $(this).attr("height") <= height - y(2);
		    });
		    bars.css("fill", "#00CC00");

		    var bars = chart.find(".bar").filter(function(){
			return $(this).attr("height") > height - y(2) && $(this).attr("height") <= height - y(3);
		    });
		    bars.css("fill", "#FFCC00");

		    var bars = chart.find(".bar").filter(function(){
			return $(this).attr("height") > height - y(3);
		    });
		    bars.css("fill", "red");
		    
		}
		
	    },
	   });
};


$(document).ready(function(){
    console.log("document ready");

    var postcode = "nw80sg";
    var max_dist = 4.;
    var n_days = 50;
    
    $("#postcode-form button").click(function(e){
	submit_form("postcode");
    });
    $("#lng-lat-form button").click(function(e){
	submit_form("lng-lat");
    });
});

function checkUsernameValidity(username) {
    if(username == "")
        return false;
    var output = ($.ajax({
        type: 'GET',
        url: 'check-username-validity/' + username,
        async: false,
    }).responseText == "0");
    return output;
}

		
		    
	   // 	    var barWidth = width / data.length;
		    
	   // 	    var bar = chart.selectAll("g")
	   // 		.data(data)
	   // 		.enter().append("g")
	   // 		.attr("transform", function(d, i) { return "translate(" + i * barWidth + ",0)"; });
		    
	   // 	    bar.append("rect")
	   // 		.attr("y", function(d) { return y(d.value); })
	   // 		.attr("height", function(d) { return height - y(d.value); })
	   // 		.attr("width", barWidth - 1);
		    
	   // 	    bar.append("text")
	   // 		.attr("x", barWidth / 2)
	   // 		.attr("y", function(d) { return y(d.value) + 3; })
	   // 		.attr("dy", ".75em")
	   // 		.text(function(d) { return d.value; });
	   // 	});
		
	   // 	function type(d) {
	   // 	    d.value = +d.value; // coerce to number
	   // 	    return d;
	   // 	}
	   //  },
