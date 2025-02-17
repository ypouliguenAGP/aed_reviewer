<script setup>

const props = defineProps({
  protections: Object,
  levels: Array
})

import { onMounted,ref } from 'vue';

const mfl = ref({})
function loadData(){
    fetch('http://localhost:5000/aed_reviewer/api/master_filter_list')
    .then(response => response.json())
    .then(data => mfl.value = data)
}

onMounted(() => {
    loadData()
})


</script>
<template>
    <div class="row">
        <div class="col" v-for="level in levels">
            <p class="text-capitalize fw-bold text-center">{{ level }}</p>
        </div>
    </div>
    <div class="row">
        <div class="col" v-for="level in levels">
            <span class="fw-light" v-for="statement in protections['protectionLevels'][level]['filter']['statement']">{{ statement }}<br/></span>
        </div>
    </div>
    
    <div class="row mt-5">
        <hr/>
        <div class="col-2"></div>
        <div class="col">
                <p class="text-capitalize fw-bold text-center my-0">Master Filter List</p>
            <span class="fw-light" v-for="statement in mfl">{{ statement }}<br/></span>
        </div>
        <div class="col-2"></div>
    </div>
</template>