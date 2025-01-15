<script>
export default {
  data() {
    return {
      interfaces: {},
    }
  },
  created() {
    this.getInterfaces();
  },
  methods: {
    getInterfaces() {
      fetch('http://localhost:5000/api/interfaces')
        .then(response => response.json())
        .then(data => this.interfaces = data)
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
      <th scope="col">Name</th>
      <th scope="col">Display Name</th>
      <th scope="col">Connected</th>
      <th scope="col">Speed</th>
      <th scope="col">Port Mirroring</th>
      <th scope="col">Alerts</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="(inter, item_id) in interfaces" :class="!inter.speed > 0 ? 'table-active': ''">
      <th scope="row">{{inter.ifname}}</th>
      <td>{{inter.display_name}}</td>
      <td><template v-if="inter.speed > 0">Yes</template><template v-else>No</template></td>
      <td><template v-if="inter.speed > 0">{{ inter.speed/1000 }}Gbps</template></td>
      <td><span :class="inter.speed > 0 && !inter.enable_port_mirroring ? 'text-warning': ''">{{humanBool(inter.enable_port_mirroring)}}</span></td>
      <td><span :class="inter.speed > 0 && !inter.alert_enabled ? 'text-danger': ''">{{humanBool(inter.alert_enabled)}}</span></td>
    </tr>
  </tbody>
</table>
</div>
</template>