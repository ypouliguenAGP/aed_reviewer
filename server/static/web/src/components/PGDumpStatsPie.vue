<template>
    <v-chart class="chart mt-3" :option="option" />
</template>

<script setup>
const props = defineProps({
  title_str: String,
  stats: Array,
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
  var stats_data = []
  for (const stat of props.stats[props.unit]){
    stats_data.push({value: stat[1], name: stat[0]})
  }
  const series = [
  {
      type: 'pie',
      radius: '50%',
      data: stats_data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    },
  ]
  var option = {
    title: {
      text: props.title_str,
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    toolbox: {
      feature: {
        saveAsImage: {}
      }
    },
    series: series
  }
  return option
}
var option = {}

watch(() => props.stats, (first, second) => {
  option = setOptions()
});
watch(() => props.unit, (first, second) => {
  option = setOptions()
});
</script>

<style scoped>
</style>
