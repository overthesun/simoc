$(document).ready(function(){
    
    function formDict(){
        var configuration = document.getElementById('wizardform');

        var dict = {};

        for(var i=0; i< configuration.length; i++){
            if(configuration[i].type =='hidden' ){
                for(var k=i+1; k<configuration.length; k++){
                    if(configuration[k].type =='radio' || configuration[k].type =='check'){
                        if(configuration[k].checked){
                            dict[configuration[i].value] = document.getElementById(String(configuration[k].id)).value;
                            break;
                        }
                    }

                    if(configuration[k].type =='select-one' || configuration[k].type == 'number'){
                        dict[configuration[i].value] = configuration[k].value;
                        break;
                    }
                }
            }        
        }
        
        return dict;
    }

    function displayDict(dict){
        
        var displayDescriptions = ['Mode','Configuration','Location','Region','Terrain','Launch Window','Duration Of Stay', 'Transportation','Payload','Model'];

        var index = 0;

        Object.keys(dict).forEach(function(key){            
            document.getElementById(key.toString()).innerHTML = displayDescriptions[index] + ": ";
            document.getElementById(key.toString()).innerHTML += dict[key].toString();
            index++;
        });
    }

    function dictToJSON(){
        return JSON.stringify(formDict());
    }

    displayDict(formDict());
    
    $('form').change(function(){
        displayDict(formDict());
    });

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var target = $(e.target).attr("href")
        if(target == '#finalize'){    
            displayDict(formDict());
        }
    });

    $(".finalize-step").click(function (e){
        sessionStorage.setItem('session-configuration', dictToJSON());
    });
});

function formDict(){
    var configuration = document.getElementById('wizardform');

    var dict = {};

    for(var i=0; i< configuration.length; i++){
        if(configuration[i].type =='hidden' ){
            for(var k=i+1; k<configuration.length; k++){
                if(configuration[k].type =='radio' || configuration[k].type =='check'){
                    if(configuration[k].checked){
                        dict[configuration[i].value] = document.getElementById(String(configuration[k].id)).value;
                        break;
                    }
                }

                if(configuration[k].type =='select-one' || configuration[k].type == 'number'){
                    dict[configuration[i].value] = configuration[k].value;
                    break;
                }
            }
        }        
    }
    
    return dict;
}

function displayDict(dict){
    
    var displayDescriptions = ['Mode','Configuration','Location','Region','Terrain','Launch Window','Duration Of Stay', 'Transportation','Payload','Model'];

    var index = 0;

    Object.keys(dict).forEach(function(key){            
        document.getElementById(key.toString()).innerHTML = displayDescriptions[index] + ": ";
        document.getElementById(key.toString()).innerHTML += dict[key].toString();
        index++;
    });
}