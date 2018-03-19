$(document).ready(function () {
    $(".next-step").click(function (e) {

        var $active = $('ul li a.active').parent();
        $active.next().find('a[data-toggle="tab"]').removeClass('disabled');
        nextTab($active);
    });

    $(".previous-step").click(function (e) {
        var $active = $('ul li a.active').parent();
        previousTab($active);
    });


    $(".cancel-step").click(function(e){
        e.preventDefault();
        $('ul li a:first').tab('show');
    });


    $(".finalize-step").click(function (e){

        if(document.getElementById('scientific-mode').checked){
            exportConfiguration();
        }


        var obj = {'mode':'.','launch_date':'.','duration_days':'.','payload':'.','location':'.','region':'.','regolith':'.'}; 
        postFormatted('/new_game', obj, function (data,status) {
            if (status == 'success') {
                var obj = {};                
                //history.pushState(obj, "SIMOC Dashboard","/dashboard");
                $('#base-container').load("/test_route",function(){
                    $.getScript('/static/js/dashboardInitialize.js');
                    $.getScript('/static/js/dashChartBar.js');
                    $.getScript('/static/js/updateInterval.js');
                    //$.getScript('/static/css/text.css');
                });
            }
        });
        
    });

});

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}
function previousTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}

