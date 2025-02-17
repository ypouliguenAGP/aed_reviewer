<script setup>
import { ref, onMounted } from 'vue';

var ip_access = ref({})

function getData() {
    fetch('http://localhost:5000/aed_reviewer/api/ip_access')
      .then(response => response.json())
      .then(data => ip_access.value = data)
}

onMounted(() => {
  getData()
})
</script>

<template>
  <div class="container-fluid">
    <table class="table">
      <thead>
        <tr>
          <th scope="col" v-for="(value, key) in ip_access">{{ key }}</th>
        </tr>
      </thead>
      <tbody>
        <tr>
            <td scope="col" v-for="(access_value, access_key) in ip_access">
                <p class="my-0" v-for="line in access_value">{{ line['int']}} {{ line['source'] }}</p>
            </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>