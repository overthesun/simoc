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

        if(document.getElementById('Scientific').checked){
            exportConfiguration();
        }

        else if( document.getElementById('Interactive').checked){
            var obj = {'mode':'.','launch_date':'.','duration_days':'.','payload':'.','location':'.','region':'.','regolith':'.'}; 
            postFormatted('/new_game', obj, function (data,status) {
                
                console.log("TEST");

                if (status == 'success') {
                    console.log("TEST");
                    $('.wizard-container').removeClass('d-visible');
                    $('.dashboard-container').removeClass('d-none');

                    $('.dashboard-container').addClass('d-visible');
                    $('.wizard-container').addClass('d-none');

                    paused = false;
                    intervalUpdate();
                }

            });
        }
    });
});

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}
function previousTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}

