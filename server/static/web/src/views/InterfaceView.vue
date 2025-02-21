<script>
export default {
  data() {
    return {
      interfaces: {},
      interfaces_mgt: {},
    }
  },
  props: {
    aed_id: String,
  },
  created() {
    this.getInterfaces();
    this.getInterfacesMgt();
  },
  methods: {
    getInterfaces() {
      fetch('http://localhost:5000/aed_reviewer/api/'+this.aed_id+'/interfaces')
        .then(response => response.json())
        .then(data => this.interfaces = data)
    },
    getInterfacesMgt() {
      fetch('http://localhost:5000/aed_reviewer/api/'+this.aed_id+'/interfaces_mgt')
        .then(response => response.json())
        .then(data => this.interfaces_mgt = data)
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
<h3>Mitigation</h3>
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
<h3>Management</h3>
<table class="table">
  <thead>
    <tr>
      <th scope="col">Name</th>
      <th scope="col">IP</th>
      <th scope="col">State</th>
      <th scope="col">MAC</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="(inter, iter_name) in interfaces_mgt" :class="inter.state == 'No carrier' ? 'table-active': ''">
      <th scope="row">{{iter_name}}</th>
      <td>{{inter.ip}}</td>
      <td>{{inter.state}}</td>
      <td>{{inter.hw}}</td>
    </tr>
  </tbody>
</table>
</div>
</template>