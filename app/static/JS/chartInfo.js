$(document).ready(function(){
	$('#pieInfo').click(function(){
		showdiv($(this).attr('id'));
	});
	$('#histogramInfo').click(function(){
		showdiv($(this).attr('id'));
	});
	$('.title').click(function(){
		hidediv();
	});
});
function showdiv(id) {            
	document.getElementById("back").style.display = "block";
	if(id == "pieInfo"){
		document.getElementById("small").style.display = "block";

	}else if(id == "histogramInfo"){
		document.getElementById("awardNumber").style.display = "block";
	}
}
function hidediv() {
	document.getElementById("back").style.display = 'none';
	document.getElementById("small").style.display = "none";
	document.getElementById("awardNumber").style.display = "none";
}