<script>
import Thresholds from '@/components/Thresholds.vue';
export default {
  components: {
    Thresholds
  },
  data() {
    return {
      pgs: {},
      sts: {},
      prefixes_expanded: {},
      prefixes_max_lenght: 6,
      search_keyword: '',
      relevant_alerts_age: Date.now()/1000-(3600*24*90),
      global_alerting: {},
      units : [
      "k",
      "M",
      "G",
    ],
     protection_level: {
      1: 'low',
      2: 'medium',
      3: 'high'
     }
    }
  },
  created() {
    this.getPGs();
    this.getSTs();
    this.getGA();
  },
  methods: {
    getPGs() {
      fetch('http://localhost:5000/aed_reviewer/api/protection_groups')
        .then(response => response.json())
        .then(data => this.pgs = data)
    },
    getSTs() {
      fetch('http://localhost:5000/aed_reviewer/api/server_types')
        .then(response => response.json())
        .then(data => this.sts = data)
    },
    getGA() {
      fetch('http://localhost:5000/aed_reviewer/api/global_alerting')
        .then(response => response.json())
        .then(data => this.global_alerting = data)
    },
    humanAlert(pg){
        if (!('alerts' in pg)) return '0'
        var count_total = 0
        if ('total' in pg['alerts']){
            for (const alert of pg['alerts']['total']){
                if (alert.stop_time > this.relevant_alerts_age) count_total += 1
            }
        }
        if ('automation' in pg['alerts']){
            for (const alert of pg['alerts']['automation']){
                if (alert.stop_time > this.relevant_alerts_age) count_total += 1
            }
        }
        var count_drop = 0
        if ('drop' in pg['alerts']){
            for (const alert of pg['alerts']['drop']){
                if (alert.stop_time > this.relevant_alerts_age) count_drop += 1
            }
        }
        var count_botnet = 0
        if ('botnet' in pg['alerts']){
            for (const alert of pg['alerts']['botnet']){
                if (alert.stop_time > this.relevant_alerts_age) count_botnet += 1
            }
        }
        return count_total+' / '+count_drop+' / '+count_botnet
    },
    simplePrefixe(prefix){
        if (prefix.split('/')[1] == '32') return ' '+prefix.split('/')[0]
        return ' '+prefix
    },

    humanPrefixes(prefixes_arr, pg_id){
        var str = ''
        if (prefixes_arr.length < this.prefixes_max_lenght || pg_id in this.prefixes_expanded){  
            for (const prefix of prefixes_arr){
                str += this.simplePrefixe(prefix)
            }
            return str
        }
        for (const prefix of prefixes_arr.slice(0, this.prefixes_max_lenght)){
                str += this.simplePrefixe(prefix)
            }
        return str
    },
    prefixesExpandedToogle(pg_id){
        if (pg_id in this.prefixes_expanded){
            delete this.prefixes_expanded[pg_id]
            return
        }
        this.prefixes_expanded[pg_id] = true
    },
    lengthArr(arr){
        return arr.length
    },
    round(value, digits=0){
      return Math.round(value*10^digits)/10^digits
    },
    KeyInObj(key, obj){
        if (key in obj) return true
        return false
    },
    IPnumber(IPaddress) {
        var ip = IPaddress.match(/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/);
        if(ip) {
            return (+ip[1]<<24) + (+ip[2]<<16) + (+ip[3]<<8) + (+ip[4]);
        }
        // else ... ?
        return null;
    },
    IPmask(maskSize) {
        return -1<<(32-maskSize)
    },

    alertRatioColor(ratio){
      if (ratio > 350) return 'text-danger'
      if (ratio > 150) return 'text-warning'
      return ''
    },
    humanUnits(value){
      if (value < 1000) return Math.max(value)
      let i = -1;
      do {
        value = value / 1000;
        i++;
      } while (value >= 1000);
      return Math.max(value).toFixed(1) + this.units[i];
    }
  },
  computed: {
    f_pgs(){
        if (this.search_keyword == '') return this.pgs
        const search_keyword = this.search_keyword.toLowerCase();
        
        var pgs_f = {}
        const ipNumSearch = this.IPnumber(this.search_keyword)
        if (ipNumSearch == null){
            for (const [pg_id, pg] of Object.entries(this.pgs)){
                if (Object.values(pg).toString().toLowerCase().includes(search_keyword)){
                    pgs_f[pg_id] = pg
                    continue
                }
            }
            return pgs_f
        }
        console.log('Search contains an IP')
        for (const [pg_id, pg] of Object.entries(this.pgs)){
          for (const prefix of pg.prefixes){
            if ((ipNumSearch & this.IPmask(prefix.split('/')[1])) == this.IPnumber(prefix.split('/')[0])){
                console.log(prefix)
                pgs_f[pg_id] = pg
                break
            }
          }
        }
        return pgs_f
      },
  }
}
</script>

<template>
<div>
    <div class="container">
        <div class="row">
                <div class="col-5">
                    <div class="input-group">
                        <input type="search" ref="search" class="form-control" id="SearchInput" placeholder="Search.." v-model="search_keyword" aria-describedby="button-clear-search">
                        <span class="input-group-text" id="button-clear-search" @click="search_keyword = '', $refs.search.focus();">X</span>
                    </div>
                </div>
            </div>
    </div>
    
    
<table class="table">
  <thead>
    <tr>
      <th scope="col">#</th>
      <th scope="col">Name</th>
      <th scope="col">Prefixes</th>
      <th scope="col">Level</th>
      <th scope="col">Alerts (T/D/B)</th>
      <th scope="col">Thresholds</th>
      <th scope="col">Warnings</th>
      <th scope="col">Details</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="(pg, pg_id) in f_pgs">
      <th scope="row">{{pg_id}}</th>
      <td><RouterLink class="text-dark" :to="'/protection-groups/'+pg_id">{{pg.name}}</RouterLink></td>
      <td>
        {{humanPrefixes(pg.prefixes, pg_id)}}
        <span v-if="lengthArr(pg.prefixes) > prefixes_max_lenght" @click="prefixesExpandedToogle(pg_id)">
            <template v-if="!KeyInObj(pg_id, this.prefixes_expanded)"><BIconArrowDown />({{lengthArr(pg.prefixes)-prefixes_max_lenght }})</template>
            <template v-else><BIconArrowUp /></template>
        </span>
      </td>
      <td><span class="text-capitalize">{{ pg.protection_level_human }}</span></td>
      <td>{{humanAlert(pg)}}</td>
      <td >
        {{ pg.alert_thresholds.total.mode}}<br/>
        <Thresholds v-if="pg.alert_thresholds" :alert_thresholds="pg.alert_thresholds" :global_alerting="global_alerting"/>
      </td>
      <td>Otto</td>
      <td>@mdo</td>
    </tr>
  </tbody>
</table>
</div>
</template>