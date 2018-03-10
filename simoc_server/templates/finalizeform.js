$(document).ready(function(){
	
    function updateFinalize(){
        var configuration = $(document.getElementById('{{step.formid}}')).serializeArray();
        document.getElementById('row-finalize').innerHTML = "";

        for(var i=0; i< configuration.length; i++){
            console.log("TEST");
            var viewBlock ="<div class='col-12'>";

            viewBlock+=configuration[i].name + ": " + configuration[i].value + "</div>";
            document.getElementById('row-finalize').innerHTML = viewBlock;
        }

    }

    updateFinalize();
    
    $('form').change(function(){
        updateFinalize();
    })

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var target = $(e.target).attr("href")
        console.log(target);
        if(target == '#finalize'){          
            updateFinalize();
        }
    });
}

