<template>
    <v-chart class="chart" :option="option" />
</template>

<script setup>

const props = defineProps({
  title_str: String,
  data: Object,
  unit: String
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
import { ref, provide, watch } from 'vue';

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
  const legend = Object.keys(props.data)
  const series = []
  for (const item of legend){
    series.push({
      name: item,
      type: 'line',
      lineStyle: {
          normal: {
            width: 1,
          }
        },  
      showSymbol: false,
      smooth: true,
      stack: 'Total',
      areaStyle: {},
      data: props.data[item][props.unit]
    })
  }

  const option = {
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
      top: 'bottom',
      textStyle: {
        width:'80',
        fontWeight: 'normal',
        fontSize: 10,
        overflow:'truncate',
        ellipsis: '..'
      },
      data: legend
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
    series: series
  };
  return option
}
var option = setOptions()

watch(() => props.unit, (first, second) => {
  option = setOptions()
});
watch(() => props.data, (first, second) => {
  option = setOptions()
});
</script>

<style scoped>
</style>
