<script setup>

const props = defineProps({
  protections: Object,
  levels: Array
})


</script>
<template>
    <div class="container-fluid px-5 mt-2">
        <div v-if="protections['protectionLevels']['low']['dnsMalform']">
            <h6 class="my-0">DNS</h6>
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
                <tr class="text-capitalize" v-if="protections['protectionLevels']['low']['dnsMalform']">
                    <th>dnsMalform</th>
                    <td v-for="level in levels" :class="protections['protectionLevels'][level]['dnsMalform']['enabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['dnsMalform']['enabled'] }}</td>
                </tr>
                <tr class="text-capitalize" v-if="protections['protectionLevels']['low']['dnsAuth']">
                    <th>dnsAuth</th>
                    <td v-for="level in levels" :class="protections['protectionLevels'][level]['dnsAuth']['enabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['dnsAuth']['enabled'] }}</td>
                </tr>
                <tr class="text-capitalize" v-if="protections['protectionLevels']['low']['dnsQuery']">
                    <th>dnsQuery</th>
                    <td v-for="level in levels">{{ protections['protectionLevels'][level]['dnsQuery']['rate'] }}</td>
                </tr>
                <tr class="text-capitalize" v-if="protections['protectionLevels']['low']['dnsNxdomain']">
                    <th>dnsNxdomain	</th>
                    <td v-for="level in levels" :class="protections['protectionLevels'][level]['dnsQuery']['rate'] < protections['protectionLevels'][level]['dnsNxdomain']['rate'] ? 'text-danger': ''">{{ protections['protectionLevels'][level]['dnsNxdomain']['rate'] }}</td>
                </tr>

                <tr class="text-capitalize" v-if="protections['protectionLevels']['low']['dnsAmp']">
                    <th>DNS Amp Protection</th>
                    <td v-for="level in levels" :class="protections['protectionLevels'][level]['dnsAmp']['enabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['dnsAmp']['enabled'] }}</td>
                </tr>

                <tr class="text-capitalize" v-if="protections['protectionLevels']['low']['dnsNonexistent']">
                    <th>DNS Nonexistent Monitor</th>
                    <td v-for="level in levels" :class="protections['protectionLevels'][level]['dnsNonexistent']['enabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['dnsNonexistent']['enabled'] }}</td>
                </tr>
                <tr class="text-capitalize" v-if="protections['protectionLevels']['low']['dnsNonexistent']">
                    <th>DNS Nonexistent Enforced</th>
                    <td v-for="level in levels" :class="protections['protectionLevels'][level]['dnsNonexistent']['enforced'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['dnsNonexistent']['enforced'] }}</td>
                </tr>

                


            </tbody>
        </table>
        </div>
       
        
    </div>
    
</template>