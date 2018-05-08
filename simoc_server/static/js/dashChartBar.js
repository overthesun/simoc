const MAX_BAR_TICK_LENGTH = 4;
const MAX_LINE_XTICK_LENGTH = 6;
const MAX_LINE_YTICK_LENGTH = 6;
const MAX_CHART_POINTS = 20;

var truncateToLength = function(value, maxLength){
  if(value === undefined)
    return value;
  var str = value.toString();
  if(str.length > maxLength){
    str = value.toPrecision(maxLength - 3);
  }
  else if(str.length  < maxLength){
    str = str.padStart(maxLength, " ");
  }
  //console.log(str);
  return str;
}

var baseLineChartOptions = {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        borderColor: ["#e9f0f4"],
        data: [],
        fill: false
      }
    ]
  },
  options: {
    legend: { display: false },
    maintainAspectRatio: false,
    tooltips: {
      enabled:false
    },
    title: {
      display: true,
    },
      scales: {
      xAxes: [{
        ticks:{
          autoSkip: true,
          callback: function(value){
            return truncateToLength(value, MAX_LINE_XTICK_LENGTH);
          }
        }
      }],
      yAxes: [{
        ticks: {
          autoSkip:true,
          //beginAtZero:true,
          callback:function(value){
            return truncateToLength(value, MAX_LINE_YTICK_LENGTH);
          }
        }
      }],
    }
  }
}



var createSingleLineOptions =function(datasetLabel, title){
  var options = $.extend(true, {}, baseLineChartOptions);
  options.data.datasets[0].label = datasetLabel;
  options.options.title.text = title;
  console.log(options);
  return options;
}

var createSingleBar = function(id, label, datasetLabel){
  return new Chart(document.getElementById(id), createSingleBarOptions(label, datasetLabel));
}

var createSingleLine = function(id, label, datasetLabel){
  return new Chart(document.getElementById(id), createSingleLineOptions(label, datasetLabel));
}

//var foodBar = createSingleBar("food-bar-chart", "Food (kJ)", "Food");
//var oxygenBar = createSingleBar("oxygen-bar-chart", "Oxygen (kPa)", "Oxygen")
//var carbonDioxideBar = createSingleBar("cotwo-bar-chart", "CO2 (kPa)", "CO2")
//var waterBar = createSingleBar("water-bar-chart", "Water (kg)", "Water")
//var chargeBar = createSingleBar("kwh-bar-chart", "Charge (kWh)", "Charge")
//var humanBar = createSingleBar("humans-bar-chart", "Humans", "Humans")

var oxygenLine = createSingleLine("canvas", "Oxygen Pressure (kPa)", "Oxygen Pressure (kPa)");
//var waterLine = createSingleLine("water-line-chart", "Total Water (kg)", "Total Water (kg)");
//var carbonDioxideLine = createSingleLine("co2-line-chart", "Carbon Dioxide Pressure (kPa)", "Carbon Dioxide Pressure (kPa)");
//var foodLine = createSingleLine("food-line-chart", "Total Food Energy (kJ)", "Total Food Energy (kJ)");



function updateLineChart(chart, stepNum, value){
  console.log(value);
  chart.data.datasets[0].data.push(value);
  chart.data.labels.push(stepNum);
  if(chart.data.datasets[0].data.length > MAX_CHART_POINTS){
    chart.data.datasets[0].data.shift();
    chart.data.labels.shift();
  }
  chart.update();
}

var updateAllLineCharts = function(avgOxygen,stepNum){//, avgCarbonDioxide, 
  //totalWater, totalFoodEnergy, stepNum){
  updateLineChart(oxygenLine, stepNum, avgOxygen);
  //updateLineChart(carbonDioxideLine, stepNum, avgCarbonDioxide);
  //updateLineChart(waterLine, stepNum, totalWater);
  //updateLineChart(foodLine, stepNum, totalFoodEnergy);
}


Chart.defaults.global.defaultFontColor = "#fff";