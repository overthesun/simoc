
$(document).ready(function(){
	//15.7 0.53
    var step_num = 0;
	var danger_values = {"oxygen":21.5 , "co2":0.1 , "water":0, "food" :0 , "power":0 };

    var stepSpeed = 1000;


    var updateInterval = 1000; // In Milleseconds
    var stepSize = 1;
    var updateRunning = true;

    var updateIntevalID = null;
	var alertInterval = null;
	var starting_humans;

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
                totalPowerCharge = data.total_power_charge;
                totalHumans = data.total_humans;
                hoursPerStep = data.hours_per_step;
                currentStep = data.step_num;
                updateAllBarCharts(avgOxygen,avgCarbonDioxide,totalWater,
                    totalFoodEnergy, totalPowerCharge);
                updateAllLineCharts(avgOxygen, avgCarbonDioxide, totalWater,
                    totalFoodEnergy, currentStep);
                updateSolarDay(currentStep, hoursPerStep);
				updateAlerts(avgOxygen, avgCarbonDioxide, totalWater, totalFoodEnergy, totalPowerCharge, totalHumans);
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
	
	function updateAlerts(oxygen, co2, h2o, food, power, humans){		
		if(starting_humans == null){
			starting_humans = humans;
		}else if(starting_humans > humans && document.getElementById('human-alert-id').innerHTML == ""){
			document.getElementById('human-alert-id').innerHTML = "<span class='alert-text'>Warning</span>: Sad news, one of the humans has died.";
			$("human-alert-id").fadeToggle();
			alertInterval = setTimeout(clearAlert.bind(null, 'human-alert-id'), 15000);
		}else if(starting_humans > humans && document.getElementById('human-alert-id').innerHTML != ""){
			clearTimeout(alertInterval);
			$("human-alert-id").fadeToggle(2000);
			document.getElementById('human-alert-id').innerHTML = "<span class='alert-text'>Warning</span>: Worse news, another one of the humans has died.";
			$("human-alert-id").fadeToggle(2000);
			alertInterval = setTimeout(clearAlert.bind(null, 'human-alert-id'), 10000);
		}
		starting_humans = humans;
		
		if(oxygen <= danger_values.oxygen && document.getElementById('oxygen-alert-id').innerHTML == ""){
			document.getElementById('oxygen-alert-id').innerHTML = "<span class='alert-text'>Warning</span>: Oxygen pressure is at a fatal level.";
			$("#oxygen-alert-id").fadeToggle();
		}else if(oxygen > danger_values.oxygen && document.getElementById('oxygen-alert-id').innerHTML != ""){
			clearAlert('oxygen-alert-id');
		}
		if(co2 >= danger_values.co2 && document.getElementById('co2-alert-id').innerHTML == ""){
			document.getElementById('co2-alert-id').innerHTML = "<span class='alert-text'>Warning</span>: CO2 pressure is at a fatal level";
			$("#co2-alert-id").fadeToggle();
		}else if(co2 < danger_values.co2 && document.getElementById('co2-alert-id').innerHTML != ""){
			clearAlert('co2-alert-id');
		}
		if(h2o <= danger_values.water && document.getElementById('h2o-alert-id').innerHTML == ""){
			document.getElementById('h2o-alert-id').innerHTML = "<'><span class='alert-text'>Warning</span>: There is no water.";
			$("#h2o-alert-id").fadeToggle();
		}else if(h2o > danger_values.water && document.getElementById('h2o-alert-id').innerHTML != ""){
			clearAlert('h2o-alert-id');
		}
		if(food <= danger_values.food && document.getElementById('food-alert-id').innerHTML == ""){
			document.getElementById('food-alert-id').innerHTML = "<span class='alert-text'>Warning</span>: There is no food.";
			$("#food-alert-id").fadeToggle();
		}else if(food > danger_values.food && document.getElementById('food-alert-id').innerHTML != ""){
			clearAlert('food-alert-id');
		}
		if(power <= danger_values.power && document.getElementById('power-alert-id').innerHTML == ""){
			document.getElementById('power-alert-id').innerHTML = "<span class='alert-text'>Warning</span>: The batteries have no charge.";
			$("#power-alert-id").fadeToggle();
		}else if(power > danger_values.power && document.getElementById('power-alert-id').innerHTML != ""){
			clearAlert('power-alert-id');
		}
	}
	
	function clearAlert(alertId){
		document.getElementById(alertId).innerHTML = "";
		$("#"+alertId).fadeToggle();
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