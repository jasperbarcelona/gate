$(document).ready(function(){

/*    $('.datepicker').datepicker()*/

    searchStatus = 'off'

    $("#plate_no").focus();

    $(".search-panel").hide();

    $("body").on('click', function() {
        $("#plate_no").focus();
    });

    $(".search-text").on('click', function() {
        $(".search-text").css("background-color","#FFFFFF");
        $(this).css("background-color","#D9D9D9");
    });

    var height = $(window).height();
    $(".container").css("height",height);
    $("tbody").css("height",height-75);
    
    $("#time").css("height",height/2);

    $(window).resize(function(){
        var height = $(window).height() ;
        $(".container").css("height",height);
        $("tbody").css("height",height-75);
        

        $("#time").css("height",height/2);
    });


    $('#search-toggle').on('click', function () {
    var $this = jQuery(this);
    if ($this.data('activated')) return false;  // Pending, return
        $this.data('activated', true);
        setTimeout(function() {
            $this.data('activated', false)
        }, 500); // Freeze for 500ms
        
    if ((typeof searchStatus === 'undefined') || (searchStatus == 'off')){
        $('.search-panel').fadeIn(300);
        searchStatus = 'on'
    }
    else{
        $('.search-panel').fadeOut(300);
        $(".search-text").css("background-color","#FFFFFF");
        searchStatus = 'off'
    }
    
});

    $('.search-text').donetyping(function(){
        search_logs()
    });

    $('.search-text').on('change', function(){
        search_logs()
    });

});