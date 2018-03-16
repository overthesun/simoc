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
      labels: ["KW/H"],
      datasets: [
        {
          label: "KW/H",
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

function updateBarChart(avg_oxygen){
  console.log(avg_oxygen);
  console.log(total_water);
  oxygenBar.data.datasets[0].data[0] = avg_oxygen;
  oxygenBar.update();   

  carbonDioxideBar.data.datasets[0].data[0] = avg_carbonDioxide;
  carbonDioxideBar.update();

  waterBar.data.datasets[0].data[0] = total_water;
  waterBar.update();
}