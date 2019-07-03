<template>
    <canvas id="canvas" style='height: 100%; width: 100%;' height='auto' width='auto'></canvas>
</template>
<script>
import Chart from 'chart.js';
import axios from 'axios'
import "chartjs-plugin-annotation";
import {mapState,mapGetters} from 'vuex' 
export default {
    data(){
        return{
            greenhouseSize:{
                'greenhouse_small':490,
                'greenhouse_medium':2454,
                'greenhouse_large':5610
            }
        }
    },

    computed:{
        ...mapGetters('configuration',['getPlantSpecies','getGreenhouse']),
        ...mapGetters('stepData',['getStepNumber']),


        maxLine:function(){
            let greenhouse = this.getGreenhouse.type
            let maxLine = this.greenhouseSize[greenhouse]
            return maxLine
        },

        graphData:function(){
            let species = this.getPlantSpecies
            let amounts = []
            let types = []
            
            species.forEach((item) =>{
                amounts.push(item.amount)
                types.push(item.type)
            })

            let data = {
                amounts:amounts,
                types:types
            }

            return data
            
        },
    },

    watch:{
        getSteNumber:function(){
            console.log("TEST2")
            this.chart.data.labels =[]
            this.chart.data.labels = this.graphData.types
            this.chart.data.datasets[0].data.pop()
            this.chart.data.datasets[0].data = this.graphData.amounts            
            this.chart.update()
            console.log("TESTING")
        },

        maxLine:function(){
            this.chart.options.annotation.annotations.pop()
            this.chart.options.annotation.annotations.push({
                type: 'line',
                mode: 'horizontal',
                scaleID: 'y-axis-0',
                value: this.maxLine,
                borderColor: 'red',
                borderWidth: 5,
                label: {
                    backgroundColor: "red",
                    content: "Test Label",
                    enabled: false
                },
            })
            this.chart.update()
        },

        graphData: function(){
            console.log("TEST2")
            this.chart.data.labels =[]
            this.chart.data.labels = this.graphData.types
            this.chart.data.datasets[0].data.pop()
            this.chart.data.datasets[0].data = this.graphData.amounts            
            this.chart.update()
        }
    },


    mounted(){
        
        const ctx = document.getElementById("canvas");
        this.chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: [1,2,3],
                    datasets: [{ 
                        lineTension: 0,
                        data: [],
                        label: "Produced",
                        borderColor: "#00aaee",
                        backgroundColor: "#00aaee",
                        fill:false,
                    }, { 
                        lineTension: 0,
                        data: [0,0,0,0,0,0,0,0,0,0,0],
                        label: "Consumed",
                        borderColor: "#cd0000",
                        fill:false,
                    }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio:false,
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Greenhouse Configuration'
                    },
                    scales:{
                        yAxes:[{
                            display:true,
                            ticks:{
                                min:0,
                                beginAtZero: true,
                            }
                        }]
                    },
                    annotation: {
                        drawTime: 'afterDatasetsDraw',
                        events: ['click'],
                        annotations: [{
                            //Don't use annotation ID's
                            type: 'line',
                            mode: 'horizontal',
                            scaleID: 'y-axis-0',
                            value: 0,
                            borderColor: 'red',
                            borderWidth: 5,
                            label: {
                                backgroundColor: "red",
                                content: "",
                                enabled: false
                            },
                        }]
                    }
                }
            });
        
        /*new Chart(ctx, {
				type: 'bar',
                data: {
                    labels: [1,2,3],
                    datasets: [{ 
                        lineTension: 0,
                        data: [],
                        label: "Produced",
                        borderColor: "#00aaee",
                        backgroundColor: "#00aaee",
                        fill:false,
                    }, { 
                        lineTension: 0,
                        data: [0,0,0,0,0,0,0,0,0,0,0],
                        label: "Consumed",
                        borderColor: "#cd0000",
                        fill:false,
                    }
                    ]
                },
				options: {
                    responsive: true,
                    maintainAspectRatio: false,
					legend: {
						position: 'top',
					},
					title: {
						display: true,
						text: 'Chart.js Bar Chart'
					},
				}
			});*/
        this.chart.update()
    }
}
</script>

<style lang="scss" scoped>
    
    canvas{
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        position:absolute;
        width:100%;
        height:100%;
    }
</style>
