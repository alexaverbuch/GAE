$(document).ready(function() {
	ajax();
	$("a").addClass("test");
	$("#orderedlist > li").addClass("blue");
	$("#orderedlist li:last").hover(function() {
		$(this).addClass("green");
	}, function() {
		$(this).removeClass("green");
	});
	$("#orderedlist").find("li").each(function(i) {
		$(this).append(" BAM! " + i);
	});
	$("#reset").click(function() {
		$("form")[0].reset();
	});
	$("a").click(function(event) {
		// alert("As you can see, the link no longer took you to jquery.com");
			// event.preventDefault();
			// $(this).hide("slow");
		});
});

function ajax() {
	// generate markup
	$("#rating").append("Please rate: ");

	for ( var i = 1; i <= 5; i++) {
		$("#rating").append("<a href='#'>" + i + "</a> ");
	}

	// add markup to container and apply click handlers to anchors
	$("#rating a").click(function(e) {
		// stop normal link click
			e.preventDefault();

			alert($(this).html());

			// send request
			$.post("rate.php", {
				rating : $(this).html()
			}, function(xml) {
				// format and output result
					$("#rating").html(
							"Thanks for rating, current average: "
									+ $("average", xml).text()
									+ ", number of votes: "
									+ $("count", xml).text());
				});
		});
};