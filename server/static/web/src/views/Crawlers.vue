<script>
export default {
  data() {
    return {
      crawlers: {},
      sts: {},
    }
  },
  created() {
    this.getItems();
    this.getSTs()
  },
  methods: {
    getItems() {
      fetch('http://localhost:5000/aed_reviewer/api/crawlers')
        .then(response => response.json())
        .then(data => this.crawlers = data)
    },
    getSTs() {
      fetch('http://localhost:5000/aed_reviewer/api/server_types')
        .then(response => response.json())
        .then(data => this.sts = data)
    },
    webCrawlerEnabledStats(){
        var enabled_count = 0
        for (const crawler_id in this.crawlers){
            if (this.crawlers[crawler_id].enabled == true) enabled_count += 1
        }
        return Math.round(enabled_count/Object.keys(this.crawlers).length*100)
    },
    webCrawlerSTEnabled(){
        var enabled_count = 0
        var crawler_available = 0
        for (const st_id in this.sts){
            console.log(enabled_count)
            console.log(st_id)
            
            if (!('webcrawler' in this.sts[st_id]['protectionLevels']['low'])) continue
            crawler_available += 1
            if (this.sts[st_id]['protectionLevels']['low']['webcrawler']['enabled']) enabled_count += 1
            console.log(enabled_count)
        }
        if (crawler_available == 0 || enabled_count == 0) return 0
        return Math.round(enabled_count/crawler_available*100)
    }
  }
}
</script>

<template>
  <main>
    <div>

    <div class="container-fluid">
        <div class="row">
            <div class="col">Web Crawlers Enabled</div>
            <div class="col">{{ webCrawlerEnabledStats() }}%</div>
        </div>
        <div class="row">
            <div class="col">Protection Group with Web Crawlers Enabled</div>
            <div class="col">{{ webCrawlerSTEnabled() }}%</div>
        </div>
    </div>
    
    <table class="table">
      <thead>
        <tr>
          <th scope="col">Name</th>
          <th scope="col">Enabled</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(crawler, item_id) in crawlers" :class="!crawler.enabled ? 'table-active': ''">
          <th scope="row">{{crawler.name}}</th>
          <td>{{crawler.enabled}}</td>
        </tr>
      </tbody>
    </table>
    </div>
  </main>
</template>