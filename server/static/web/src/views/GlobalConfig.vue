<script setup>
const props = defineProps({
  aed_id: String,
})
import { ref, onMounted } from 'vue';

var global_config = ref([])
var proxies = ref([])

var proxy_type = ref({
    1: 'ATLAS',
    2: 'Cloud Signaling',
})

function getItem() {
    fetch('/aed_reviewer/api/'+props.aed_id+'/global')
      .then(response => response.json())
      .then(data => global_config.value = data)
}

function getProxy() {
    fetch('/aed_reviewer/api/'+props.aed_id+'/http_proxy')
      .then(response => response.json())
      .then(data => proxies.value = data)
}

function cleanValue(value){
    if (value.startsWith('"') && value.endsWith('"')){
        return value.slice(1, ).slice(0, -1)
    }
    return value
}

function timestampToDate(timestamp){
    return new Date(timestamp * 1000);
    
}


function humanEnabled(value){
  if (value == 0) return 'Yes'
  return 'No'
}

onMounted(() => {
    getItem()
    getProxy()
})
</script>

<template>
    <div class="container-fluid">
      <h3>Global Config</h3>
      <table class="table table-sm table-bordered">
        <thead>
          <tr>
            <th>Key</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(value, key) in global_config">
            <td>{{key}}</td>
            
            <td>
                <template v-if="key == 'aif-last-update-time'">{{ timestampToDate(value) }}</template>
                <template v-else>{{cleanValue(value)}}</template>
            </td>
          </tr>
        </tbody>
      </table>

      <h3>Proxy</h3>
      <template v-for="proxy in proxies">
        <table class="table table-sm table-bordered">
            <thead>
            <tr>
                <th>Key</th>
                <th>Value</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(value, key) in proxy">
                <td>{{key}}</td>
                <td>
                    <template v-if="key == 'enable'">{{ humanEnabled(value) }}</template>
                    <template v-else-if="key == 'type'">{{ proxy_type[value] }}</template>
                    
                    <template v-else>{{value}}</template>
                </td>
            </tr>
            </tbody>
        </table>
      </template>
    </div>
  </template>