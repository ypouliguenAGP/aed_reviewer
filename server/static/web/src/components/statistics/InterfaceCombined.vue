<template>
  <v-chart class="chart" :option="option" />
</template>

<script setup>

const props = defineProps({
  aed_id: String,
  graph_unit: String
})


import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart, LineChart } from 'echarts/charts';
import {
TitleComponent,
TooltipComponent,
LegendComponent,
ToolboxComponent,
GridComponent,
} from 'echarts/components';
import VChart, { THEME_KEY } from 'vue-echarts';
import { ref, provide, onMounted, watch, getCurrentInstance } from 'vue';

use([
CanvasRenderer,
PieChart,
TitleComponent,
TooltipComponent,
LegendComponent,
ToolboxComponent,
GridComponent,
LineChart,
]);

const incoming = ref([])
const outgoing = ref([])

var option = setOptions()

function loadData(){
    fetch(`/aed_reviewer/api/${props.aed_id}/statusdump/traffic/combined/${props.graph_unit}?start_date=1`)
      .then(response => response.json())
      .then(data => {
        incoming.value.length = 0
        outgoing.value.length = 0
        for (const point of data.data){
          incoming.value.push([point[0], point[1]])
          outgoing.value.push([point[0], point[2]])
        }
        option = setOptions()
        console.log('data retrieved')
      })
      .catch(err => console.error('loadData error:', err))
}


provide(THEME_KEY, 'light');

onMounted(() => {
    loadData()
})


function setOptions(){
  var option = {
    title: {
      text: 'Combined Traffic'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      data: ['Incoming', 'Outgoing']
    },
    toolbox: {
      feature: {
        saveAsImage: {}
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '5%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'time',
        boundaryGap: false,
      }
    ],
    yAxis: [
      {
        type: 'value'
      }
    ],
    series: [
      {
        name: 'Incoming',
        type: 'line',
        showSymbol: false,
        smooth: true,
        stack: 'Total',
        color: [
        '#8EC764'
        ],
        lineStyle: {
          normal: {
            width: 1,
          }
        },
        areaStyle: {},
        data: incoming.value
      },
      {
        name: 'Outgoing',
        type: 'line',
        showSymbol: false,
        smooth: true,
        stack: 'Total',
        color: [
        '#5470C6'
        ],
        lineStyle: {
          normal: {
            width: 1,
          }
        },
        areaStyle: {},
        data: outgoing.value
      }
    ]
  };
  return option
}

watch(() => props.graph_unit, (first, second) => {
  loadData()
});


</script>

<style scoped>
</style>