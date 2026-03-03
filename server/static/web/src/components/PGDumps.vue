<script setup>

const props = defineProps({
  pg_id: String,
  aed_id: String,
})

import { onMounted, ref, computed, nextTick } from 'vue';
import { Tooltip } from 'bootstrap';

const dumps = ref([])

const filters = ref({
    src_country: '',
    src_ip: '',
    dst_ip: '',
    proto: '',
    src_port: '',
    dst_port: '',
    len: '',
    tcp_flags: '',
    action: ''
})

function matchesFilter(value, filter, exact = false) {
    if (filter === '') return true
    
    const valueStr = String(value ?? '').toLowerCase()
    let isNegated = false
    let filterStr = filter.trim()
    
    if (filterStr.startsWith('!')) {
        isNegated = true
        filterStr = filterStr.substring(1)
    } else if (filterStr.toLowerCase().startsWith('not:')) {
        isNegated = true
        filterStr = filterStr.substring(4)
    }
    
    if (filterStr === '') return true
    
    const matches = exact 
        ? valueStr === filterStr.toLowerCase()
        : valueStr.includes(filterStr.toLowerCase())
    return isNegated ? !matches : matches
}

function matchesNumericFilter(value, filter) {
    if (filter === '') return true
    
    let filterStr = filter.trim()
    let isNegated = false
    
    if (filterStr.startsWith('!')) {
        isNegated = true
        filterStr = filterStr.substring(1)
    } else if (filterStr.toLowerCase().startsWith('not:')) {
        isNegated = true
        filterStr = filterStr.substring(4)
    }
    
    if (filterStr === '') return true
    
    const numValue = Number(value)
    let matches = false
    
    // Check for range syntax (e.g., 1024..4567)
    if (filterStr.includes('..')) {
        const [minStr, maxStr] = filterStr.split('..')
        const min = Number(minStr)
        const max = Number(maxStr)
        matches = !isNaN(min) && !isNaN(max) && numValue >= min && numValue <= max
    } else if (filterStr.startsWith('>=')) {
        const target = Number(filterStr.substring(2))
        matches = !isNaN(target) && numValue >= target
    } else if (filterStr.startsWith('<=')) {
        const target = Number(filterStr.substring(2))
        matches = !isNaN(target) && numValue <= target
    } else if (filterStr.startsWith('>')) {
        const target = Number(filterStr.substring(1))
        matches = !isNaN(target) && numValue > target
    } else if (filterStr.startsWith('<')) {
        const target = Number(filterStr.substring(1))
        matches = !isNaN(target) && numValue < target
    } else {
        const target = Number(filterStr)
        matches = !isNaN(target) && numValue === target
    }
    
    return isNegated ? !matches : matches
}

const filteredDumps = computed(() => {
    return dumps.value.filter(dump => {
        return (
            matchesFilter(dump.src_country, filters.value.src_country) &&
            matchesFilter(dump.src_ip, filters.value.src_ip) &&
            matchesFilter(dump.dst_ip, filters.value.dst_ip) &&
            matchesFilter(dump.proto, filters.value.proto, true) &&
            matchesNumericFilter(dump.src_port, filters.value.src_port) &&
            matchesNumericFilter(dump.dst_port, filters.value.dst_port) &&
            matchesNumericFilter(dump.len, filters.value.len) &&
            matchesFilter(dump.tcp_flags, filters.value.tcp_flags) &&
            matchesFilter(dump.action, filters.value.action)
        )
    })
})

const filterStats = computed(() => {
    const total = dumps.value.length
    const displayed = filteredDumps.value.length
    const percentage = total > 0 ? ((displayed / total) * 100).toFixed(1) : 0
    return { displayed, total, percentage }
})

function loadData(){
    fetch('/aed_reviewer/api/'+props.aed_id+'/protection_groups/'+props.pg_id+'/dumps/')
    .then(response => response.json())
    .then(data => dumps.value = data)
}

function initTooltips() {
    nextTick(() => {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
        tooltipTriggerList.forEach(el => new Tooltip(el))
    })
}

