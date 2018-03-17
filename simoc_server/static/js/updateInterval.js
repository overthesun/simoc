
$(document).ready(function(){

    var step_num = 0;


    console.log("TESTING TIME");
    var updateInterval = 1000; // In Milleseconds
    var updateRunning = true;
    
    setInterval(function(){ if(updateRunning){updateStep();}}, updateInterval);

    function updateStep(){

        var urlString = "/get_step?step_num="+(step_num++);

        getFormatted(urlString, function (data,status) {
            if (status == 'success'){ 
                console.log("Step Updated");
                console.log(data);
                avg_oxygen = data.avg_oxygen_pressure;
                avg_carbonDioxide = data.avg_carbonDioxide;
                total_water= data.total_water;
                updateBarChart(avg_oxygen,avg_carbonDioxide,total_water);
                //updateSolarDay(data.step.num)
                
            }
        });
     
    }

    $('#dashboard-pause').click(function(){

    })


});


