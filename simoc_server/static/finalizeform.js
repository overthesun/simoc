$(document).ready(function(){
    
    function updateFinalize(){
        document.getElementById('row-finalize').innerHTML = "";

        console.log(document.forms)
        var configuration = document.getElementById('wizardform');

        console.log(configuration.length);;
        for(var i=0; i< configuration.length; i++){
            if(configuration[i].type =='hidden' || configuration[i].type =='select-one' || configuration[i].type == 'number')
                document.getElementById('row-finalize').innerHTML += "<div class='col-6'>" + configuration[i].value + ':' + '</div>';

            if(configuration[i].type =='radio' || configuration[i].type =='check'){
                if(configuration[i].checked){
                    console.log(document.getElementById(String(configuration[i].id)).value);
                    document.getElementById('row-finalize').innerHTML += "<div class='col-6'>" + document.getElementById(String(configuration[i].id)).value + ':' + '</div>';
                }
            }

        }
        /*



        
        console.log(configuration);
        for(var i=0; i< configuration.length; i++){
            
            var viewBlock ="<div class='col-12'>";
            
            viewBlock+=configuration[i].name + ": " + configuration[i].value + "</div>";
            document.getElementById('row-finalize').innerHTML += viewBlock;
        }*/

    }

    updateFinalize();
    
    $('form').change(function(){
        updateFinalize();
    })

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var target = $(e.target).attr("href")
        if(target == '#finalize'){    
            updateFinalize();
        }
    });
});

