
$(document).ready(function(){

    var step_num = 0;


    console.log("TESTING TIME");
    var updateInterval = 1000; // In Milleseconds
    var updateRunning = true;
    var stepSize = 1;

    var updateIntevalID = setInterval(function(){ if(updateRunning){updateStep();}}, updateInterval);


    var currentStep = null;

    function updateStep(){
        var route = "/get_step";
        if(currentStep !== null){
            currentStep += stepSize;
            route += '?step_num=' + currentStep;
        }
        getFormatted(route, function (data,status) {

            if (status == 'success'){ 
                console.log("Step Updated");
                console.log(data);
                avgOxygen = data.avg_oxygen_pressure;
                avgCarbonDioxide = data.avg_carbon_dioxide_pressure;
                totalWater= data.total_water;
                totalFoodEnergy = data.total_food_energy;
                totalPowerCharge = data.total_power_charge;
                currentStep = data.step_num;
                updateAllBarCharts(avgOxygen,avgCarbonDioxide,totalWater,
                    totalFoodEnergy, totalPowerCharge);
                updateAllLineCharts(avgOxygen, avgCarbonDioxide, totalWater,
                    totalFoodEnergy, currentStep);
                //updateSolarDay(data.step.num)
            }
        });
     
    }

    $('#dashboard-pause').click(function(){

    })


});


