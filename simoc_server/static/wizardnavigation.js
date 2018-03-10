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

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var target = $(e.target).attr("href")
        console.log(target);
        if(target == '#finalize'){
          
          UpdateFinal();
        }
      });

      $(".finalize-step").click(function (e){
        var obj = {};

            postFormatted('/login', obj, function (data,status) {
                //alert(JSON.stringify(data+'status:'+status));
                if (status == 'success') {
                    alertForm("Login Success!", "alert-success")
                    gotourl('/gameinit');
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

function postFormatted(url, data, callback){
    return ajaxFormatted(url, data, {
        method:"POST",
        success: callback
    });
}