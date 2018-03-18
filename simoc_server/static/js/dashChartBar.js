new Chart(document.getElementById("food-bar-chart"), {
    type: 'bar',
    data: {
      labels: ["FOOD"],
      datasets: [
        {
          label: "Food(kg)",
          backgroundColor: ["#e9f0f4"],
          data: [10]
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        display: true,
      },
      scales: {
        xAxes: [{
          barPercentage: 1.0,
          ticks: {
            autoSkip: false,
            maxRotation: 0,
            minRotation: 0
          }
        }]
      }
    }
});

var oxygenBar = new Chart(document.getElementById("oxygen-bar-chart"), {
    type: 'bar',
    data: {
      labels: ["OXYGEN"],
      datasets: [
        {
          label: "Oxygen",
          backgroundColor: ["#e9f0f4"],
          data: [10]
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        display: true,
      },

      scales: {
        xAxes: [{
          barPercentage: 1.0,
          ticks: {
            autoSkip: false,
            maxRotation: 0,
            minRotation: 0
          }
        }]
      }
    }
});

var carbonDioxideBar = new Chart(document.getElementById("cotwo-bar-chart"), {
    type: 'bar',
    data: {
      labels: ["CO2"],
      datasets: [
        {
          label: "CO2",
          backgroundColor: ["#e9f0f4"],
          data: [4]
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        display: true,
      },
      scales: {
        xAxes: [{
          barPercentage: 1.0,
          ticks: {
            autoSkip: false,
            maxRotation: 0,
            minRotation: 0
          }
        }]
      }
    }
});

var waterBar = new Chart(document.getElementById("water-bar-chart"), {
    type: 'bar',
    data: {
      labels: ["WATER"],
      datasets: [
        {
          label: "Water(L)",
          backgroundColor: ["#e9f0f4"],
          data: [10]
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        display: true,
      },
      scales: {
        xAxes: [{
          barPercentage: 1.0,
          ticks: {
            autoSkip: false,
            maxRotation: 0,
            minRotation: 0
          }
        }]
      }
    }
});

new Chart(document.getElementById("kwh-bar-chart"), {
    type: 'bar',
    data: {
      labels: ["kWh"],
      datasets: [
        {
          label: "kWh",
          backgroundColor: ["#e9f0f4"],
          data: [10]
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        display: true,
      },
      scales: {
        xAxes: [{
          barPercentage: 1.0,
          ticks: {
            autoSkip: false,
            maxRotation: 0,
            minRotation: 0
          }
        }]
      }
    }
});

function updateBarChart(avg_oxygen,avg_carbonDioxide,total_water){
  console.log(avg_oxygen);
  console.log(total_water);
  oxygenBar.data.datasets[0].data[0] = avg_oxygen;
  oxygenBar.update();   

  //carbonDioxideBar.data.datasets[0].data[0] = avg_carbonDioxide;
  //carbonDioxideBar.update();

  waterBar.data.datasets[0].data[0] = total_water;
  waterBar.update();


  //if(oxygenLine.data.datasets[0].data.length >= 10)
  //  oxygenLine.data.datasets[0].data.pop();
  
  oxygenLine.data.datasets[0].data.unshift(avg_oxygen);
  oxygenLine.update();

  //carbonDioxideLine.data.datasets[0].data.unshift(avg_carbonDioxide);
  //carbonDioxideLine.update();

  //waterLine.data.datasets[0].data.unshift(total_water);
  //waterLine.update();

}


var oxygenLine = new Chart(document.getElementById("oxygen-line-chart"), {
    type: 'line',
    data: {
      labels: [0,1,2,3,4,5,6,7,8,9,10,11,12],
      datasets: [
        {
          label: "Oxygen Pressure",
          borderColor: ["#e9f0f4"],
          data: [],
          fill: false
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        text:"Oxygen Pressure",
        display: true,
      }
    }
});

var waterDioxideLine = new Chart(document.getElementById("water-line-chart"), {
    type: 'line',
    data: {
      labels: [0,1,2,3,4,5,6,7,8,9,10,11,12],
      datasets: [
        {
          label: "Water(L)",
          borderColor: ["#e9f0f4"],
          data: [940,955,950,980,970,960,970,980,1000],
          fill: false
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        text:"Total Water(L)",
        display: true,
      }
    }
});

var carbonDioxideLine = new Chart(document.getElementById("co2-line-chart"), {
    type: 'line',
    data: {
      labels: [0,1,2,3,4,5,6,7,8,9,10,11,12],
      datasets: [
        {
          data:[.4,.3,.2,.5,.6,.7,.4,.2],
          label: "Carbon Dioxide Pressure",
          borderColor: ["#e9f0f4"],
          
          fill: false
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        text:"Carbon Dioxide Pressure",
        display: true,
      }
    }
});

var foodLine = new Chart(document.getElementById("food-line-chart"), {
    type: 'line',
    data: {
      labels: [0,1,2,3,4,5,6,7,8,9,10,11,12],
      datasets: [
        {
          label: "Total Food (kg)",
          borderColor: ["#e9f0f4"],
          data: [,460,440,455,470,465,485,480,490,500],
          fill: false
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        text:"Total Food (kg)",
        display: true,
      }
    }
});

Chart.defaults.global.defaultFontColor = "#fff";