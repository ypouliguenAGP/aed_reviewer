<template>
    <div id="dump_stats">
        <div class="row mt-1">
            <div class="col col col-lg-4"></div>
            <div class="col">
                <ul class="nav nav-pills nav-fill nav-pills-sm">
                    <li class="nav-item">
                    <button class="nav-link" :class="unit == 'pps' ? 'active': ''" @click="unit='pps'">PPS <template v-if="stats['action']">({{ humanUnits(sumPackets(stats['action']['pps'])) }})</template></button>
                    </li>
                    <li class="nav-item">
                    <button class="nav-link" :class="unit == 'bps' ? 'active': ''" @click="unit='bps'">BPS <template v-if="stats['action']">({{ humanUnits(sumPackets(stats['action']['bps'])) }})</template></button>
                    </li>
                </ul>
            </div>
            <div class="col col col-lg-4">
                <p class="text-end pe-5" v-if="stats['action']">Avg packet length: {{ avgPacketSize() }}</p>
            </div>
        </div>
        <div class="row">
            <div class="col col-12 col-xl-6">
                <PGDumpStatsPie :stats="stats['src_port']" :unit="unit" title_str="Top Src Port"/>
            </div>
            <div class="col col-12 col-xl-6">
                <PGDumpStatsPie :stats="stats['dst_port']" :unit="unit" title_str="Top Dst Port"/>
            </div>
        </div>
        <div class="row">
            <div class="col col-12 col-xl-6">
                <PGDumpStatsPie :stats="stats['proto']" :unit="unit" title_str="Top Proto"/>
            </div>
            <div class="col col-12 col-xl-6">
                <PGDumpStatsPie :stats="stats['src_country']" :unit="unit" title_str="Top Src Country"/>
            </div>
        </div>
        <div class="row">
            <div class="col col-12 col-xl-6">
                <PGDumpStatsPie :stats="stats['src_ip']" :unit="unit" title_str="Top Src IP"/>
            </div>
            <div class="col col-12 col-xl-6">
                <PGDumpStatsPie :stats="stats['dst_ip']" :unit="unit" title_str="Top Dst IP"/>
            </div>
        </div>
        <div class="row">
            <div class="col col-12 col-xl-6">
                <PGDumpStatsPie :stats="stats['action']" :unit="unit" title_str="Action"/>
            </div>
        </div>
        
        

        
        
        
        
        
        
    </div>
</template>

<script setup>
const props = defineProps({
  title_str: String,
  pg_id: String,
})
import { ref, onMounted } from 'vue';
import { humanUnits } from '@/composables/helpers.js';
import PGDumpStatsPie from './PGDumpStatsPie.vue';

const stats = ref({})
const unit = ref('pps')

function loadData(){
    fetch('http://localhost:5000/aed_reviewer/api/protection_groups/'+props.pg_id+'/dump_stats/')
    .then(response => response.json())
    .then(data => stats.value = data)
}

function sumPackets(packets){
    var count = 0
    for (const packet of packets){
        count += packet[1]
    }
    return count
}
function avgPacketSize(){
    return Math.round(sumPackets(stats.value['action']['bps'])/sumPackets(stats.value['action']['pps']))
}

onMounted(() => {
    loadData()
})
</script>

<style scoped>

</style>
