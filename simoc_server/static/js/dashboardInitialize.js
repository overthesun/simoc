$(document).ready(function () {

    var configuration = JSON.parse(sessionStorage.getItem('session-configuration'));
    
    displayDict(configuration);

    function displayDict(dict){
        
        var displayDescriptions = ['Mode','Config','Location','Region','Terrain','Launch Window','Duration Of Stay', 'Transportation','Payload','Model'];

        var index = 0;

        Object.keys(dict).forEach(function(key){
            

            if(key == "payload-id")
                document.getElementById(key.toString()).innerHTML = "Humans: ";
            else if(key != "model-id")
                document.getElementById(key.toString()).innerHTML = displayDescriptions[index] + ": ";
            
            document.getElementById(key.toString()).innerHTML += dict[key].toString();
            index++;
        });
    }
});