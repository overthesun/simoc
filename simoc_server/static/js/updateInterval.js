
$(document).ready(function(){

    var step_num = 0;

    var stepSpeed = 1000;


    var updateInterval = 1000; // In Milleseconds
    var stepSize = 1;
    var updateRunning = true;

    var updateIntevalID = null;

    function setUpdateTimeout(){
        updateIntevalID = setTimeout(function() {
            if(updateRunning){
                updateStep();
            }
        }, updateInterval);
    }


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
                totalFoodMass = data.total_food_mass;
                totalBiomass = data.total_biomass
                totalInedibleBiomass = data.total_inedible_biomass
                totalPowerCharge = data.total_power_charge;
                totalHumans = data.total_humans;
                hoursPerStep = data.hours_per_step;
                currentStep = data.step_num;
                waterGray = data.total_grey_water;
                waterGraySolids = data.total_grey_water_solids;

                oxygenG.refresh(avgOxygen);
                carbdonDioxideG.refresh(avgCarbonDioxide);
                waterG.refresh(totalWater);
                biomassG.refresh(totalBiomass);
                //eProducedG.refresh();
                //eConsumedG.refresh();

                document.getElementById("biomassTotal").innerHTML = totalBiomass.toFixed(2);
                document.getElementById("biomassEdible").innerHTML = totalFoodMass.toFixed(2);
                
                document.getElementById("foodEnergy").innerHTML = totalFoodEnergy.toFixed(2);
                document.getElementById("foodMass").innerHTML = totalFoodMass.toFixed(2);

                document.getElementById("waterPotable").innerHTML = totalWater.toFixed(2);
                document.getElementById("waterGray").innerHTML = waterGray.toFixed(2);
                document.getElementById("waterGraySolid").innerHTML = waterGraySolids.toFixed(2);
                //updateAllBarCharts(avgOxygen,avgCarbonDioxide,totalWater,
                  //  totalFoodEnergy, totalPowerCharge);
                //updateAllLineCharts(avgOxygen, avgCarbonDioxide, totalWater,
                //    totalFoodEnergy, currentStep);
                updateSolarDay(currentStep, hoursPerStep);
            }
        }).done(function(){
            setUpdateTimeout();
        });
    }

    setUpdateTimeout();

    $('#dashboard-pause').click(function(){

    })

    function updateSolarDay(stepNum, hoursPerStep){
        var hours = stepNum * hoursPerStep;
        console.log(hours, stepNum, hoursPerStep);
        document.getElementById('currentDate-id').innerHTML = "Mars: Sol " + Math.floor(1+(hours / 24.65));
    }

    $("#slowdown-button").click(function(){
        updateInterval = Math.min(5000, updateInterval + 100);
        stepSpeed = Math.min(5000, stepSpeed + 100);
        document.getElementById('currentSpeed-id').innerHTML =  hoursPerStep + " Hour per " + stepSpeed/1000.0 + "s";
    })

    $("#speedup-button").click(function(){
        updateInterval = Math.max(300, updateInterval - 100);
        stepSpeed = Math.max(300, stepSpeed - 100);
        document.getElementById('currentSpeed-id').innerHTML = hoursPerStep + " Hour per " + stepSpeed/1000.0 + "s";
    })

    $("#pause-button").click(function(){
    updateRunning = !updateRunning;

        if(updateRunning){
            setUpdateTimeout();
        }
    })

});


