function startTime()
{
var today=new Date();
var h=today.getHours();
var m=today.getMinutes();
var s=today.getSeconds();

// add a zero in front of numbers<10
if (h<10) {
    h = '0' + h;
}

m=checkTime(m);
s=checkTime(s);
document.getElementById('time-clock').innerHTML=h+":"+m+":"+s;
t=setTimeout('startTime()',500);
}
function checkTime(i)
{
if (i<10)
{
i="0" + i;
}
return i;
}

$('form').submit(function(e) {
    e.preventDefault();
    var sticker_no = $("#plate_no").val()
    $.post('/authenticate',{sticker_no:sticker_no},
    function(data){
    $('#current-panel .panel-body').html(data);
    $("#plate_no").val('');
    });

    add_log(sticker_no);
});

function add_log(sticker_no){
    $.post('/addlog',{sticker_no:sticker_no},
    function(data){
    $('#log-table tbody').html(data);
    });
}