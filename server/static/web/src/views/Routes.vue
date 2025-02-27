<script>
export default {
  data() {
    return {
      routes: {},
    }
  },
  props: {
    aed_id: String,
  },
  created() {
    this.getRoutes();
  },
  methods: {
    getRoutes() {
      fetch('/aed_reviewer/api/'+this.aed_id+'/ip_routes')
        .then(response => response.json())
        .then(data => this.routes = data)
    },
    humanBool(value){
      if (value === true) return 'Yes'
      return 'No'
    }

    
  },
}
</script>

<template>
<div>
<table class="table">
  <thead>
    <tr>
      <th scope="col">Destination</th>
      <th scope="col">Gateway</th>
      <th scope="col">Interface</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="(route_elements, route_gw) in routes">
      <td>
        <span v-for="route in route_elements">{{ route.destination }}<br/></span>
      </td>
      <td>{{route_gw}}</td>
      <td >{{route_elements[0].int}}</td>
    </tr>
  </tbody>
</table>
</div>
</template>