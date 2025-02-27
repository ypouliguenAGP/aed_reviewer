<script setup>
const props = defineProps({
  aed_id: String,
})

import { onMounted,ref } from 'vue';
import { humanUnits } from '@/composables/helpers';

const global_alerting = ref({})
function loadData(){
    fetch('/aed_reviewer/api/'+props.aed_id+'/global_alerting')
    .then(response => response.json())
    .then(data => global_alerting.value = data)
}

function avgPacketSize(pps, bps){
    return Math.round(bps/(pps*8))
}

onMounted(() => {
    loadData()
})

</script>

<template>
    <div>
        <table class="table">
            <thead>
            <tr>
                <th scope="col">Type</th>
                <th scope="col">Enabled</th>
                <th scope="col">Percent</th>
                <th scope="col">Ignore PPS</th>
                <th scope="col">Ignore BPS</th>
                <th scope="col">Ignore AVG length</th>
            </tr>
            </thead>
            <tbody>
                <tr v-for="(alerting, key) in global_alerting">
                    <th class="text-capitalize">{{key}}</th>
                    <td class="text-capitalize">{{ alerting.enabled }}</td>
                    <th>{{ alerting.percent }}%</th>
                    <td>{{ humanUnits(alerting.ignore_pps) }}</td>
                    <td>{{ humanUnits(alerting.ignore_bps) }}</td>
                    <td>
                        <span :class="(avgPacketSize(alerting.ignore_pps, alerting.ignore_bps) > 1500 || avgPacketSize(alerting.ignore_pps, alerting.ignore_bps) < 30) ? 'text-warning': 'text-success'">{{ avgPacketSize(alerting.ignore_pps, alerting.ignore_bps) }} bytes</span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>