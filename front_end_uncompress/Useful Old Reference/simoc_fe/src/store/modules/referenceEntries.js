export default{
    state:{
        currentEntry:"welcome",
        entries:{
            welcome:
                `
                    <div style="margin-bottom:2rem">Welcome to SIMOC</div>
                    <div style="margin-bottom:2rem">This is the enclyclopedia reference for the configuration
                    wizard. By clicking on a fields title, you can navigate directly to 
                    that specific entry.</div><div >We have a number of additional features that will
                    be added in future versions of the encyclopedia, including links to 
                    other articles tagged within entries themselves,images, and possibly even
                    videos.</div>
                `,
            contents:
                `This is the table of contents. It is currently in the works, and will be available
                in a future version.`,
            location:
                ``,
            duration:
                ``,
            humans:
                `<p>If you design a mission that includes 
                humans in your off-world habitat, then 
                several other components will be required: 
                Food for the humans to consume as they travel 
                from Earth to Mars and for their time on Mars 
                until the greenhouse produces the first edible plants; 
                an Environmental Control and Life Support System (ECLSS)
                to maintain breathable air and potable water, as well as
                manage the human waste products; and a place for the humans 
                to work, recreate, and sleep.</p><br>Humans are 
                not required for a mission configuration.`,
        }
    },
    getters:{
        getEntry: state => state.entries[state.currentEntry],
        getCurrentEntry: state => state.currentEntry
    },
    mutations:{
        setEntry: (state,value) => state.currentEntry = value
    },
}