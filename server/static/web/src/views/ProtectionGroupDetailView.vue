<script>
import PGAlertModal from '../components/PGAlertModal.vue'
import NetworkGraphs from '@/components/NetworkGraphs.vue';
import PGChanges from '@/components/PGChanges.vue';
import Protections from '@/components/Protections.vue';

export default {
  props: {
    pg_id: String,
  },
  components:{
    PGAlertModal,
    NetworkGraphs,
    Protections,
    PGChanges
  },
  data() {
    return {
      graph_unit: 'pps',
      pg: {},
      st: {},
      relevant_alerts_age: Date.now()/1000-(3600*24*90),
      protection_level: {
      1: 'low',
      2: 'medium',
      3: 'high'
     },
     PGAlertModalVisible: false,
     now: Date.now(),
     chart_period: '1d',
     selected_tab: 'protections',
    }
  },
  created() {
    this.getData();
    console.log(this.pg_id)
  },
  methods: {
    getData() {
      fetch('http://localhost:5000/api/protection_groups/'+this.pg_id)
        .then(response => response.json())
        .then(data => this.pg = data.data)
    },
    humanPrefixes(prefixes_arr){
        var str = ''
        for (const prefix of prefixes_arr){
            str += this.simplePrefixe(prefix)
        }
        return str
      },
      simplePrefixe(prefix){
          if (prefix.split('/')[1] == '32') return ' '+prefix.split('/')[0]
          return ' '+prefix
      },
      formatDate(dateString) {
            const date = new Date(dateString);
            return new Intl.DateTimeFormat('default', {dateStyle: 'long'}).format(date);
      },
      totalAlerts(){
        if (!('alerts' in this.pg)) return 0
        var count_total = 0
        if ('total' in this.pg['alerts']){
            for (const alert of this.pg['alerts']['total']){
                if (alert.stop_time > this.relevant_alerts_age) count_total += 1
            }
        }
        if ('automation' in this.pg['alerts']){
            for (const alert of this.pg['alerts']['automation']){
                if (alert.stop_time > this.relevant_alerts_age) count_total += 1
            }
        }
        return count_total
      },
      dropAlerts(){
        if (!('alerts' in this.pg)) return 0
        var count = 0
        if ('drop' in this.pg['alerts']){
            for (const alert of this.pg['alerts']['drop']){
                if (alert.stop_time > this.relevant_alerts_age) count += 1
            }
        }
        return count
      },
      botnetAlerts(){
        if (!('alerts' in this.pg)) return 0
        var count= 0
        if ('drop' in this.pg['alerts']){
            for (const alert of this.pg['alerts']['drop']){
                if (alert.stop_time > this.relevant_alerts_age) count += 1
            }
        }
        return count
      },
  },

}
</script>

<template>
  <div class="container-fluid">
    <PGAlertModal :alerts="pg.alerts" v-if="PGAlertModalVisible" />
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
      <div class="col"><span class="text-capitalize">{{ this.protection_level[pg.security_level] }}</span></div>
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
        <span class="text-danger" v-else-if="pg.profile_capture.stop_time*1000 < now-(86400*420*1000)">{{formatDate(pg.profile_capture.stop_time*1000)}} ({{pg.profile_capture.duration/3600}} hours)</span>
        <span class="text-warning" v-else-if="pg.profile_capture.stop_time*1000 < now-(86400*270*1000)">{{formatDate(pg.profile_capture.stop_time*1000)}}({{pg.profile_capture.duration/3600}} hours)</span>
        <span class="text-success" v-else-if="pg.profile_capture.stop_time*1000 < now-(86400*270*1000)">{{formatDate(pg.profile_capture.stop_time*1000)}} ({{pg.profile_capture.duration/3600}} hours)</span>
      </div>
    </div>
    <div class="row">
      <div class="col-3">Alerts Total Traffic:</div>
      <div class="col">{{ totalAlerts() }} <button v-if="totalAlerts() > 0" @click="PGAlertModalVisible = true" class="btn btn-sm btn-secondary">Show</button></div>
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
    </ul>
    <NetworkGraphs v-if="pg.stats && selected_tab == 'stats'" :pg_id="pg_id" />
    <Protections v-if="pg.protections && selected_tab == 'protections'" :protections="pg.protections"/>
    <PGChanges v-if="pg.server_type && selected_tab == 'changes'" :pg_id="pg_id"/>
</div>


</template>
<style>
.chart {
  height: 20em;
}
</style>