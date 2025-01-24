<template>
    <div id="dump_stats">
        <PGDumpStatsPie :stats="stats['src_ip']" unit="pps" title_str="Top Src IP"/>
        <PGDumpStatsPie :stats="stats['dst_ip']" unit="pps" title_str="Top Dst IP"/>
        <PGDumpStatsPie :stats="stats['proto']" unit="pps" title_str="Top Proto"/>
        <PGDumpStatsPie :stats="stats['src_port']" unit="pps" title_str="Top Src Port"/>
        <PGDumpStatsPie :stats="stats['dst_port']" unit="pps" title_str="Top Dst Port"/>
        <PGDumpStatsPie :stats="stats['action']" unit="pps" title_str="Action"/>
        <PGDumpStatsPie :stats="stats['src_country']" unit="pps" title_str="Top Src Country"/>
    </div>
</template>

<script setup>
const props = defineProps({
  title_str: String,
  pg_id: String,
})
import { ref, onMounted } from 'vue';
import PGDumpStatsPie from './PGDumpStatsPie.vue';

const stats = ref({})
const unit = ref('pps')

function loadData(){
    fetch('http://localhost:5000/api/protection_groups/'+props.pg_id+'/dump_stats/')
    .then(response => response.json())
    .then(data => stats.value = data)
}


onMounted(() => {
    loadData()
})
</script>

<style scoped>
</style>
