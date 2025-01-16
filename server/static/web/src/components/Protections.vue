<script setup>

const props = defineProps({
  protections: Object,
})

import { onMounted,ref } from 'vue';
import ProtectionRates from '@/components/ProtectionRates.vue';



const chart_period = ref('1d')
const graph_unit = ref('bps')
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
</script>
<template>
<div id="protections">
    <h4>AIF</h4>
    <h4>Rates</h4>
    <ProtectionRates :protections="protections" unit="pps"/>
    <ProtectionRates :protections="protections" unit="bps"/>
    <div class="row">
        <div class="col">Type</div>
        <div class="col">Low</div>
        <div class="col">Medium</div>
        <div class="col">High</div>
    </div>
    <div class="row">
        <div class="col">Main</div>
        <div class="col">
            <template v-if="protections.protectionLevels.low.zombie.bps == 0">/<br/></template>
            <template v-else>{{humanUnits(protections.protectionLevels.low.zombie.bps)}}bps</template>
            
            {{humanUnits(protections.protectionLevels.low.zombie.pps)}}pps
        </div>
        <div class="col">
            {{humanUnits(protections.protectionLevels.medium.zombie.bps)}}bps<br/>
            {{humanUnits(protections.protectionLevels.medium.zombie.pps)}}pps
            <span v-if="protections.protectionLevels.medium.zombie.bps != 0 && protections.protectionLevels.medium.zombie.pps != 0"><br/>AVG Size: {{ protections.protectionLevels.medium.zombie.bps/(protections.protectionLevels.medium.zombie.pps*8) }}B</span>
        </div>
        <div class="col">
            {{humanUnits(protections.protectionLevels.high.zombie.bps)}}bps<br/>
            {{humanUnits(protections.protectionLevels.high.zombie.pps)}}pps
            <span v-if="protections.protectionLevels.high.zombie.bps != 0 && protections.protectionLevels.high.zombie.pps != 0"><br/>AVG Size: {{ protections.protectionLevels.high.zombie.bps/(protections.protectionLevels.high.zombie.pps*8) }}B</span>
        </div>
    </div>
    <div class="row mt-2">
        <div class="col">UDP</div>
        <div class="col">
            {{humanUnits(protections.protectionLevels.low.udpFlood.bps)}}bps<br/>
            {{humanUnits(protections.protectionLevels.low.udpFlood.pps)}}pps
            <span v-if="protections.protectionLevels.low.udpFlood.bps != 0 && protections.protectionLevels.low.udpFlood.pps != 0"><br/>AVG Size: {{ protections.protectionLevels.low.udpFlood.bps/(protections.protectionLevels.low.udpFlood.pps*8) }}B</span>
        </div>
        <div class="col">
            {{humanUnits(protections.protectionLevels.medium.udpFlood.bps)}}bps<br/>
            {{humanUnits(protections.protectionLevels.medium.udpFlood.pps)}}pps
            <span v-if="protections.protectionLevels.medium.udpFlood.bps != 0 && protections.protectionLevels.medium.udpFlood.pps != 0"><br/>AVG Size: {{ protections.protectionLevels.medium.udpFlood.bps/(protections.protectionLevels.medium.udpFlood.pps*8) }}B</span>
        </div>
        <div class="col">
            {{humanUnits(protections.protectionLevels.high.udpFlood.bps)}}bps<br/>
            {{humanUnits(protections.protectionLevels.high.udpFlood.pps)}}pps
            <span v-if="protections.protectionLevels.high.udpFlood.bps != 0 && protections.protectionLevels.high.udpFlood.pps != 0"><br/>AVG Size: {{ protections.protectionLevels.high.udpFlood.bps/(protections.protectionLevels.high.udpFlood.pps*8) }}B</span>
        </div>
        
    </div>
    <div class="row mt-2">
        <div class="col">ICMP</div>
        <div class="col">
            {{humanUnits(protections.protectionLevels.low.detectIcmp.bps)}}bps<br/>
            {{humanUnits(protections.protectionLevels.low.detectIcmp.pps)}}pps
            <span v-if="protections.protectionLevels.low.detectIcmp.bps != 0 && protections.protectionLevels.low.detectIcmp.pps != 0"><br/>AVG Size: {{ protections.protectionLevels.low.detectIcmp.bps/(protections.protectionLevels.low.detectIcmp.pps*8) }}B</span>
        </div>
        <div class="col">
            {{humanUnits(protections.protectionLevels.medium.detectIcmp.bps)}}bps<br/>
            {{humanUnits(protections.protectionLevels.medium.detectIcmp.pps)}}pps
            <span v-if="protections.protectionLevels.medium.detectIcmp.bps != 0 && protections.protectionLevels.medium.detectIcmp.pps != 0"><br/>AVG Size: {{ protections.protectionLevels.medium.detectIcmp.bps/(protections.protectionLevels.medium.detectIcmp.pps*8) }}B</span>
        </div>
        <div class="col">
            {{humanUnits(protections.protectionLevels.high.detectIcmp.bps)}}bps<br/>
            {{humanUnits(protections.protectionLevels.high.detectIcmp.pps)}}pps
            <span v-if="protections.protectionLevels.high.detectIcmp.bps != 0 && protections.protectionLevels.high.detectIcmp.pps != 0"><br/>AVG Size: {{ protections.protectionLevels.high.detectIcmp.bps/(protections.protectionLevels.high.detectIcmp.pps*8) }}B</span>
        </div>
        
    </div>
    <div class="row mt-2">
        <div class="col">Fragment</div>
        <div class="col">
            {{humanUnits(protections.protectionLevels.low.fragmentation.bps)}}bps<br/>
            {{humanUnits(protections.protectionLevels.low.fragmentation.pps)}}pps
            <span v-if="protections.protectionLevels.low.fragmentation.bps != 0 && protections.protectionLevels.low.fragmentation.pps != 0"><br/>AVG Size: {{ protections.protectionLevels.low.fragmentation.bps/(protections.protectionLevels.low.fragmentation.pps*8) }}B</span>
        </div>
        <div class="col">
            {{humanUnits(protections.protectionLevels.medium.fragmentation.bps)}}bps<br/>
            {{humanUnits(protections.protectionLevels.medium.fragmentation.pps)}}pps
            <span v-if="protections.protectionLevels.medium.fragmentation.bps != 0 && protections.protectionLevels.medium.fragmentation.pps != 0"><br/>AVG Size: {{ protections.protectionLevels.medium.fragmentation.bps/(protections.protectionLevels.medium.fragmentation.pps*8) }}B</span>
        </div>
        <div class="col">
            {{humanUnits(protections.protectionLevels.high.fragmentation.bps)}}bps<br/>
            {{humanUnits(protections.protectionLevels.high.fragmentation.pps)}}pps
            <span v-if="protections.protectionLevels.high.fragmentation.bps != 0 && protections.protectionLevels.high.fragmentation.pps != 0"><br/>AVG Size: {{ protections.protectionLevels.high.fragmentation.bps/(protections.protectionLevels.high.fragmentation.pps*8) }}B</span>
        </div>
        
    </div>

    <h4>TCP</h4>

</div>
</template>