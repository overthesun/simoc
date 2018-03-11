var intervalRate = 3000; //1000 = 1 sec

var paused = true; // Starts paused

var avg_oxygen_pressure = 0;
var avg_co2_pressure;
var total_water;

function intervalUpdate(){

    //if(paused)
    //    return false;
    
    setInterval(function(){ getStep(); console.log("New Step"); }, 3000);

}

function intervalIncrease(){

}

function intervalDecrease(){

}

function getStep(){
    getFormatted('/get_step', function (data,status) {
            if (status == 'success'){ 
                var stepData = {}
                avg_oxygen_pressure = data.avg_oxygen_pressure;
                console.log(data.avg_oxygen_pressure);
                window.myBar.update();
        }
    });
}

function getOxygen(){
    return avg_oxygen_pressure;
}