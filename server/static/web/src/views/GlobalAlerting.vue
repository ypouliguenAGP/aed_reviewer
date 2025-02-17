<script setup>
import { onMounted,ref } from 'vue';
import { humanUnits } from '@/composables/helpers';

const global_alerting = ref({})
function loadData(){
    fetch('http://localhost:5000/aed_reviewer/api/global_alerting')
    .then(response => response.json())
    .then(data => global_alerting.value = data)
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
            </tr>
            </thead>
            <tbody>
                <tr v-for="(alerting, key) in global_alerting">
                    <th class="text-capitalize">{{key}}</th>
                    <td class="text-capitalize">{{ alerting.enabled }}</td>
                    <th>{{ alerting.percent }}%</th>
                    <td>{{ humanUnits(alerting.ignore_pps) }}</td>
                    <td>{{ humanUnits(alerting.ignore_bps) }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>