<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted } from 'vue';

// const props = defineProps({
//     aed_id: String
// })
const aed_id = ref('blank')
if (location.pathname.split('/'.length > 1)){
    if (location.pathname.split('/')[1].startsWith('aed-')) aed_id.value = location.pathname.split('/')[1]
    else if (location.pathname.split('/')[2].startsWith('aed-')) aed_id.value = location.pathname.split('/')[2]
}

var system_name = ref(aed_id.value)

function getSysName() {
    fetch('/aed_reviewer/api/'+aed_id.value+'/system_name')
      .then(response => response.json())
      .then(data => {
        system_name.value = data
        document.title = "AED - "+system_name.value.name
    })
}

onMounted(() => {
  getSysName()
})

</script>

<template>
    <div class="grid-container">
        <div class="grid-child left">
            <ul class="bd-links-nav list-unstyled mb-0 pb-3 pb-md-2 pe-lg-2">
                <li class="bd-links-group py-2">
                    <strong class="bd-links-heading d-flex w-100 align-items-center fw-semibold">AEDs</strong>
                    <ul class="list-unstyled fw-normal pb-2 small">
                        <li><RouterLink class="bd-links-link d-inline-block rounded" to="/add">Add</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" to="/link">Access</RouterLink></li>
                        <li v-if="aed_id != 'blank'"><RouterLink class="bd-links-link d-inline-block rounded" :to="'/'+aed_id+'/protection-groups'">{{ system_name.name }}</RouterLink></li>
                    </ul>
                </li>
            </ul>
            <ul v-if="aed_id != 'blank'" class="bd-links-nav list-unstyled mb-0 pb-3 pb-md-2 pe-lg-2">
                <li class="bd-links-group py-2">
                    <strong class="bd-links-heading d-flex w-100 align-items-center fw-semibold">Protections</strong>
                    <ul class="list-unstyled fw-normal pb-2 small">
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="'/'+aed_id+'/protection-groups'">Protection Groups</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="{ name: 'crawlers', params: { aed_id: aed_id }}">Crawlers</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="'/'+aed_id+'/global_alerting'">Global Alerting</RouterLink></li>
                    </ul>
                </li>
            </ul>
            <ul v-if="aed_id != 'blank'" class="bd-links-nav list-unstyled mb-0 pb-3 pb-md-2 pe-lg-2">
                <li class="bd-links-group py-2">
                    <strong class="bd-links-heading d-flex w-100 align-items-center fw-semibold">Statistics</strong>
                    <ul class="list-unstyled fw-normal pb-2 small">
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="'/'+aed_id+'/statistics/interfaces'">Interfaces</RouterLink></li>
                    </ul>
                </li>
            </ul>
            <ul v-if="aed_id != 'blank'" class="bd-links-nav list-unstyled mb-0 pb-3 pb-md-2 pe-lg-2">
                <li class="bd-links-group py-2">
                    <strong class="bd-links-heading d-flex w-100 align-items-center fw-semibold">Configuration</strong>
                    <ul class="list-unstyled fw-normal pb-2 small">
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="'/'+aed_id+'/hardware'">Hardware</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="'/'+aed_id+'/licenses'">Licenses</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="'/'+aed_id+'/global_config'">Global Config</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="'/'+aed_id+'/interfaces'">Interfaces</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="'/'+aed_id+'/routes'">Routes</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="'/'+aed_id+'/notifications'">Notifications</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="'/'+aed_id+'/ip_access'">IP Access</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="'/'+aed_id+'/changes'">Changes</RouterLink></li>
                    </ul>
                </li>
            </ul>
            <ul v-if="aed_id != 'blank'" class="bd-links-nav list-unstyled mb-0 pb-3 pb-md-2 pe-lg-2">
                <li class="bd-links-group py-2">
                    <strong class="bd-links-heading d-flex w-100 align-items-center fw-semibold">Explore</strong>
                    <ul class="list-unstyled fw-normal pb-2 small">
                        <li><RouterLink class="bd-links-link d-inline-block rounded" :to="'/' + aed_id + '/packet-explorer'">Packet Explorer</RouterLink></li>
                    </ul>
                </li>
            </ul>
            <ul class="bd-links-nav list-unstyled mb-0 pb-3 pb-md-2 pe-lg-2">
                <li class="bd-links-group py-2">
                    <strong class="bd-links-heading d-flex w-100 align-items-center fw-semibold">Tool Settings</strong>
                    <ul class="list-unstyled fw-normal pb-2 small">
                        <li><RouterLink class="bd-links-link d-inline-block rounded" to="/settings">General</RouterLink></li>
                    </ul>
                </li>
            </ul>
            
        </div>
        <div class="grid-child right">
            <RouterView />
        </div>

    </div>
</template>

<style>
.grid-container {
    display: grid;
    grid-template-columns: 1fr 10fr;
    grid-gap: 20px;
}
.bd-links-link {
	padding: .1875rem .5rem;
	margin-top: .125rem;
	margin-left: 0.625rem;
	color: var(--bs-body-color);
	text-decoration: none;
}
.bd-links-group{
    padding-left: .2rem;
}
.bd-links-link:hover, .bd-links-link:focus, .bd-links-link.router-link-active{
	color: #fff;
	background-color:#026D70;
}
.bd-links-link.router-link-active {
	font-weight: 600;
}

</style>