<script setup>

const props = defineProps({
  pg_id: String,
})
import PGAlertModal from '../components/PGAlertModal.vue'
import NetworkGraphs from '@/components/NetworkGraphs.vue';
import PGAlerts from '@/components/PGAlerts.vue';
import PGChanges from '@/components/PGChanges.vue';
import PGDumps from '@/components/PGDumps.vue';
import PGDumpStats from '@/components/PGDumpStats.vue';
import Protections from '@/components/Protections.vue';
import { useSimplePrefixe } from '@/composables/ips.js';
import { useFormatDate } from '@/composables/helpers.js';
import { ref, onMounted } from 'vue'

var graph_unit = ref('pps')
const pg = ref({})
const relevant_alerts_age = ref(Date.now()/1000-(3600*24*120)) // 120 Days
const protection_levels = ref({
  1: 'low',
  2: 'medium',
  3: 'high'
})
const now = ref(Date.now())
var chart_period = ref('1d')
var selected_tab = ref('protections')

function getData() {
    fetch('http://localhost:5000/api/protection_groups/'+props.pg_id)
      .then(response => response.json())
      .then(data => pg.value = data.data)
}

function humanPrefixes(prefixes_arr){
  var str = ''
  for (const prefix of prefixes_arr){
      str += useSimplePrefixe(prefix)
  }
  return str
}




function totalAlerts(){
  if (!('alerts' in pg.value)) return 0
  var count_total = 0
  if ('total' in pg.value['alerts']){
      for (const alert of pg.value['alerts']['total']){
          if (alert.stop_time > relevant_alerts_age.value) count_total += 1
      }
  }
  if ('automation' in pg.value['alerts']){
      for (const alert of pg.value['alerts']['automation']){
          if (alert.stop_time > relevant_alerts_age.value) count_total += 1
      }
  }
  return count_total
}
function dropAlerts(){
  if (!('alerts' in pg.value)) return 0
  var count = 0
  if ('drop' in pg.value['alerts']){
      for (const alert of pg.value['alerts']['drop']){
          if (alert.stop_time > relevant_alerts_age.value) count += 1
      }
  }
  return count
}

function botnetAlerts(){
  if (!('alerts' in pg.value)) return 0
  var count= 0
  if ('drop' in pg.value['alerts']){
      for (const alert of pg.value['alerts']['drop']){
          if (alert.stop_time > relevant_alerts_age.value) count += 1
      }
  }
  return count
}

onMounted(() => {
  getData()
})
</script>

<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-3">Name:</div>
      <div class="col">{{ pg.name }}</div>
    </div>
    <div class="row" v-if="pg.protections">
      <div class="col-3">Protection:</div>
      <div class="col">{{ pg.protections.serverName }} ({{ pg.server_type }})</div>
    </div>
    <div class="row" v-if="pg.prefixes">
      <div class="col-3">Prefixes:</div>
      <div class="col">{{ humanPrefixes(pg.prefixes) }}</div>
    </div>
    <div class="row">
      <div class="col-3">Level:</div>
      <div class="col"><span class="text-capitalize">{{ protection_levels[pg.security_level] }}</span></div>
    </div><div class="row">
      <div class="col-3">Mode:</div>
      <div class="col"><span class="text-capitalize">
        <span class="text-success" v-if="pg.active">Active</span>
        <span class="text-danger" v-else>Inactive</span>
      </span></div>
    </div>
    <div class="row">
      <div class="col-3">Profile Capture:</div>
      <div class="col">
        <span class="text-danger" v-if="pg.profile_capture == null">Never</span>
        <span class="text-success" v-else-if="pg.profile_capture.ongoing">Ongoing</span>
        <span class="text-danger" v-else-if="pg.profile_capture.stop_time*1000 < now-(86400*420*1000)">{{useFormatDate(pg.profile_capture.stop_time*1000)}} ({{pg.profile_capture.duration/3600}} hours)</span>
        <span class="text-warning" v-else-if="pg.profile_capture.stop_time*1000 < now-(86400*270*1000)">{{useFormatDate(pg.profile_capture.stop_time*1000)}}({{pg.profile_capture.duration/3600}} hours)</span>
        <span class="text-success" v-else-if="pg.profile_capture.stop_time*1000 < now-(86400*270*1000)">{{useFormatDate(pg.profile_capture.stop_time*1000)}} ({{pg.profile_capture.duration/3600}} hours)</span>
      </div>
    </div>
    <div class="row">
      <div class="col-3">Alerts Total Traffic:</div>
      <div class="col">{{ totalAlerts() }}</div>
    </div>
    <div class="row">
      <div class="col-3">Alerts Drop Traffic:</div>
      <div class="col">{{ dropAlerts() }}</div>
    </div>
    <div class="row">
      <div class="col-3">Alerts Botnet Traffic:</div>
      <div class="col">{{ botnetAlerts() }}</div>
    </div>
    <ul class="nav nav-tabs">
      <li class="nav-item">
        <a class="nav-link" :disabled="!pg.stats" :class="selected_tab == 'stats' ? 'active': ''" href="#" @click="selected_tab = 'stats'">Statistics</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="selected_tab == 'protections' ? 'active': ''" href="#" @click="selected_tab = 'protections'">Protections</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="selected_tab == 'changes' ? 'active': ''" href="#" @click="selected_tab = 'changes'">Changes</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="selected_tab == 'alerts' ? 'active': ''" href="#" @click="selected_tab = 'alerts'">Alerts</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="selected_tab == 'dumps' ? 'active': ''" href="#" @click="selected_tab = 'dumps'">Dumps</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="selected_tab == 'dump_stats' ? 'active': ''" href="#" @click="selected_tab = 'dump_stats'">Dump Stats</a>
      </li>
    </ul>
    <NetworkGraphs v-if="pg.stats && selected_tab == 'stats'" :pg_id="pg_id" />
    <Protections v-if="pg.protections && selected_tab == 'protections'" :protections="pg.protections"/>
    <PGChanges v-if="pg.server_type && selected_tab == 'changes'" :pg_id="pg_id"/>
    <PGAlerts v-if="pg.alerts && selected_tab == 'alerts'" :alerts="pg.alerts"/>
    <PGDumps v-if="pg.stats && selected_tab == 'dumps'" :pg_id="pg_id"/>
    <PGDumpStats v-if="pg.stats && selected_tab == 'dump_stats'" :pg_id="pg_id"/>
</div>


</template>

<style>
.chart {
  height: 20em;
}
</style>