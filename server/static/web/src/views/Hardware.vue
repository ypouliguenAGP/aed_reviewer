<script setup>
const props = defineProps({
  aed_id: String,
})
import { ref, onMounted } from 'vue';

var hardware = ref([])

function getHardware() {
    fetch('/aed_reviewer/api/'+props.aed_id+'/hardware')
      .then(response => response.json())
      .then(data => hardware.value = data)
}

function stringSplit(input_string, separator, item){
  console.log(input_string)
  // console.log(input_string.length)
  // console.log(input_string.split(separator))
  if (input_string === undefined) return ''
  return input_string.split(separator)[item]

}

onMounted(() => {
  getHardware()
})
</script>

<template>
  <div class="container-fluid">
    <h3>Hardware</h3>
    <table class="table table-sm table-bordered">
      <thead>
        <tr>
          <th>Key</th>
          <th>Value</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="line in hardware">
          <td>{{ stringSplit(line, ':', 0) }}</td>
          <td>{{ stringSplit(line, ':', 1) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>