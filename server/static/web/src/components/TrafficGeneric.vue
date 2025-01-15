<template>
  <v-chart class="chart" :option="option" />
</template>

<script setup>


const props = defineProps({
  title_str: String,
  data: Object,
  unit: String,
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

provide(THEME_KEY, 'light');

function setOptions(){
  var option = {
    title: {
      text: props.title_str
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
      data: ['Passed', 'Dropped']
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
        name: 'Passed',
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
        data: props.data['Passed']
      },
      {
        name: 'Dropped',
        type: 'line',
        lineStyle: {
          normal: {
            width: 1,
          }
        },
        smooth: true,
        stack: 'Total',
        color: [
        '#CC4043'
        ],
        showSymbol: false,
        areaStyle: {},
        data: props.data['Dropped']
      },
    ]
  };
  return option
}

var option = setOptions()

watch(() => props.data, (first, second) => {
  option = setOptions()
});
</script>

<style scoped>
    
</style>
