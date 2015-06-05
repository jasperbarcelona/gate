$(document).ready(function(){

/*    $('.datepicker').datepicker()*/

    $("#plate_no").focus();

    $("body").on('click', function() {
        $("#plate_no").focus();
    });

    var height = $(window).height() - 80;
    $("#log-panel .panel-body").css("height",height);
    $("#current-panel .panel-body").css("height",height/2);
    $("#time").css("height",height/2);

    $(window).resize(function(){
        var height = $(window).height() - 80;
        $("#log-panel .panel-body").css("height",height);
        $("#current-panel .panel-body").css("height",height/2);
        $("#time").css("height",height/2);
    });

});