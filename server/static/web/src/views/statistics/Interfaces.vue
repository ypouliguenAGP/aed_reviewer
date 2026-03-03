<script setup>

const props = defineProps({
  aed_id: String,
})

import { onMounted,ref } from 'vue';
import InterfaceGraph from '../../components/statistics/InterfaceGraph.vue';
import InterfacePairGraph from '../../components/statistics/InterfacePairGraph.vue';
import InterfaceCombined from '../../components/statistics/InterfaceCombined.vue';

const graph_unit = ref('pps')
const ifaces = ref([])
const selected_tab = ref('per_interface')


// Retrieve list of interfaces
function loadInterfaces(){
    fetch(`/aed_reviewer/api/${props.aed_id}/statusdump/interfaces`)
      .then(response => response.json())
      .then(data => {
        ifaces.value = reorderInterfaces(data.data)
        console.log('interfaces retrieved:', ifaces.value)
      })
      .catch(err => console.error('loadInterfaces error:', err))
}

// Function to reorder interface, such as ext0,int0,ext1,int1,...
function reorderInterfaces(interfaces) {
    let ext_ifaces = interfaces.filter(i => i.startsWith('ext'));
    let int_ifaces = interfaces.filter(i => i.startsWith('int'));
    let other_ifaces = interfaces.filter(i => !i.startsWith('ext') && !i.startsWith('int'));
    let reordered = [];
    let maxLength = Math.max(ext_ifaces.length, int_ifaces.length);
    for (let i = 0; i < maxLength; i++) {
        if (i < ext_ifaces.length) {
            reordered.push(ext_ifaces[i]);
        }
        if (i < int_ifaces.length) {
            reordered.push(int_ifaces[i]);
        }
    }
    return reordered.concat(other_ifaces);
}

// Function to list the pairs of interfaces (ext0/int0 --> 0, ext1/int1 --> 1, ...)
function getInterfacePairs(interfaces) {
    let pairs = new Set();
    interfaces.forEach(iface => {
        let match = iface.match(/(ext|int)(\d+)/);
        if (match) {
            pairs.add(match[2]);
        }
    });
    return Array.from(pairs).sort((a, b) => a - b);
}

onMounted(() => {
    loadInterfaces()
})
</script>


<template>
    <div id="network-graphs" class="mt-2">
        <div class="row mb-2">
            <div class="col">
            </div>
            <div class="col">
            <ul class="nav nav-pills nav-fill nav-pills-sm">
                <li class="nav-item">
                <button class="nav-link" :class="graph_unit == 'pps' ? 'active': ''" @click="graph_unit='pps'">PPS</button>
                </li>
                <li class="nav-item">
                <button class="nav-link" :class="graph_unit == 'bps' ? 'active': ''" @click="graph_unit='bps'">BPS</button>
                </li>
            </ul>
            </div>
        </div>
        <ul class="nav nav-tabs">
          <li class="nav-item">
            <a class="nav-link" :class="selected_tab == 'per_interface' ? 'active': ''" href="#" @click="selected_tab = 'per_interface'">Per Interface</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="selected_tab == 'per_pair' ? 'active': ''" href="#" @click="selected_tab = 'per_pair'">Per Pair</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="selected_tab == 'combined' ? 'active': ''" href="#" @click="selected_tab = 'combined'">Combined</a>
          </li>
        </ul>
        <div v-if="selected_tab == 'per_interface'" v-for="iface in ifaces">
          <InterfaceGraph :iface="iface" :aed_id="aed_id" :graph_unit="graph_unit" />
        </div>
        <div v-else-if="selected_tab == 'per_pair'" v-for="pair in getInterfacePairs(ifaces)">
          <InterfacePairGraph :pair="pair" :aed_id="aed_id" :graph_unit="graph_unit" />
        </div>
        <div v-else-if="selected_tab == 'combined'">
          <InterfaceCombined :aed_id="aed_id" :graph_unit="graph_unit" />
        </div>
    </div>
</template>


<style>
.chart {
  height: 20em;
}
</style>
