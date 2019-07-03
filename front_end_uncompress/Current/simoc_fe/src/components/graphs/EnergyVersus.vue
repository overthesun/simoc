<!--
Energy versus chart component used within the dashboard.

Updates values from the approriate step data getters when it sees an updated value within the 
getStepBuffer object. This causes the bug that makes the line chart 'crawl' during the initial buffering period.

See chart.js documentation for further details on the related mounted functions.
-->

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
        ...mapGetters('dashboard',['getStepBuffer','getTotalProduction','getTotalConsumption'])
    },

    watch:{
        //Update the chart datasets and labels when the step buffer has changed.
        //This actually causes a bug where charts are updated even when just the 'max' is 
        //updated within the object. This needs to be changed to watch just the step number only to prevent
        //uncessary updates as seen currently in the energy versus chart.
        getStepBuffer:{
            handler:function(){
                this.updateChart()
            },
            deep:true
        }
    },

    methods:{

        //Could actually be placed within the watch method.
        updateChart:function(){
            console.log(this.getTotalProduction(this.getStepBuffer.current))
            let{enrg_kwh:consumption} = this.getTotalConsumption(this.getStepBuffer.current)
            let{enrg_kwh:production} = this.getTotalProduction(this.getStepBuffer.current)

            this.chart.data.datasets[0].data.shift()
            this.chart.data.datasets[1].data.shift()
            this.chart.data.labels.shift()

            this.chart.data.datasets[0].data.push(production.value)
            this.chart.data.datasets[1].data.push(consumption.value)
            this.chart.data.labels.push(this.getStepBuffer.current)

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
