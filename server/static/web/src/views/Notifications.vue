<script>
export default {
  data() {
    return {
      notifications: {},
    }
  },
  created() {
    this.getItems();
  },
  methods: {
    getItems() {
      fetch('http://localhost:5000/aed_reviewer/api/notifications')
        .then(response => response.json())
        .then(data => this.notifications = data)
    },
    toString(array, separator){
      return array.join(separator)
    },
    keyInObj(obj, key){
      if (key in obj) return true
      return false
    }

    
  }
}
</script>

<template>
  <main>
    <div>
    
    <h3>Syslog</h3>
    <table class="table" v-if="this.notifications['syslog'].length > 0">
      <thead>
        <tr>
          <th scope="col">Host</th>
          <th scope="col">Port</th>
          <th scope="col">Created By</th>
          <th scope="col">Facility</th>
          <th scope="col">Severity</th>
          <th scope="col">Protocol</th>
          <th scope="col">Format</th>
          <th scope="col">Types</th>
        </tr>
      </thead>
      <tbody>
            <tr v-for="notification in this.notifications['syslog']">
                <th>{{ notification.host }}</th>
                <td>{{ notification.port }}</td>
                <th>{{ notification.creator }}</th>
                <td>{{ notification.facility }}</td>
                <td>{{ notification.severity }}</td>
                <td class="text-uppercase">{{ notification.protocol }}</td>
                <td>{{ notification.format }}</td>
                <td class="text-capitalize">{{toString(notification.types, ' ')}}</td>
            </tr>
      </tbody>
    </table>
    <h3>Email</h3>
    <table class="table" v-if="this.notifications['email'].length > 0">
      <thead>
        <tr>
          <th scope="col">From</th>
          <th scope="col">To</th>
          <th scope="col">Created By</th>
          <th scope="col">Types</th>
        </tr>
      </thead>
      <tbody>
            <tr v-for="notification in this.notifications['email']">
                <th>{{ notification.from }}</th>
                <td>{{ notification.to }}</td>
                <th>{{ notification.creator }}</th>
                <td class="text-capitalize">{{toString(notification.types, ' ')}}</td>
            </tr>
      </tbody>
    </table>
    <h3>SNMP</h3>
    <table class="table" v-if="this.notifications['snmp'].length > 0">
      <thead>
        <tr>
          <th scope="col">Host</th>
          <th scope="col">Version</th>
          <th scope="col">Community</th>
          <th scope="col">Privacy (v3)</th>
          <th scope="col">Auth (v3)</th>
          <th scope="col">Sec Level (v3)</th>
          <th scope="col">Created By</th>
          <th scope="col">Types</th>
        </tr>
      </thead>
      <tbody>
            <tr v-for="notification in this.notifications['snmp']">
                <th>{{ notification.host }}</th>
                <td>{{ notification.version }}</td>
                <td>{{ notification.community }}</td>
                <td><template v-if="notification.version != 2">{{ notification.priv_proto }}</template></td>
                <td><template v-if="notification.version != 2">{{ notification.auth_proto }}</template></td>
                <td><template v-if="notification.version != 2">{{ notification.sec_level }}</template></td>
                <th>{{ notification.creator }}</th>
                <td class="text-capitalize">{{toString(notification.types, ' ')}}</td>
            </tr>
      </tbody>
    </table>
    </div>
  </main>
</template>