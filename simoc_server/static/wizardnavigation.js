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
        var obj = {'mode':'.','launch_date':'.','duration_days':'.','payload':'.','location':'.','region':'.','regolith':'.'}; 

            postFormatted('/test_route', obj, function (data,status) {
                
                console.log("TEST");

                if (status == 'success') {
                    alert("IT WORKED!");
                }

                else{
                    console.log("TEST");
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

