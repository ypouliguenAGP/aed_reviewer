<script>
export default {
  props: {
    pg_id: String,
  },
  data() {
    return {
      pgs: {},
      st: {},
      relevant_alerts_age: Date.now()/1000-(3600*24*90)
    }
  },
  created() {
    this.getData();
    console.log(this.pd_id)
  },
  methods: {
    getData() {
      fetch('http://localhost:5000/aed_reviewer/api/protection_group/')
        .then(response => response.json())
        .then(data => this.pgs = data)
    },
  },

}
</script>

<template>
{{ pg_id }}
</template>