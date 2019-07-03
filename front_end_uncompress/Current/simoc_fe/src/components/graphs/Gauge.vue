<!--
Gauge chart component used within the dashboard.

 Props are used to pass in the values for the gauges to use within the 'Gauge' component. Passing in the getter method
was simply added so that the gauges were more generalized for future implementations beyond atmospheric tracking.
See chart.js documentation for further explantion of below fucntionality.

-->

<template>
    <div style='position:relative'>
        <canvas :id="id" style="height: 100%; width: 100%;" height='auto' width='auto'/>
    </div>
</template>

<script>
import Chart from 'chart.js';
import "chartjs-plugin-annotation";
import {mapState,mapGetters} from 'vuex' 
export default {
    props:{
        id:String,
        color:String,
        keyValue:String,
        maximum:Number,
        label:String,
        getter:Function,
        stepDataKey:String
    },

    computed:{
        ...mapGetters('dashboard',['getStepBuffer'])
        //...mapGetters('stepData',['getStepNumber'])
    },

    watch:{      
        //Update the chart datasets and labels when the step buffer has changed.
        //This actually causes a bug where charts are updated even when just the 'max' is 
        //updated within the object. This needs to be changed to watch just the step number only to prevent
        //uncessary updates as seen currently in the energy versus chart.
        getStepBuffer:{
            handler:function(){
                const {current} = this.getStepBuffer
                let retrieved = this.getter(current)
                let value = retrieved[this.keyValue]
                let remainder = this.maximum - value

                this.chart.data.labels = [this.label]
                this.chart.data.datasets[0].data.pop()
                this.chart.data.datasets[0].data = [value,remainder]
                this.chart.data.datasets[0].backgroundColor = [this.color, '#fff']
                this.chart.options.elements.centerText.text = (value*100).toFixed(4)+"%"
                this.chart.update()
            },
            deep:true
        }
    },

    mounted(){
        const ctx = document.getElementById(this.id)
        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data:{
                centerText: "TEST",
                labels: ['Oxygen'],
                datasets:[{
                    backgroundColor: this.color,
                    data:[10]
                }]
            },
            rotation: Math.PI * -.5,
            options:{
                elements:{
                    arc:{
                        borderWidth: 0
                    },
                    centerText:{
                        text:"Calculating",
                    }
                },
                legend:{
                    display: false,
                },
                animation:{
                    animateScale: false,
                    animateRotate:false
                },
                defaultFontColor: '#1e1e1e',
                response: true,
                maintainAspectRatio: false,
                drawborder:false,
                cutoutPercentage: 70,
                rotation: Math.PI,
                circumference: 1 * Math.PI
            },
            plugins:[{
                beforeDraw: function(chart){
                    var width = chart.chart.width;
                    var height = chart.chart.height;
                    var ctx = chart.chart.ctx;

                    ctx.restore();
                    var fontSize = (height/144).toFixed(2);
                    ctx.font = fontSize + "em sans-serif";
                    ctx.textBaseline = "bottom";                  

                    var text = chart.chart.options.elements.centerText.text,
                        textX = Math.round((width - ctx.measureText(text).width) / 2),
                        textY = height;

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
    canvas{
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        position: absolute;
        width: 100%;
        height: 100%;
    }
</style>
