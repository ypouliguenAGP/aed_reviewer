<script setup>

const props = defineProps({
  alerts: Object,
})

import { onMounted,ref } from 'vue';
const units = ref([
      "k",
      "M",
      "G",
])
function humanUnits(value){
      if (value < 1000) return Math.max(value)
      let i = -1;
      do {
        value = value / 1000;
        i++;
      } while (value >= 1000);
      return Math.max(value).toFixed(1) + units.value[i];
}
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-GB', {dateStyle: 'long',  timeStyle: 'short'}).format(date);
}
</script>
<template>
    <div id="alerts" class="mt-2">
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Type</th>
                    <th>Start Time</th>
                    <th>Stop Time</th>
                    <th>Duration</th>
                    <th>Rate</th>
                </tr>
            </thead>
            <tbody>
                <template v-for="(alerts_arr, alert_type) in alerts">
                    <tr v-for="alert in alerts_arr">
                        <th>{{alert.id}}</th>
                        <td><span class="text-capitalize">{{alert_type}}</span></td>
                        <td>{{formatDate(alert.start_time*1000)}}</td>
                        <td>{{formatDate(alert.stop_time*1000)}}</td>
                        <td>{{ (alert.stop_time-alert.start_time)/60 }} min</td>
                        <td>
                            <template v-if="alert.unit == 'pps' || alert.unit == 'bps'">{{humanUnits(alert.rate)}}{{alert.unit}}</template>
                            <template v-else>{{alert.rate}}{{alert.unit}}</template>
                            
                        </td>
                    </tr>
                </template>
            </tbody>
        </table>
    
    </div>
    </template>