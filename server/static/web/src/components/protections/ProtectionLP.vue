<script setup>

import { onMounted,ref } from 'vue';
import TrafficLocation from '@/components/TrafficLocation.vue';

const props = defineProps({
  protections: Object,
  levels: Array,
  pg_id: String
})
function CountryArray(){
    var countries = []
    for (const level of props.levels){
        if (!('countries' in props.protections['protectionLevels'][level]['ipLocationPolicing'])) continue
        
        for (const country of props.protections['protectionLevels'][level]['ipLocationPolicing']['countries']){
            console.log(country)
            if (!(country['country'] in countries)) countries.push(country['country'])
        }
    }
    return countries
}

const chart_period = ref('1d')
const graph_unit = ref('pps')
const locations = ref({})
function loadPeriod(new_chart_period){
    chart_period.value = new_chart_period
    fetch('http://localhost:5000/aed_reviewer/api/protection_groups/'+props.pg_id+'/traffic_locations/'+chart_period.value)
    .then(response => response.json())
    .then(data => locations.value = data)
}
onMounted(() => {
    loadPeriod(chart_period.value)
})

</script>
<template>

    <div class="container-fluid px-5 mt-2">
        {{ CountryArray() }}
        <table class="table table-hover table-striped table-sm">
            <thead>
                <tr>
                    <th scope="col"></th>
                    <th scope="col" v-for="level in levels">
                        <span class="text-capitalize">{{ level }}</span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr class="text-capitalize">
                    <th>Enabled</th>
                    <td v-for="level in levels" :class="protections['protectionLevels'][level]['ipLocationPolicing']['enabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['ipLocationPolicing']['enabled'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Other</th>
                    <td v-for="level in levels" ><template v-if="protections['protectionLevels'][level]['ipLocationPolicing']['enabled']">{{ protections['protectionLevels'][level]['ipLocationPolicing']['otherAction'] }}</template></td>
                </tr>
                <tr class="text-capitalize">
                    <th>PPS rate</th>
                    <td v-for="level in levels" >{{ protections['protectionLevels'][level]['ipLocationPolicing']['otherPps'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>BPS rate</th>
                    <td v-for="level in levels" >{{ protections['protectionLevels'][level]['ipLocationPolicing']['otherBps'] }}</td>
                </tr>
            </tbody>
        </table>
        
        <table class="table table-hover table-striped table-sm">
            <thead>
                <tr>
                    <th scope="col"></th>
                    <th scope="col" v-for="level in levels">
                        <span class="text-capitalize">{{ level }}</span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="country in CountryArray()">
                    <th>{{country}}</th>
                    <td v-for="level in levels">
                        <template v-for="item in props.protections['protectionLevels'][level]['ipLocationPolicing']['countries']">
                            <template v-if="item['country'] == country">
                                <span v-if="item['allow'] == false" class="text-danger">Drop</span>
                                <span v-else>
                                    <span v-if="item['pps'] || item['bps']" class="text-warning">Rate 
                                        <span v-if="item['pps']">{{item['pps']}} PPS</span>
                                        <span v-if="item['bps']"><template v-if="item['pps']">,</template> {{item['bps']}} BPS</span>
                                    </span>
                                    <span v-else class="text-success">Allow All</span>
                                    
                                </span>
                            </template>
                        </template>
                    </td>
                </tr>
            </tbody>
        </table>
        <TrafficLocation title_str="Location" v-if="locations" :data="locations" :unit="graph_unit"/>
    </div>
    
</template>