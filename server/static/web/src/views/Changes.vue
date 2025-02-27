<script setup>
const props = defineProps({
  aed_id: String,
})
import { ref, onMounted, watch } from 'vue';

const changes = ref([])
const change_types = ref([])
const search_keyword = ref('')
const type_selected = ref('*')

function getChangeTypes() {
    fetch('/aed_reviewer/api/'+props.aed_id+'/change_types/')
      .then(response => response.json())
      .then(data => change_types.value = data)
      .then(data => change_types.value.push('*'))
      .then(data => console.log(change_types.value))
}

function getChanges() {
    fetch('/aed_reviewer/api/'+props.aed_id+'/changes/',{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ subtype: type_selected.value, search_str: search_keyword.value }),
    })
      .then(response => response.json())
      .then(data => changes.value = data)
      .then(data => changes.value = array_reorder(data))
}

function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    return new Intl.DateTimeFormat('en-GB', {dateStyle: 'medium', timeStyle: 'short'}).format(date);
}

function array_reorder(array){
    array.sort(function(b,a){
    // Turn your strings into dates, and then subtract them
    // to get a value that is either negative, positive, or zero.
    return new Date(a.tstamp) - new Date(b.tstamp);
    });
    return array
}

onMounted(() => {
    getChanges()
    getChangeTypes()
})

watch(search_keyword, async (newSearch, oldSearch) => {
    getChanges()
})

watch(type_selected, async (newItem, oldItem) => {
    getChanges()
})
</script>

<template>
  <div class="container-fluid">
    <div class="row">
        <div class="col-5">
            <div class="input-group">
                <input type="search" ref="search" class="form-control" id="SearchInput" placeholder="Search.." v-model="search_keyword" aria-describedby="button-clear-search">
                <span class="input-group-text" id="button-clear-search" @click="search_keyword = '', $refs.search.focus();">X</span>
            </div>
        </div>
        <div class="col-3">
            <select class="form-select" aria-label="select type" v-model="type_selected">
                <option v-for="option in change_types" :value="option">
                    {{ option }}
                </option>
            </select>
        </div>
    </div>
    <table class="mt-2 table table-sm table-bordered table-striped table-hover">
      <thead>
        <tr>
          <th>#</th>
          <th>Gid</th>
          <th>Gid Name</th>
          <!-- <th>Source</th> -->
          <th>subsystem</th>
          <th>Time</th>
          <th>Username</th>
          <th>Message</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="change in changes">
          <th>{{ change.id }}</th>
          <td>{{ change.gui }}</td>
          <td>{{ change.gid_name }}</td>
          <!-- <td>{{ change.source }}</td> -->
          <td>{{ change.subsystem }}</td>
          <td>{{ formatDate(change.tstamp) }}</td>
          <td>{{ change.username }}</td>
          <td>{{ change.message }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>