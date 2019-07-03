<!-- This component is simply for displaying which entry should be displayed on the reference side of the wizard. 

Future version should retrieve entries directly from the database, and simply use a v-html for the internal structure of the entry text. A 
v-for could be used to loop through each, populating the title, entry, and adding on the table of contents link to the bottom. This would
automate the process and prevent the need for individual sections for every entry. Table of contents could be opulated the same way
using v-for to populate all links with the title and the approriate value for the link.
-->

<template>
    <div class='encyclopedia-wrapper'>
        <div class='reference-item' v-if="getActiveRefEntry === 'Welcome'">
            <div class='reference-item-title'>Welcome To SIMOC</div>
            <div class='reference-item-entry'><a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Table')">Table Of Contents</a></div>
            <div class='reference-item-entry'>
                This is the enclyclopedia reference for the configuration
                wizard. By clicking on a fields title, you can navigate directly to 
                that specific entry.
            </div>
        </div>

        <div class='reference-item' v-if="getActiveRefEntry === 'Location'">
            <div class='reference-item-title'>Location</div>
            <div class='reference-item-entry'>
                Entry Being Written
            </div>
            <div class='reference-item-entry'><a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Table')">Table Of Contents</a></div>
        </div>

        <div class='reference-item' v-if="getActiveRefEntry === 'Duration'">
            <div class='reference-item-title'>Mission Duration</div>
            <div class='reference-item-entry'>
                Entry Being Written
            </div>
            <div class='reference-item-entry'><a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Table')">Table Of Contents</a></div>

        </div>

        <div class='reference-item' v-if="getActiveRefEntry === 'Inhabitants'">
            <div class='reference-item-title'>Inhabitants</div>
            <div class='reference-item-entry'>
                If you design a mission that includes humans in your off-world habitat, 
                then several other components will be required: 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Food')">Food</a> 
                for the humans to consume as they travel from Earth to Mars and for their time
                on Mars until the 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Greenhouse')">greenhouse</a>
                produces the first edible plants; an                 
                Environmental Control and Life Support System 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('ECLSS')">(ECLSS)</a> 
                to maintain breathable air and potable water, as well as manage the human waste products;
                 and a place for the humans to work, recreate, and sleep.
            </div>
            <div class='reference-item-entry'>
                Humans are not required for a mission configuration.
            </div>
            <div class='reference-item-entry'><a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Table')">Table Of Contents</a></div>
        </div>

        <div class='reference-item' v-if="getActiveRefEntry === 'Food'">
            <div class='reference-item-title'>Food</div>
            <div class='reference-item-entry'>
                Carefully consider the time required in transit from Earth to Mars, at roughly 7 
                months one-way. It is imperative that your humans have ample food supply for this
                journey, and enough food to sustain them on Mars as the 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('PlantSpecies')">plant species</a> 
                are growing in the 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Greenhouse')">greenhouse</a>
                , unable to produce edible fruit and vegetables until they mature.
            </div>
            <div class='reference-item-entry'>
                While the total mass of the food required to bring the humans to Mars will be included in the 
                payload calculations, the journey from Earth to Mars is not an integral part of this simulation. 
                Therefore, at the launch of the simulation the food consumed during the transit will be immediately 
                depleted from the total mass.
            </div>
            <div class='reference-item-entry'>
                FOOD is not required if no humans are selected.
            </div>
            <div class='reference-item-entry'><a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Table')">Table Of Contents</a></div>
        </div>

        <div class='reference-item' v-if="getActiveRefEntry === 'CrewQuarters'">
            <div class='reference-item-title'>Crew Quarters</div>
            <div class='reference-item-entry'>
                In selecting your crew quarters, it is prudent to consider a balance between the minimum volume 
                required to support the number of 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">humans</a> 
                you have chosen for their physical comport, and the 
                psychological benefits of a larger space. While SIMOC does not at this time model 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">human</a> 
                social interactions, the further benefit of a larger crew quarters is that it holds more breathable air, 
                and as such, acts as a storehouse for the key element for 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">human</a> 
                survival—breathing.
            </div>
            <div class='reference-item-entry'>
                If you are able to bring a larger crew quarters on the first mission, this also allows you to add 
                more humans without having to physically add structures. Future versions of SIMOC will enable the 
                scaling of your habitat to accommodate a growing community.
            </div>
            <div class='reference-item-entry'>
                CREW QUARTERS are not required if no 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">humans</a> 
                are selected.   
            </div>
            <div class='reference-item-entry'><a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Table')">Table Of Contents</a></div>
        </div>

        <div class='reference-item' v-if="getActiveRefEntry === 'ECLSS'">
            <div class='reference-item-title'>ECLSS</div>
            <div class='reference-item-entry'>
                An Environmental Control and Life Support System (ECLSS) is a set of machines whose function 
                is to maintain clean air, water, and relative humidity while sustaining a comfortable temperature for 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">human</a>  
                occupants of a closed environmental, such as a submarine, space craft, or off-world habitat.
            </div>
            <div class='reference-item-entry'>
                ECLSS modules are composed of many interconnected components, each of which is modeled in SIMOC. 
                But as they are also reach required, it is assumed they will be used together, as part of a total, 
                working system. As such, you much choose how many ECLSS modules you will bring on your mission.
            </div>
            <div class='reference-item-entry'>
                Each ECLSS module is designed to support three 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">humans</a>.
            </div>
            <div class='reference-item-entry'>
                An ECLSS module is not required if no 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">humans</a> 
                are selected.
            </div>
            <div class='reference-item-entry'><a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Table')">Table Of Contents</a></div>
        </div>

        <div class='reference-item' v-if="getActiveRefEntry === 'Greenhouse'">
            <div class='reference-item-title'>Greenhouse</div>
            <div class='reference-item-entry'>
                As with the 
                crew quarters, 
                the size of the greenhouse is a choice. If you intent for your 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">humans</a>  
                to consume only the 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('FOOD')">food</a>  
                they have brought with them, and to rely fully on 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('ECLSS')">ECLSS</a>   
                modules, a greenhouse is not required. If you desire for your 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">humans</a>  
                to consume some fresh fruits and vegetables, even if just one salad per few days, you might select a small greenhouse. The available 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('PlantSpecies')">plants</a>  
                will off-set some of the function of the 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('ECLSS')">ECLSS</a>  
                module(s). If you select a large greenhouse, you may have the option to eventually use the mechanical 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('ECLSS')">ECLSS</a>  
                modules as back-up only, and your 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">humans</a>   
                might enjoy fresh food with every meal.
            </div>
            <div class='reference-item-entry'>
                Keep in mind that if you select a large quantity of 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('PlantSpecies')">plants</a>
                , you might require a larger greenhouse
            </div>
            <div class='reference-item-entry'>
                Each greenhouse comes includes an airlock in order that it can maintain an internal concentration of CO2 greater than that which is safe or comfortable for 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">humans</a>.
            </div>
            <div class='reference-item-entry'>
                A GREENHOUSE is not required, even if 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">humans</a> 
                are selected.
            </div>
            <div class='reference-item-entry'><a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Table')">Table Of Contents</a></div>
        </div>

        <div class='reference-item' v-if="getActiveRefEntry === 'PlantSpecies'">
            <div class='reference-item-title'>Plant Species</div>
            <div class='reference-item-entry'>
                If your elect to provide your 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">humans</a> 
                with something more interesting than freeze-dried 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Food')">food</a>  
                for their long stay on Mars, a 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Greenhouse')">greenhouse</a> 
                and plants is a welcomed respite from the monotony of meals in a squeeze bottles and aluminum foil.
            </div>
            <div class='reference-item-entry'>
                Not only to fruits and vegetables provide nutrients and calories, they also help maintain a breathable 
                atmosphere and clean water, off-setting, maybe even replacing the function of the 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('ECLSS')">ECLSS</a>  
                modules. When selecting your plants, from 1 to 6 species, you will also select the percentage of the total volume of the 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Greenhouse')">greenhouse</a> 
                allocated to each plant species.
            </div>
            <div class='reference-item-entry'>
                Keep in mind that you will be starting your plants from seeds, not seedlings nor mature transplants. So make certain you have provided your 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">humans</a>
                with ample freeze-dried food for the journey to Mars, and during the time require before first harvest.
            </div>
            <div class='reference-item-entry'>
                PLANTS are not required, even if 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">humans</a>
                are selected.
            </div>
            <div class='reference-item-entry'><a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Table')">Table Of Contents</a></div>
        </div>

        <div class='reference-item' v-if="getActiveRefEntry === 'PowerGeneration'">
            <div class='reference-item-title'>Power Generation</div>
            <div class='reference-item-entry'>
                Select the number of solar photo-voltaic (PV) panels you believe will be required to sustain the electrical power needs of your full habitat.
                This includes electric heat, lighting for the 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">human</a>  
                occupied space and for the 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('PlantSpecies')">plants</a> 
                in the 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Greenhouse')">greenhouse</a> 
                too, 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('ECLSS')">ECLSS</a>
                operation, radio communication from the habitat to the orbiter, and personal computers.
            </div>
            <div class='reference-item-entry'>
                On 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Location')">Mars</a>
                , the total solar gain is roughly 1/3 that on Earth (at its maximum potential). Therefore, a 300 watt solar panel on 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Location')">Earth</a> 
                would generate only 100 watts on 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Location')">Mars</a>
                . This means you will need 3x more panels to produce the same amount of electric power.
            </div>
            <div class='reference-item-entry'>
                Keep in mind that not only do you need ample power for all electric devices by day, but also to charge the batteries to operate many of the same devices by night.
                 This will result in a substantial quantity of solar PV panels in your total array.
            </div>
            <div class='reference-item-entry'><a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Table')">Table Of Contents</a></div>
        </div>

        <div class='reference-item' v-if="getActiveRefEntry === 'PowerStorage'">
            <div class='reference-item-title'>Power Storage</div>
            <div class='reference-item-entry'>
                While 
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('PowerGeneration')">solar PV panels</a> 
                generate power by day, it is the batteries that provide power at night. As such, the total battery capacity 
                should be large enough to carry the habitat through an entire Martian night.',

            </div>
            <div class='reference-item-entry'><a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Table')">Table Of Contents</a></div>
        </div>

        <div class='reference-item' v-if="getActiveRefEntry === 'Table'">
            <div class='reference-item-title'>Table Of Contents</div>
            <div class='reference-item-entry'>
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Location')">Location</a>
            </div>
            <div class='reference-item-entry'>
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Duration')">Mission Duration</a>
            </div>
            <div class='reference-item-entry'>
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Inhabitants')">Inhabitants</a>
            </div>
            <div class='reference-item-entry'>
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Food')">Food Supply</a>
            </div>
            <div class='reference-item-entry'>
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('CrewQuarters')">Crew Habitat</a>
            </div>
            <div class='reference-item-entry'>
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('ECLSS')">Environmental Control</a>
            </div>
            <div class='reference-item-entry'>
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('Greenhouse')">Greenhouse</a>
            </div>
            <div class='reference-item-entry'>
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('PlantSpecies')">Plant Species</a>
            </div>
            <div class='reference-item-entry'>
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('PowerGeneration')">Power Generation</a>
            </div>
            <div class='reference-item-entry'>
                <a class='reference-link' href="#" @click="SETACTIVEREFENTRY('PowerStorage')">Power Storage</a>
            </div>
        </div>



    </div>
</template>

<script>
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
export default {
    computed:{
        ...mapGetters('wizard',['getActiveRefEntry'])
    },
    methods:{
        ...mapMutations('wizard',['SETACTIVEREFENTRY'])
    }   
}
</script>

<style lang="scss" scoped>
    .encyclopedia-wrapper{
        width:100%;
        height:100%;
        overflow-y:auto;
    }

    .reference-item{
        margin-right: 16px;
    }

    .reference-item-entry,.reference-item-title{
        &:not(:last-of-type){
            margin-bottom: 16px;
        }
    }

    .reference-item-title{
        font-size:24px;
        width: auto;
        font-weight:400;
    }

    .reference-link{
        text-decoration: underline;
        color:lightgreen;
        font-weight: 600;

        &:visited{
            color:lightgreen;

        }
    }
</style>
