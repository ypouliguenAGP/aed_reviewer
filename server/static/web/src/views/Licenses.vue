<script setup>
const props = defineProps({
  aed_id: String,
})
import { ref, onMounted } from 'vue';

var licenses = ref([])

function getLicenses() {
    fetch('/aed_reviewer/api/'+props.aed_id+'/licenses')
      .then(response => response.json())
      .then(data => licenses.value = data)
}

function stringSplit(input_string, separator, item){
  console.log(input_string)
  // console.log(input_string.length)
  // console.log(input_string.split(separator))
  if (input_string === undefined) return ''
  return input_string.split(separator)[item]

}

onMounted(() => {
  getLicenses()
})
</script>

<template>
  <div class="container-fluid">
    <h3>Licenses</h3>
    <p>
        <span v-for="line in licenses">{{ line }}<br/></span>
    </p>
  </div>
</template>