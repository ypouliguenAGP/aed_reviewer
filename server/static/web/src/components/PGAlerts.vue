<script setup>

const props = defineProps({
  alerts: Object,
})

import { onMounted,ref, computed } from 'vue';
import { round, now } from '@/composables/helpers';
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

const s_alerts = computed(() => {
    var alerts = []
    for (const [alert_type, alert_arr] of Object.entries(props.alerts)) {
        console.log(alert_type)
        for (const alert_value of alert_arr) {
            var alert = alert_value
            alert['type'] = alert_type
            alerts.push(alert)
        }
    }
    alerts.sort((a,b) => b.start_time - a.start_time);
    return alerts
})
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
                    <tr v-for="alert in s_alerts">
                        <th>{{alert.id}}</th>
                        <td><span class="text-capitalize">{{alert.type}}</span></td>
                        <td>{{formatDate(alert.start_time*1000)}}</td>
                        <td>
                            <template v-if="alert.stop_time != null">{{formatDate(alert.stop_time*1000)}}</template>
                            <template v-else>Ongoing</template>
                        </td>
                        <td>
                            <template v-if="alert.stop_time != null">{{ round((alert.stop_time-alert.start_time)/60) }} min</template>
                            <template v-else>/</template>
                        </td>

                        <td></td>
                        <td>
                            <template v-if="alert.unit == 'pps' || alert.unit == 'bps'">{{humanUnits(alert.rate)}}{{alert.unit}}</template>
                            <template v-else>{{alert.rate}}{{alert.unit}}</template>
                            
                        </td>
                    </tr>
            </tbody>
        </table>
    
    </div>
    </template>