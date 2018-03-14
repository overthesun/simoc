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

            console.log("TEST");
            var obj = {'mode':'.','launch_date':'.','duration_days':'.','payload':'.','location':'.','region':'.','regolith':'.'}; 
            postFormatted('/new_game', obj, function (data,status) {
                
                

                if (status == 'success') {
                    var stateObj = {} // Use this to pass in the form data.
                    window.history.pushState(stateObj,'SIMOC Dashboard',"dashboard.html"); //Dashboard route will just call current session
                    //Logic for replacing div with dashboard div.
                    $('#base-container').load(obj);
                    console.log("TEST");
                    paused = false;
                    intervalUpdate(); // Change this to somewhere else?

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

