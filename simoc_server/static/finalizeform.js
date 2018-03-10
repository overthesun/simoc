$(document).ready(function(){
	
    function updateFinalize(){
        var configuration = $(document.getElementById('wizardform')).serializeArray();
        document.getElementById('row-finalize').innerHTML = "";

        console.log(configuration.length);
        for(var i=0; i< configuration.length; i++){
            console.log(configuration[i].name + ": " + configuration[i].value);
            var viewBlock ="<div class='col-12'>";

            viewBlock +=configuration[i].name + ": " + configuration[i].value + "</div>";
            document.getElementById('row-finalize').innerHTML += viewBlock;
        }

    }

    updateFinalize();
    
    $(document.getElementById('wizardform')).change(function(){
        console.log(TEST);
        updateFinalize();
    })

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var target = $(e.target).attr("href")
        console.log(target);
        if(target == '#finalize'){          
            updateFinalize();
        }
    });
});

