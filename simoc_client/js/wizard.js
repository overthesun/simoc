$(document).ready(function () {
    //Initialize tooltips

    $('nav-tabs li.active a').next().removeClass('disabled');
    $('tab nav-tabs li.active a').next().addClass('active');

    $('.nav-tabs > li a[title]').tooltip();

    console.log($('nav-tabs li a.active').next().id);
    
    //Wizard
    $('.nav-tabs > li a[data-toggle="tab"]').on('show.bs.tab', function (e) {

        var $target = $(e.target);
    
        if ($target.parent().hasClass('disabled')) {            
            return false;
        }
    });

    $(".next-step").click(function (e) {
        
        var $active = $('.nav-tabs li.active');

        $active.removeClass('active');
        $active.next().removeClass('disabled');
        $active.next().addClass('active');

        console.log($active.next());
        nextTab($active);

    });
    $(".prev-step").click(function (e) {

        var $active = $('.nav-tabs li a.active');
        prevTab($active);

    });
});

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}
function prevTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}

