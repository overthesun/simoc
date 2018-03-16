

$(document).ready(function(){
    console.log("TESTING TIME");
    var updateInterval = 1000; // In Milleseconds
    var updateRunning = true;
   
    var updateIntevalID = setInterval(function(){ if(updateRunning){updateStep();}}, updateInterval);

    function updateStep(){
        getFormatted('/get_step', function (data,status) {
            if (status == 'success'){ 
                console.log("Step Updated");
                console.log(data);
                avg_oxygen = data.avg_oxygen_pressure;
                avg_carbonDioxide = data.avg_carbonDioxide;
                total_water= data.total_water;
                updateBarChart(avg_oxygen,avg_carbonDioxide,total_water);
            }
        });
     
    }

    $('#dashboard-pause').click(function(){

    })
});


