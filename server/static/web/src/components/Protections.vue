<script setup>

const props = defineProps({
  protections: Object,
  pg_id: String
})

import { onMounted,ref } from 'vue';
import ProtectionRates from '@/components/protections/ProtectionRates.vue';
import ProtectionFL from './protections/ProtectionFL.vue';
import ProtectionAIF from './protections/ProtectionAIF.vue';
import ProtectionTCP from './protections/ProtectionTCP.vue';
import ProtectionTLS from './protections/ProtectionTLS.vue';
import ProtectionLP from './protections/ProtectionLP.vue';
import ProtectionUDP from './protections/ProtectionUDP.vue';
import ProtectionShaping from './protections/ProtectionShaping.vue';
const levels = ref(['low','medium','high'])
const selected_tab = ref('rates')


</script>
<template>
<div id="protections" class="mt-3">
    <ul class="nav nav-tabs">
      <li class="nav-item">
        <a class="nav-link" :class="selected_tab == 'filter_list' ? 'active': ''" href="#" @click="selected_tab = 'filter_list'">Filter List</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="selected_tab == 'aif' ? 'active': ''" href="#" @click="selected_tab = 'aif'">AIF</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="selected_tab == 'rates' ? 'active': ''" href="#" @click="selected_tab = 'rates'">Rates</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="selected_tab == 'tcp' ? 'active': ''" href="#" @click="selected_tab = 'tcp'">TCP</a>
      </li>
      <li class="nav-item" v-if="protections['protectionLevels']['low']['dnsMalform']">
        <a class="nav-link" :class="selected_tab == 'udp' ? 'active': ''" href="#" @click="selected_tab = 'udp'">UDP</a>
      </li>
      <li class="nav-item" v-if="protections['protectionLevels']['low']['tlsMalformed']">
        <a class="nav-link" :class="selected_tab == 'tls' ? 'active': ''" href="#" @click="selected_tab = 'tls'">TLS</a>
      </li>
      <li class="nav-item" v-if="protections['protectionLevels']['low']['shaping']">
        <a class="nav-link" :class="selected_tab == 'shaping' ? 'active': ''" href="#" @click="selected_tab = 'shaping'">Shaping</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="selected_tab == 'location_policing' ? 'active': ''" href="#" @click="selected_tab = 'location_policing'">IP Location Policing</a>
      </li>
    </ul>
    <div v-if="selected_tab == 'filter_list'">
        <ProtectionFL :levels="levels" :protections="protections"/>
    </div>
    <div v-if="selected_tab == 'aif'">
        <ProtectionAIF :levels="levels" :protections="protections"/>
    </div>
    <div v-if="selected_tab == 'tcp'">
        <ProtectionTCP :levels="levels" :protections="protections"/>
    </div>
    <div v-if="selected_tab == 'udp'">
        <ProtectionUDP :levels="levels" :protections="protections"/>
    </div>
    <div v-if="selected_tab == 'tls'">
        <ProtectionTLS :levels="levels" :protections="protections"/>
    </div>
    <div v-if="selected_tab == 'shaping'">
        <ProtectionShaping :levels="levels" :protections="protections" />
    </div>
    <div v-if="selected_tab == 'location_policing'">
        <ProtectionLP :levels="levels" :protections="protections" :pg_id="pg_id"/>
    </div>
    
    <div v-if="selected_tab == 'rates'">
        <div class="row">
            <div class="col col-12 col-xl-6">
                <ProtectionRates :protections="protections" unit="pps"/>
            </div>
            <div class="col col-12 col-xl-6">
                <ProtectionRates :protections="protections" unit="bps"/>
            </div>
        </div>
        <div v-if="protections['protectionLevels']['common']['zombie']['flexible']['1']['filter'].length > 0 || protections['protectionLevels']['common']['zombie']['flexible']['2']['filter'].length > 0">
            <h4>Flexibles</h4>
        
            <table class="table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Description</th>
                        <th>Filter</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-if="protections['protectionLevels']['common']['zombie']['flexible']['1']['filter'].length > 0">
                        <th>1</th>
                        <td>{{protections['protectionLevels']['common']['zombie']['flexible']['1']['description']}}</td>
                        <td class="fw-light">
                            <span v-for="statement in protections['protectionLevels']['common']['zombie']['flexible']['1']['filter']">
                                {{ statement }}<br/>
                            </span>{{}}
                        </td>
                    </tr>
                    <tr v-if="protections['protectionLevels']['common']['zombie']['flexible']['2']['filter'].length > 0">
                        <th>2</th>
                        <td>{{protections['protectionLevels']['common']['zombie']['flexible']['2']['description']}}</td>
                        <td class="fw-light">
                            <span v-for="statement in protections['protectionLevels']['common']['zombie']['flexible']['2']['filter']">
                                {{ statement }}<br/>
                            </span>{{}}
                        </td>
                    </tr>
                </tbody>
            </table>    
        </div>
        
    </div>

</div>
</template>