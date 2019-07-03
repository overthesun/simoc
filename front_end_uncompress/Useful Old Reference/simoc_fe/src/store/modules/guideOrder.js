export default{
    state:{
        sections:[
            {
                componentName:"InitialForm",
                entryName:"initial",
                buttonName:"Initial",
                sectionName:"Initial",
            },
            {
                componentName:"InhabitantsForm",
                entryName:"humans",
                buttonName:"Humans",
                sectionName:"Inhabitants",
            },
            {
                componentName:"GreenhouseForm",
                entryName:"greenhouse",
                buttonName:"Greenhouse",
                sectionName:"Greenhouse",
            },
            {
                componentName:"PowerForm",
                entryName:"power",
                buttonName:"Power",
                sectionName:"Power",
            },
            {
                componentName:"FinalizeForm",
                entryName:"finalize",
                buttonName:"Finalize",
                sectionName:"Finalize",
            },
        ],
        skipGuidance:false
    },

    mutations:{
       skipConfiguration: (state,value) => state.skipGuidance = value,
    },

    getters:{
        skipGuidance: state => state.skipGuidance,
        sectionOrder: state => state.sections,      
    }
}