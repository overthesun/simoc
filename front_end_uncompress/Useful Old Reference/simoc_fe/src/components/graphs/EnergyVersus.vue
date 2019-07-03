<template>
    <canvas :id="id" style="height: 100%; width: 100%;" height='auto' width='auto'/>
</template>

<script>
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
export default {
    props:{
        id:String,
    },

    computed:{
        ...mapGetters('stepData',['getStepNumber','getTotalProduction','getTotalConsumption'])
    },

    watch:{
        getStepNumber:function(){
            this.updateChart()
        }
    },

    methods:{
        updateChart:function(){
            console.log(this.getTotalProduction(this.getStepNumber))
            let{enrg_kwh:consumption} = this.getTotalConsumption(this.getStepNumber)
            let{enrg_kwh:production} = this.getTotalProduction(this.getStepNumber)

            this.chart.data.datasets[0].data.shift()
            this.chart.data.datasets[1].data.shift()
            this.chart.data.labels.shift()

            this.chart.data.datasets[0].data.push(production.value)
            this.chart.data.datasets[1].data.push(consumption.value)
            this.chart.data.labels.push(this.getStepNumber)

            this.chart.update()
        }
    },


    mounted(){
        const ctx = document.getElementById(this.id)
        this.chart = new Chart(ctx, {
            type: 'line',
            data:{
                labels: Array(24),
                datasets:[{
                        lineTension: 0,
                        data: Array(24),
                        label: 'Produced',
                        borderColor: "rgba(0,0,255,1)",
                        fill:false
                    },
                    {
                        lineTension: 0,
                        data: Array(24),
                        label: 'Produced',
                        borderColor: "#cd0000",
                        fill: false
                    }
                ]
            },
            options:{
                scales:{
                    yAxes:[{
                        ticks:{
                            beginAtZero:true,
                            callback:function(value,index,values){
                                return value + ' kW'
                            }
                        }
                    }]
                },
                legend:{
                    display:false,
                },
                animation:{
                    animateScale: false,
                    animateRotate: false,
                },
                title:{
                    display:false,
                    text:'(Energy) Consumption Vs Production'
                },
                scales:{
                    xAxes:[{
                        ticks:{
                            min:0,
                            max:24,
                            beginAtZero:true,
                        }
                    }]
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

</style>
