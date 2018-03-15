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



    $(".finalize-step").click(function (e){

        if(document.getElementById('scientific-mode').checked){
            exportConfiguration();
        }


        var obj = {'mode':'.','launch_date':'.','duration_days':'.','payload':'.','location':'.','region':'.','regolith':'.'}; 
        postFormatted('/new_game', obj, function (data,status) {
            if (status == 'success') {
                var stateObj ={};
                history.pushState(stateObj, "SIMOC Dashboard","/dashboard");
                $('#base-container').load("/test_route");
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

