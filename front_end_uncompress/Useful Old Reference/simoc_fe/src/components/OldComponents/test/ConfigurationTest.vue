<template>
    <div class='interior-wrapper'>
        <button @click="testmethod">TEST</button>
    </div>
</template>

<script>
export default {
    methods:{
        testmethod:function(){
            console.log(this.$refs);
        }
    }
}
</script>



<style lang="scss" scoped>
    @import "../../sass/components/configuration-interior";
    @import "../../sass/components/configuration-main";
</style>