<template>
  <h4 class="text-center">Pair {{ props.pair }}</h4>
  <v-chart class="chart" :option="option_inbound" />
  <v-chart class="chart" :option="option_outbound" />
</template>

<script setup>

const props = defineProps({
  pair: String,
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

const ext_rx = ref([])
const ext_tx = ref([])
const int_rx = ref([])
const int_tx = ref([])

var option_inbound = setOptions('inbound')
var option_outbound = setOptions('outbound')

function loadData(){
    fetch(`/aed_reviewer/api/${props.aed_id}/statusdump/pair/${props.pair}/${props.graph_unit}?step=300&start_date=1`)
      .then(response => response.json())
      .then(data => {
        ext_rx.value.length = 0
        int_rx.value.length = 0
        ext_tx.value.length = 0
        int_tx.value.length = 0
        for (const point of data.data){
          ext_rx.value.push([point[0], point[1]])
          int_tx.value.push([point[0], -point[2]])
          ext_tx.value.push([point[0], point[3]])
          int_rx.value.push([point[0], -point[4]])
        }
        option_inbound = setOptions()
        option_outbound = setOptions()
        console.log('data retrieved')
      })
      .catch(err => console.error('loadData error:', err))
}


provide(THEME_KEY, 'light');

onMounted(() => {
    loadData()
})


function setOptions(direction){
  var option = {
    title: {},
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
        name: 'RX',
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
      },
      {
        name: 'TX',
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
      }
    ]
  };
  if (direction == 'inbound') {
    option['title'] = {text: 'Inbound Traffic'}
    option['legend']['data'] = ['EXT RX', 'INT TX']
    option['series'][0]['name'] = 'EXT RX'
    option['series'][0]['data'] = ext_rx.value
    option['series'][1]['name'] = 'INT TX'
    option['series'][1]['data'] = int_tx.value
  } else {
    option['title'] = {text: 'Outbound Traffic'}
    option['legend']['data'] = ['EXT TX', 'INT RX']
    option['series'][1]['name'] = 'INT RX'
    option['series'][1]['data'] = int_rx.value
    option['series'][0]['name'] = 'EXT TX'
    option['series'][0]['data'] = ext_tx.value
  }
  return option
}

watch(() => props.graph_unit, (first, second) => {
  loadData()
});


</script>

<style scoped>
</style>