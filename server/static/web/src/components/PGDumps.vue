<script setup>

const props = defineProps({
  pg_id: String,
})

import { onMounted,ref } from 'vue';

const dumps = ref({})
function loadData(){
    fetch('http://localhost:5000/aed_reviewer/api/protection_groups/'+props.pg_id+'/dumps/')
    .then(response => response.json())
    .then(data => dumps.value = data)
}

onMounted(() => {
    loadData()
})
</script>
<template>
<div id="dumps" class="mt-2">
    <table class="table table-striped table-hover">
        <thead>
            <tr>
                <th>#</th>
                <th>Source Country</th>
                <th>Source IP</th>
                <th>Destination IP</th>
                <th>Proto</th>
                <th>Source Port</th>
                <th>Destination Port</th>
                <th>Len</th>
                <th>Tflags</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="dump in dumps">
                <th>{{dump['#']}}</th>
                <td>{{dump.src_country	}}</td>
                <td>{{dump.src_ip}}</td>
                <td>{{dump.dst_ip}}</td>
                <td>{{dump.proto}}</td>
                <td>{{dump.src_port}}</td>
                <td>{{dump.dst_port}}</td>
                <td>{{dump.len}}</td>
                <td>{{dump.tcp_flags}}</td>
                <td>{{dump.action}}</td>
            </tr>
        </tbody>
    </table>

</div>
</template>