onMounted(() => {
    loadData()
    initTooltips()
})
</script>
<template>
<div id="dumps" class="mt-2">
    <table class="table table-striped table-hover">
        <thead>
            <tr>
                <th>#</th>
                <th data-bs-toggle="tooltip" data-bs-html="true" data-bs-title="<strong>Text filter (partial match)</strong><br><br><code>FR</code> - contains 'FR'<br><code>!US</code> - does NOT contain 'US'<br><code>not:CN</code> - does NOT contain 'CN'">Source Country</th>
                <th data-bs-toggle="tooltip" data-bs-html="true" data-bs-title="<strong>Text filter (partial match)</strong><br><br><code>192.168</code> - contains '192.168'<br><code>!10.0</code> - does NOT contain '10.0'<br><code>not:172</code> - does NOT contain '172'">Source IP</th>
                <th data-bs-toggle="tooltip" data-bs-html="true" data-bs-title="<strong>Text filter (partial match)</strong><br><br><code>192.168</code> - contains '192.168'<br><code>!10.0</code> - does NOT contain '10.0'<br><code>not:172</code> - does NOT contain '172'">Destination IP</th>
                <th data-bs-toggle="tooltip" data-bs-html="true" data-bs-title="<strong>Exact match filter</strong><br><br><code>6</code> - exactly TCP<br><code>17</code> - exactly UDP<br><code>!1</code> - NOT ICMP">Proto</th>
                <th data-bs-toggle="tooltip" data-bs-html="true" data-bs-title="<strong>Numeric filter</strong><br><br><code>443</code> - equals 443<br><code>&gt;1024</code> - greater than 1024<br><code>&gt;=80</code> - greater or equal to 80<br><code>&lt;1024</code> - less than 1024<br><code>&lt;=443</code> - less or equal to 443<br><code>1024..4567</code> - range (1024 to 4567)<br><code>!22</code> - NOT equals 22">Source Port</th>
                <th data-bs-toggle="tooltip" data-bs-html="true" data-bs-title="<strong>Numeric filter</strong><br><br><code>443</code> - equals 443<br><code>&gt;1024</code> - greater than 1024<br><code>&gt;=80</code> - greater or equal to 80<br><code>&lt;1024</code> - less than 1024<br><code>&lt;=443</code> - less or equal to 443<br><code>1024..4567</code> - range (1024 to 4567)<br><code>!22</code> - NOT equals 22">Destination Port</th>
                <th data-bs-toggle="tooltip" data-bs-html="true" data-bs-title="<strong>Numeric filter</strong><br><br><code>64</code> - equals 64<br><code>&gt;100</code> - greater than 100<br><code>&gt;=64</code> - greater or equal to 64<br><code>&lt;1500</code> - less than 1500<br><code>&lt;=1000</code> - less or equal to 1000<br><code>64..1500</code> - range (64 to 1500)<br><code>!0</code> - NOT equals 0">Len</th>
                <th data-bs-toggle="tooltip" data-bs-html="true" data-bs-title="<strong>Text filter (partial match)</strong><br><br><code>S</code> - contains 'SYN'<br><code>A</code> - contains 'ACK'<br><code>!R</code> - does NOT contain 'RST'">Tflags</th>
                <th data-bs-toggle="tooltip" data-bs-html="true" data-bs-title="<strong>Text filter (partial match)</strong><br><br><code>drop</code> - contains 'drop'<br><code>pass</code> - contains 'pass'<br><code>!drop</code> - does NOT contain 'drop'">Action</th>
            </tr>
            <tr>
                <th><small>{{ filterStats.displayed }}/{{ filterStats.total }} ({{ filterStats.percentage }}%)</small></th>
                <th><input type="text" v-model="filters.src_country" class="form-control form-control-sm" placeholder="Filter..."></th>
                <th><input type="text" v-model="filters.src_ip" class="form-control form-control-sm" placeholder="Filter..."></th>
                <th><input type="text" v-model="filters.dst_ip" class="form-control form-control-sm" placeholder="Filter..."></th>
                <th><input type="text" v-model="filters.proto" class="form-control form-control-sm" placeholder="Filter..."></th>
                <th><input type="text" v-model="filters.src_port" class="form-control form-control-sm" placeholder="Filter..."></th>
                <th><input type="text" v-model="filters.dst_port" class="form-control form-control-sm" placeholder="Filter..."></th>
                <th><input type="text" v-model="filters.len" class="form-control form-control-sm" placeholder="Filter..."></th>
                <th><input type="text" v-model="filters.tcp_flags" class="form-control form-control-sm" placeholder="Filter..."></th>
                <th><input type="text" v-model="filters.action" class="form-control form-control-sm" placeholder="Filter..."></th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="dump in filteredDumps">
                <th>{{dump['#']}}</th>
                <td>{{dump.src_country}}</td>
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