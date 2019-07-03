
<template>
    <div>
        <input type="number" name="fieldNumber" value=0 min=0 step=1 @input="handleChange"/>
        <input type="text" name="fieldText" value="" v-on:change="handleChange"/>
    </div>
</template>

<script>
export default {

    props:{
        handleChange:Function
    }

}
</script>

<style lang="scss" scoped>

</style>

<template>
    <div>
        <div class='input-wrapper'>
            <label class='input-label'>
                <div class='input-title'></div>
                <input type='number' class='input-text' value=0 min=0 step=1 @input="handleChange"/>
                <div class='input-reminder-wrapper'>
                </div>
            </label>
        </div>
    </div>
</template>

<script>
export default {

    props:{
        handleChange:Function
    }

}
</script>

<style lang="scss" scoped>

</style>

