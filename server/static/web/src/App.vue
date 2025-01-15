<script setup>
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>

    <div class="grid-container">
        <div class="grid-child left">
            <ul class="bd-links-nav list-unstyled mb-0 pb-3 pb-md-2 pe-lg-2">
                <li class="bd-links-group py-2">
                    <strong class="bd-links-heading d-flex w-100 align-items-center fw-semibold">AED</strong>
                    <ul class="list-unstyled fw-normal pb-2 small">
                        <li><RouterLink class="bd-links-link d-inline-block rounded" to="/protection-groups">Protection Groups</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" to="/interfaces">Interfaces</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" to="/crawlers">Crawlers</RouterLink></li>
                        <li><RouterLink class="bd-links-link d-inline-block rounded" to="/notifications">Notifications</RouterLink></li>
                    </ul>
                </li>
            </ul>
            <ul class="bd-links-nav list-unstyled mb-0 pb-3 pb-md-2 pe-lg-2">
                <li class="bd-links-group py-2">
                    <strong class="bd-links-heading d-flex w-100 align-items-center fw-semibold">Settings</strong>
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