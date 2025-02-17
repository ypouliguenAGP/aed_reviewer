<script setup>

const props = defineProps({
  protections: Object,
  levels: Array
})


</script>
<template>
    <div class="container-fluid px-5 mt-2">
        <h6 class="my-0">Malformed</h6>
        <table class="table table-hover table-striped">
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
                    <td v-for="level in levels" :class="protections['protectionLevels'][level]['tlsMalform']['enabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['tlsMalform']['enabled'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Cipher Limit</th>
                    <td v-for="level in levels" >{{ protections['protectionLevels'][level]['tlsMalform']['cipher_limit'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Extension Limit</th>
                    <td v-for="level in levels" >{{ protections['protectionLevels'][level]['tlsMalform']['extension_limit'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Compression Limit</th>
                    <td v-for="level in levels" >{{ protections['protectionLevels'][level]['tlsMalform']['compression_limit'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Max Hello Length</th>
                    <td v-for="level in levels" >{{ protections['protectionLevels'][level]['tlsMalform']['max_hello_length'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Min Pending Seconds</th>
                    <td v-for="level in levels" >{{ protections['protectionLevels'][level]['tlsMalform']['min_pend_secs'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Max Pending Seconds</th>
                    <td v-for="level in levels" >{{ protections['protectionLevels'][level]['tlsMalform']['max_pend_secs'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Early Whitelist</th>
                    <td v-for="level in levels" >{{ protections['protectionLevels'][level]['tlsMalform']['early_whitelist'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Max Early Close</th>
                    <td v-for="level in levels" >{{ protections['protectionLevels'][level]['tlsMalform']['max_early_close'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Client Alert</th>
                    <td v-for="level in levels" >{{ protections['protectionLevels'][level]['tlsMalform']['clients_can_alert'] }}</td>
                </tr>

            </tbody>
        </table>
        
    </div>
    
</template>