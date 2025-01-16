<script setup>

const props = defineProps({
  pg_id: String,
})

import { onMounted,ref } from 'vue';

const chart_period = ref('1d')
const graph_unit = ref('bps')
const changes = ref({})
function loadLogs(){
    fetch('http://localhost:5000/api/protection_groups/'+props.pg_id+'/changes/')
    .then(response => response.json())
    .then(data => changes.value = array_reorder(data))
}
function array_reorder(array){
    array.sort(function(a,b){
    // Turn your strings into dates, and then subtract them
    // to get a value that is either negative, positive, or zero.
    return new Date(b.tstamp) - new Date(a.tstamp);
    });
    return array
}
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('default', {dateStyle: 'long'}).format(date);
}
onMounted(() => {
    loadLogs()
})
</script>
<template>
<div id="events" class="mt-2">
    <table class="table table-striped table-hover">
        <thead>
            <tr>
                <th>#</th>
                <th>Date</th>
                <th>Sub System</th>
                <th>Username</th>
                <th>Source</th>
                <th>Message</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="log in changes">
                <th>{{log.id}}</th>
                <td>{{formatDate(log.tstamp*1000)}}</td>
                <td>{{log.subsystem}}</td>
                <td>{{log.username}}</td>
                <td>{{log.source}}</td>
                <td>{{log.message}}</td>
            </tr>
        </tbody>
    </table>

</div>
</template>