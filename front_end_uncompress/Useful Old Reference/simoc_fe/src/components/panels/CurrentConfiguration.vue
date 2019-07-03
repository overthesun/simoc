<template>
    <div class='item-wrapper'>
        <div class='line-wrapper'>
            <div class='line-title'>Location:</div>
            <div class='line-item'>Mars</div>
        </div>
        <div class='line-wrapper'>
            <div class='line-title'>Inhabitants:</div>
            <div class='line-item'></div>
        </div>
        <div class='line-wrapper'>
            <div class='line-title'>Duration:</div>
            <div class='line-item'></div>
        </div>
        <div class='line-wrapper'>
            <div class='line-title'>Food:</div>
            <div class='line-item'></div>
        </div>
        <div class='line-wrapper'>
            <div class='line-title'>Greenhouse:</div>
            <div class='line-item'></div>
        </div>
        <div class='plant-wrapper' v-for="(line,index) in getPlantSpecies" :key="index">
            <div class='line-title'>Plant Species:</div>
            <div class='line-item'>{{formattedPlantNames(getPlantSpecies[index].type)}}</div>
            <div class='line-title'>Qty:</div>
            <div class='line-item'>{{getPlantSpecies[index].amount}}</div>
        </div>
        <div class='line-wrapper'>
            <div class='line-title'>Crew Quarters:</div>
            <div class='line-item'></div>
        </div>
        <div class='line-wrapper'>
            <div class='line-title'>ECLSS:</div>
            <div class='line-item'></div>
        </div>
        <div class='line-wrapper'>
            <div class='line-title'>Solar Arrays:</div>
            <div class='line-item'></div>
        </div>
        <div class='line-wrapper'>
            <div class='line-title'>Power Storage:</div>
            <div class='line-item'></div>
        </div>
    </div>
</template>

<script>
export default {

}
</script>

<style lang="scss" scoped>

</style>
