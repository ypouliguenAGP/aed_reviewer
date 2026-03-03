<script setup>
import { computed } from 'vue';
import { humanUnits } from '../composables/helpers';

const props = defineProps({
    alert_thresholds: Object,
    global_alerting: Object,
})


function alertRatioColor(ratio){
    if (ratio > 350) return 'text-danger'
    if (ratio > 150) return 'text-warning'
    return ''
}

const calcultated_total = computed(() => {
    console.log('Running calcultated_total')
    var calculated = {'pps': null, 'bps': null}
    if (['auto_level_static','alert_static'].includes(props.alert_thresholds.total.mode)){
        calculated['pps'] = props.alert_thresholds.total.pps
        calculated['bps'] = props.alert_thresholds.total.bps
        calculated['pps_ratio'] = Math.round(props.alert_thresholds.total.pps/props.alert_thresholds.total.baseline.pps*100)
        calculated['bps_ratio'] = Math.round(props.alert_thresholds.total.bps/props.alert_thresholds.total.baseline.bps*100)
    }
    else if (props.global_alerting.total.enabled === false) return calculated
    else {
        const calcultated_total_pps = props.alert_thresholds.total.baseline.pps * props.global_alerting.total.percent/100
        // PPS
        if (calcultated_total_pps > props.global_alerting.total.ignore_pps){
            calculated['pps'] = calcultated_total_pps
            calculated['pps_ratio'] = props.global_alerting.total.percent
        }
        else {
            calculated['pps'] = props.global_alerting.total.ignore_pps
            if (props.global_alerting.total.ignore_pps/props.alert_thresholds.total.baseline.pps > 9999){
                calculated['pps_ratio'] = 999999
            } else {
                calculated['pps_ratio'] = Math.round(props.global_alerting.total.ignore_pps/props.alert_thresholds.total.baseline.pps*100)
            }
        }
        // BPS
        const calcultated_total_bps = props.alert_thresholds.total.baseline.bps * props.global_alerting.total.percent/100
        if (calcultated_total_bps > props.global_alerting.total.ignore_bps){
            calculated['bps'] = calcultated_total_bps
            calculated['bps_ratio'] = props.global_alerting.total.percent
        }
        else {
            calculated['bps'] = props.global_alerting.total.ignore_bps
            if (props.global_alerting.total.ignore_bps/props.alert_thresholds.total.baseline.bps > 9999){
                calculated['bps_ratio'] = 999999
            } else {
                calculated['bps_ratio'] = Math.round(props.global_alerting.total.ignore_bps/props.alert_thresholds.total.baseline.bps*100)
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