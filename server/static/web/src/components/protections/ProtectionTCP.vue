<script setup>

const props = defineProps({
  protections: Object,
  levels: Array
})


</script>
<template>
    <div class="container-fluid px-5 mt-2">
        <div v-if="protections['protectionLevels']['low']['synAuth']">
            <h6 class="my-0">SYN Auth</h6>
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
                    <td v-for="level in levels" :class="protections['protectionLevels'][level]['synAuth']['enabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['synAuth']['enabled'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>outOfSeq</th>
                    <td v-for="level in levels" :class="protections['protectionLevels'][level]['synAuth']['outOfSeqEnabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['synAuth']['outOfSeqEnabled'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Automation</th>
                    <td v-for="level in levels" :class="protections['protectionLevels'][level]['synAuth']['automationEnabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['synAuth']['automationEnabled'] }}<template v-if="protections['protectionLevels'][level]['synAuth']['automationEnabled']"> - {{ protections['protectionLevels'][level]['synAuth']['automationThreshold'] }}</template></td>
                </tr>
                <tr class="text-capitalize">
                    <th>HTTP Auth</th>
                    <td v-for="level in levels">{{ protections['protectionLevels'][level]['synAuth']['httpAuthEnabled'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Javascript</th>
                    <td v-for="level in levels">{{ protections['protectionLevels'][level]['synAuth']['javascriptEnabled'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Soft Reset</th>
                    <td v-for="level in levels">{{ protections['protectionLevels'][level]['synAuth']['softResetEnabled'] }}</td>
                </tr>

            </tbody>
        </table>
        </div>
        
        <div v-if="protections['protectionLevels']['low']['detectSyn']">
            <hr class="mt-3"/>
            <h6 class="my-0">SYN Flood</h6>
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
                        <td v-for="level in levels" :class="protections['protectionLevels'][level]['detectSyn']['enabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['synAuth']['enabled'] }}</td>
                    </tr>
                    <tr class="text-capitalize">
                        <th>synRate</th>
                        <td v-for="level in levels"><template v-if="protections['protectionLevels'][level]['synAuth']['enabled']">{{ protections['protectionLevels'][level]['detectSyn']['synRate'] }}</template></td>
                    </tr>
                    <tr class="text-capitalize">
                        <th>synAckDeltaRate</th>
                        <td v-for="level in levels"><template v-if="protections['protectionLevels'][level]['synAuth']['enabled']">{{ protections['protectionLevels'][level]['detectSyn']['synAckDeltaRate'] }}</template></td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div v-if="protections['protectionLevels']['low']['connlimit']">
            <hr class="mt-3"/>
            <h6 class="my-0">Connection Limit</h6>
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
                        <td v-for="level in levels" :class="protections['protectionLevels'][level]['connlimit']['enabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['connlimit']['enabled'] }}</td>
                    </tr>
                    <tr class="text-capitalize">
                        <th>Limit</th>
                        <td v-for="level in levels"><template v-if="protections['protectionLevels'][level]['connlimit']['enabled']">{{ protections['protectionLevels'][level]['connlimit']['connLimit'] }}</template></td>
                    </tr>
                    <tr class="text-capitalize">
                        <th>Blacklist</th>
                        <td v-for="level in levels"><template v-if="protections['protectionLevels'][level]['connlimit']['enabled']">{{ protections['protectionLevels'][level]['connlimit']['blacklistEnabled'] }}</template></td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div v-if="protections['protectionLevels']['low']['idleReset']">
            <hr class="mt-3"/>
            <h6 class="my-0">Idle Reset</h6>
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
                        <td v-for="level in levels" :class="protections['protectionLevels'][level]['idleReset']['enabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['idleReset']['enabled'] }}</td>
                    </tr>
                    <tr class="text-capitalize">
                        <th>idleTimeout</th>
                        <td v-for="level in levels"><template v-if="protections['protectionLevels'][level]['idleReset']['enabled']">{{ protections['protectionLevels'][level]['idleReset']['idleTimeout'] }}</template></td>
                    </tr>
                    <tr class="text-capitalize">
                        <th>initSize</th>
                        <td v-for="level in levels"><template v-if="protections['protectionLevels'][level]['idleReset']['enabled']">{{ protections['protectionLevels'][level]['idleReset']['initSize'] }}</template></td>
                    </tr>
                    <tr class="text-capitalize">
                        <th>numIdles</th>
                        <td v-for="level in levels"><template v-if="protections['protectionLevels'][level]['idleReset']['enabled']">{{ protections['protectionLevels'][level]['idleReset']['numIdles'] }}</template></td>
                    </tr>
                    <tr class="text-capitalize">
                        <th>track_long_lived</th>
                        <td v-for="level in levels" :class="protections['protectionLevels'][level]['idleReset']['enabled'] ? 'text-success': 'text-danger'"><template v-if="protections['protectionLevels'][level]['idleReset']['enabled']">{{ protections['protectionLevels'][level]['idleReset']['track_long_lived'] }}</template></td>
                    </tr>
                    <tr class="text-capitalize">
                        <th>headerTime</th>
                        <td v-for="level in levels"><template v-if="protections['protectionLevels'][level]['idleReset']['enabled']">{{ protections['protectionLevels'][level]['idleReset']['headerTime'] }}</template></td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        
    </div>
    
</template>