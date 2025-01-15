

<script setup>

const props = defineProps({
  pg_id: String,
})

import { onMounted,ref } from 'vue';
import TrafficLocation from '@/components/TrafficLocation.vue';
import TrafficGeneric from '../components/TrafficGeneric.vue'
import TrafficProtocol from '@/components/TrafficProtocol.vue';
import TrafficService from '@/components/TrafficService.vue';


const chart_period = ref('1d')
const graph_unit = ref('bps')
const stats = ref({})
function loadPeriod(new_chart_period){
    chart_period.value = new_chart_period
    fetch('http://localhost:5000/api/protection_groups/'+props.pg_id+'/traffic/'+chart_period.value)
    .then(response => response.json())
    .then(data => stats.value = data)
    console.log(chart_period.value)
}
onMounted(() => {
    loadPeriod(chart_period.value)
})
</script>


<template>
    <div id="network-graphs" class="container mt-2">
        <div class="row">
            <div class="col">
            <ul class="nav nav-pills nav-fill">
                <li class="nav-item">
                <button class="nav-link" :class="chart_period == '7d' ? 'active': ''" @click="loadPeriod('7d')">7 Days</button>
                </li>
                <li class="nav-item">
                <button class="nav-link" :class="chart_period == '1d' ? 'active': ''" @click="loadPeriod('1d')">1 Day</button>
                </li>
                <li class="nav-item">
                <button class="nav-link" :class="chart_period == '1h' ? 'active': ''" @click="loadPeriod('1h')">1 Hour</button>
                </li>
            </ul>
            </div>
            <div class="col">
            </div>
            <div class="col">
            <ul class="nav nav-pills nav-fill">
                <li class="nav-item">
                <button class="nav-link" :class="graph_unit == 'pps' ? 'active': ''" @click="graph_unit='pps'">PPS</button>
                </li>
                <li class="nav-item">
                <button class="nav-link" :class="graph_unit == 'bps' ? 'active': ''" @click="graph_unit='bps'">BPS</button>
                </li>
            </ul>
            </div>
        </div>
        <TrafficGeneric title_str="Traffic" v-if="stats.traffic" :data="stats.traffic[graph_unit]" :unit="graph_unit" />
        <TrafficLocation title_str="Location" v-if="stats.locations" :data="stats.locations" :unit="graph_unit"/>
        <TrafficProtocol title_str="Protocols" v-if="stats.protocols" :data="stats.protocols" :unit="graph_unit"/>
        <TrafficService title_str="Services" v-if="stats.services" :data="stats.services" :unit="graph_unit"/>
    </div>
</template>


<style scoped>
</style>
