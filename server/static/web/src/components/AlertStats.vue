<script setup>
import { ref, onMounted, computed } from 'vue';
import { humanUnits } from '@/composables/helpers';

const props = defineProps({
    alert_thresholds: Object,
    protection_levels: Object,
})

const global_alerting = ref({})
const pg_extra = ref({})
function getGA() {
    fetch('http://localhost:5000/aed_reviewer/api/global_alerting')
    .then(response => response.json())
    .then(data => global_alerting.value = data)
    // .then(addAlertThreshold())
}
// function addAlertThreshold(){
//     console.log('running addAlertThreshold')
//     console.log(global_alerting)
//     if (['auto_level_static','alert_static'].includes(props.alert_thresholds.total.mode)){
//         pg_extra.value.calcultated_total_pps = props.alert_thresholds.total.pps
//         pg_extra.value.calcultated_total_pps_ratio = Math.round(props.alert_thresholds.total.pps/props.alert_thresholds.total.baseline.pps*100)
//         pg_extra.value.calcultated_total_bps = props.alert_thresholds.total.bps
//         pg_extra.value.calcultated_total_bps_ratio = Math.round(props.alert_thresholds.total.bps/props.alert_thresholds.total.baseline.bps*100)
//         return
//     }
//     if (global_alerting.value.total.enabled === false){
//         pg_extra.value.calcultated_total_pps = null
//         pg_extra.value.calcultated_total_bps = null
//         return
//     }
//     const calcultated_total_pps = props.alert_thresholds.total.baseline.pps * global_alerting.value.total.percent/100
//     console.log(calcultated_total_pps)
//     // PPS
//     if (calcultated_total_pps > global_alerting.value.total.ignore_pps){
//     pg_extra.value.calcultated_total_pps = calcultated_total_pps
//     pg_extra.value.calcultated_total_pps_ratio = global_alerting.value.total.percent
//     }
//     else {
//     pg_extra.value.calcultated_total_pps = global_alerting.value.total.ignore_pps
//     if(global_alerting.value.total.ignore_pps/props.alert_thresholds.total.baseline.pps > 9999){
//         pg_extra.value.calcultated_total_pps_ratio = 999999
//     } else {
//         pg_extra.value.calcultated_total_pps_ratio = Math.round(global_alerting.value.total.ignore_pps/props.alert_thresholds.total.baseline.pps*100)
//     }
//     }
//     // BPS
//     const calcultated_total_bps = props.alert_thresholds.total.baseline.bps * global_alerting.value.total.percent/100
//     if (calcultated_total_bps > global_alerting.value.total.ignore_bps){
//     pg_extra.value.calcultated_total_bps = calcultated_total_bps
//     pg_extra.value.calcultated_total_bps_ratio = global_alerting.value.total.percent
//     }
//     else {
//     pg_extra.value.calcultated_total_bps = global_alerting.value.total.ignore_bps
//     if(global_alerting.value.total.ignore_bps/props.alert_thresholds.total.baseline.bps > 9999){
//         pg_extra.value.calcultated_total_bps_ratio = 999999
//     } else {
//         pg_extra.value.calcultated_total_bps_ratio = Math.round(global_alerting.value.total.ignore_bps/props.alert_thresholds.total.baseline.bps*100)
//     }
//     }
// }

function alertRatioColor(ratio){
    if (ratio > 350) return 'text-danger'
    if (ratio > 150) return 'text-warning'
    return ''
}

onMounted(() => {
  getGA()
})

const calcultated_total = computed(() => {
    console.log('Running calcultated_total')
    var calculated = {'pps': null, 'bps': null}
    if (['auto_level_static','alert_static'].includes(props.alert_thresholds.total.mode)){
        calculated['pps'] = props.alert_thresholds.total.pps
        calculated['bps'] = props.alert_thresholds.total.bps
        calculated['pps_ratio'] = Math.round(props.alert_thresholds.total.pps/props.alert_thresholds.total.baseline.pps*100)
        calculated['bps_ratio'] = Math.round(props.alert_thresholds.total.bps/props.alert_thresholds.total.baseline.bps*100)
    }
    else if (global_alerting.value.total.enabled === false) return calculated
    else {
        const calcultated_total_pps = props.alert_thresholds.total.baseline.pps * global_alerting.value.total.percent/100
        // PPS
        if (calcultated_total_pps > global_alerting.value.total.ignore_pps){
            calculated['pps'] = calcultated_total_pps
            calculated['pps_ratio'] = global_alerting.value.total.percent
        }
        else {
            calculated['pps'] = global_alerting.value.total.ignore_pps
            if (global_alerting.value.total.ignore_pps/props.alert_thresholds.total.baseline.pps > 9999){
                calculated['pps_ratio'] = 999999
            } else {
                calculated['pps_ratio'] = Math.round(global_alerting.value.total.ignore_pps/props.alert_thresholds.total.baseline.pps*100)
            }
        }
        // BPS
        const calcultated_total_bps = props.alert_thresholds.total.baseline.bps * global_alerting.value.total.percent/100
        if (calcultated_total_bps > global_alerting.value.total.ignore_bps){
            calculated['bps'] = calcultated_total_bps
            calculated['bps_ratio'] = global_alerting.value.total.percent
        }
        else {
            calculated['bps'] = global_alerting.value.total.ignore_bps
            if (global_alerting.value.total.ignore_bps/props.alert_thresholds.total.baseline.bps > 9999){
                calculated['bps_ratio'] = 999999
            } else {
                calculated['bps_ratio'] = Math.round(global_alerting.value.total.ignore_bps/props.alert_thresholds.total.baseline.bps*100)
            }
        }
    }
    

    return calculated

})

</script>

<template>
  <template v-if="global_alerting.total">
    <span :class="calcultated_total['pps'] == global_alerting.total.ignore_pps ? 'text-primary': ''">{{humanUnits(calcultated_total['pps'])}}pps </span><span :class="alertRatioColor(calcultated_total['pps_ratio'])">({{calcultated_total['pps_ratio'] }}%)</span><br/>
    <span :class="calcultated_total['bps'] == global_alerting.total.ignore_bps ? 'text-primary': ''">{{humanUnits(calcultated_total['bps'])}}bps </span><span :class="alertRatioColor(calcultated_total['bps_ratio'])">({{calcultated_total['bps_ratio'] }}%)</span><br/>  </template>
</template>