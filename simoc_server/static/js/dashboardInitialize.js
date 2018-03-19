$(document).ready(function () {

    var configuration = JSON.parse(sessionStorage.getItem('session-configuration'));
    
    displayDict(configuration);

    function displayDict(dict){
        
        var displayDescriptions = ['Mode','Model','Location','Region','Terrain','Launch Window','Duration Of Stay', 'Transportation','Payload'];

        var index = 0;

        Object.keys(dict).forEach(function(key){
            

            if(key == "payload-id")
                document.getElementById(key.toString()).innerHTML = "Humans: ";
            else if(key != "model-id")
                document.getElementById(key.toString()).innerHTML = displayDescriptions[index] + ": ";

            if(key == "durationofstay-id")
                document.getElementById(key.toString()).innerHTML += dict[key].toString() + " Months";
            else if(key == "launchwindow-id")
                document.getElementById(key.toString()).innerHTML += '<br>' + dict[key].toString();
            else
                document.getElementById(key.toString()).innerHTML += dict[key].toString();
            index++;
        });
    }
});
