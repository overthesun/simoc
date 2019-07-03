<!-- Greenhouse Doughnut Graph 

Updates and uses the values from the greenhouse and the plant species within the wizard store to populate the graph values. Currently
has enough color values for up to 30 plants.

See chart.js documentation for more details.
-->

<template>
    <canvas id="canvas" style='height: 100%; width: 100%;' height='auto' width='auto'></canvas>
</template>

<script>
import Chart from 'chart.js';
import axios from 'axios'
import "chartjs-plugin-annotation";
import {mapState,mapGetters} from 'vuex' 
import {StringFormatter} from '../../javascript/stringFormatter'
export default {
    data(){
        return{
            //Greenhouse volumes. These should be retrieved from the database in the future to populate.
            greenhouseSize:{
                'none':0,
                'greenhouse_small':490,
                'greenhouse_medium':2454,
                'greenhouse_large':5610
            },

            //Enough colors to cover all the plant types. Used to specify the color for each section of the pie chart.
            backgroundColor:["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe", "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000", "#aaffc3", "#808000", "#ffd8b1", "#000075", "#808080", "#ffffff", "#000000"]
        }
    },

    computed:{
        ...mapGetters('wizard',['getConfiguration']),
        ...mapGetters('dashboard',['getStepBuffer']),
        

        /*
        No longer used

        graphData:function(){
            let {greenhouse,plantSpecies} = this.getConfiguration
            let amounts = []
            let types = []
            
            let totalUsed = 0

            plantSpecies.forEach((item) =>{
                amounts.push(item.amount)
                types.push(new StringFormatter(item.type))
                totalUsed += parseInt(item.amount)
            })

            amounts.push()

            let data = {
                amounts:amounts,
                types:types
            }

            return data
        }*/            
    },

    methods:{
        //Format the plant data to be used within the chart object.

        greenhouseConfiguration:function(){
            const {greenhouse,plantSpecies} = this.getConfiguration // get the plants and greehouse from the configuration
            let values ={data:[this.greenhouseSize[greenhouse.type]],labels:["Free Space"]} // Set the first value of the dataset to the size of the greenhouse and add the label free space               
            plantSpecies.forEach((item)=>{
                values.data[0] = Math.max(0,values.data[0] - item.amount) //Calculates the total free space left after all the plants are added, modifies the first index initialized above. 
                values.data.push(item.amount) //Push in the amount of the plant that is present.
                //values.labels.push(this.stringFormatter(item.type))
                values.labels.push(StringFormatter(item.type)) //format the plant name string for display
            })

            return values
        },
        //Format the plant names before displaying them.
        stringFormatter: function(value){
            let formatted = ""

            formatted = value.replace(/_/g," ")
            formatted = formatted.toLowerCase()
                    .split(" ")
                    .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
                    .join(" ")

            return formatted   
        }
    },
    watch:{
        //Both watchers repeat the same functionality. This should really be moved into a method to cut down on the amount of code.

        //Watches for changes within the getStepBuffer object within dashboard store.
        getStepBuffer:{
            handler:function(){
                const {greenhouse,plantSpecies} = this.getConfiguration
                const {data,labels} = this.greenhouseConfiguration()
                this.chart.data.labels =[]
                this.chart.data.labels = labels
                this.chart.data.datasets[0].data.pop()
                this.chart.data.datasets[0].data = data    
                this.chart.options.elements.centerText.text = data[0] + " m³ / " + this.greenhouseSize[greenhouse.type] + " m³"        
                this.chart.update()
            },
            deep:true
        },

        //Watches for changes within the getConfiguration object within the wizard store.
        getConfiguration:{
            handler:function(){
                const {greenhouse,plantSpecies} = this.getConfiguration
                const {data,labels} = this.greenhouseConfiguration()
                this.chart.data.labels =[]
                this.chart.data.labels = labels
                this.chart.data.datasets[0].data.pop()
                this.chart.data.datasets[0].data = data
                this.chart.options.elements.centerText.text = data[0] + " m³ / " + this.greenhouseSize[greenhouse.type] + " m³"
                this.chart.update()
            },
            deep:true
        },
    },
    update(){
        
    },
    mounted(){
        console.log("TEST")
        const ctx = document.getElementById("canvas")
        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data:{
                labels: ["Free Space"],
                datasets:[{
                    backgroundColor: this.backgroundColor,
                    data:[0],
                }]
            },
            options:{
                response:true,
                maintainAspectRatio:false,
                           cutoutPercentage: 70,
                elements:{
                    arc:{
                        borderWidth: 0
                    },
                    centerText:{
                        text:"Greenhouse Doughnut Calculating",
                    }
                },
                legend:{
                    onClick:null,
                    display:true,
                    fontColor: "#eeeeee",
                    position: 'bottom',
                    labels:{
                        fontColor: "#eeeeee",
                        fontFamily: "open sans",
                        fontSize: 14,
                        boxWidth: 4,
                        usePointStyle:true,
                    }
                },
                animation:{
                    animateScale:false,
                    animateRotate:false,
                },
                drawborder: false,
            },
            plugins:[{
                beforeDraw: function(chart){
                    var width = chart.chart.width;
                    var height = chart.chart.height;
                    var ctx = chart.chart.ctx;

                    ctx.restore();
                    var fontSize = (height/300).toFixed(2);
                    ctx.font = fontSize + "em sans-serif";
                    ctx.textBaseline = "bottom";                  

                    var text = chart.chart.options.elements.centerText.text,
                        textX = Math.round((width - ctx.measureText(text).width) / 2),
                        textY = height/2;

                    ctx.fillStyle = 'white';
                    ctx.fillText(text,textX,textY);
                    ctx.save();
                }
            }]
        })
    }
}

</script>

<style lang="scss" scoped>

    .doughnut-wrapper{
        position:relative;
        display:grid;
        grid-template-rows: minmax(0px,1fr) 32px;
        grid-row-gap: 16px;
    }
</style>
