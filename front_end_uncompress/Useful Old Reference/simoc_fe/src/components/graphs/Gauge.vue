<template>
    <canvas :id="id" style="height: 100%; width: 100%;" height='auto' width='auto'/>
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
        getter:Function
    },

    computed:{
        ...mapGetters('stepData',['getStepNumber'])
    },

    watch:{
        getStepNumber:function(){
            console.log("UPDATING")
        },
        
        getStepNumber:function(){
            let retrieved = this.getter(this.getStepNumber)
            let value = retrieved[this.keyValue]
            let remainder = this.maximum - value
            console.log(this.keyValue)
            console.log(retrieved)
            console.log(value)
            console.log(remainder)

            this.chart.data.labels = [this.label]
            this.chart.data.datasets[0].data.pop()
            this.chart.data.datasets[0].data = [value,remainder]
            this.chart.data.datasets[0].backgroundColor = [this.color, '#fff']
            this.chart.update()
        }
    },

    mounted(){
        const ctx = document.getElementById(this.id)
        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data:{
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
            }
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
