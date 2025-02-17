<script setup>

const props = defineProps({
  protections: Object,
  levels: Array
})


</script>
<template>
    <div class="container-fluid px-5 mt-2">
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
                    <th>Web Crawler Support</th>
                    <td v-for="level in levels">{{ protections['protectionLevels'][level]['webcrawler']['enabled'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Reputation</th>
                    <td v-for="level in levels">{{ protections['protectionLevels'][level]['reputation']['enabled'] }}</td>
                </tr>
                
                <tr class="text-capitalize">
                    <th>Confidence</th>
                    <td v-for="level in levels">{{ protections['protectionLevels'][level]['reputation']['asertConfidence'] }}</td>
                </tr>
                <tr class="text-capitalize">
                    <th>Deep Scrubbing</th>
                    <td v-for="level in levels">{{ protections['protectionLevels'][level]['reputation']['deepScrubbing'] }}</td>
                </tr>

            </tbody>
        </table>
    </div>
    
</template>