<template>
    <v-chart class="chart" :option="option" />
</template>

<script setup>

const props = defineProps({
  protections: Object,
  unit: String
})
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, BarChart } from 'echarts/charts';
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
CanvasRenderer,,
TitleComponent,
BarChart,
TooltipComponent,
LegendComponent,
ToolboxComponent,
GridComponent,
LineChart,
]);

provide(THEME_KEY, 'light');

function setOptions(){
    const posList = [
        'left',
        'right',
        'top',
        'bottom',
        'inside',
        'insideTop',
        'insideLeft',
        'insideRight',
        'insideBottom',
        'insideTopLeft',
        'insideTopRight',
        'insideBottomLeft',
        'insideBottomRight'
    ];
    const labelOption = {
        rotate: {
        min: -90,
        max: 90
        },
        align: {
            options: {
            left: 'left',
            center: 'center',
            right: 'right'
            }
        },
        verticalAlign: {
            options: {
            top: 'top',
            middle: 'middle',
            bottom: 'bottom'
            }
        },
        position: {
            options: posList.reduce(function (map, pos) {
            map[pos] = pos;
            return map;
            }, {})
        },
        distance: {
            min: 0,
            max: 100
        }
    };

    const main_data = [
    props.protections.protectionLevels.low.zombie[props.unit],
    props.protections.protectionLevels.medium.zombie[props.unit],
    props.protections.protectionLevels.high.zombie[props.unit]
    ]
    const fragment_data = [
    props.protections.protectionLevels.low.fragmentation[props.unit],
    props.protections.protectionLevels.medium.fragmentation[props.unit],
    props.protections.protectionLevels.high.fragmentation[props.unit]
    ] 
    const icmp_data = [
    props.protections.protectionLevels.low.detectIcmp[props.unit],
    props.protections.protectionLevels.medium.detectIcmp[props.unit],
    props.protections.protectionLevels.high.detectIcmp[props.unit]
    ]
    const udp_data = [
    props.protections.protectionLevels.low.udpFlood[props.unit],
    props.protections.protectionLevels.medium.udpFlood[props.unit],
    props.protections.protectionLevels.high.udpFlood[props.unit]
    ]

  const option = {
    title: {
        text: props.unit
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
        type: 'shadow'
        }
    },
    legend: {
        data: ['Total', 'UDP', 'ICMP', 'Frag']
    },
    toolbox: {
        show: true,
        orient: 'vertical',
        left: 'right',
        top: 'center',
        feature: {
        mark: { show: true },
        dataView: { show: true, readOnly: false },
        magicType: { show: true, type: ['line', 'bar', 'stack'] },
        restore: { show: true },
        saveAsImage: { show: true }
        }
    },
    xAxis: [
        {
        type: 'category',
        axisTick: { show: false },
        data: ['Low', 'Mediun', 'High']
        }
    ],
    yAxis: [
        {
        type: 'value'
        }
    ],
    series: [
        {
        name: 'Total',
        type: 'bar',
        barGap: 0,
        label: labelOption,
        emphasis: {
            focus: 'series'
        },
        data: main_data
        },
        {
        name: 'UDP',
        type: 'bar',
        label: labelOption,
        emphasis: {
            focus: 'series'
        },
        data: udp_data
        },
        {
        name: 'ICMP',
        type: 'bar',
        label: labelOption,
        emphasis: {
            focus: 'series'
        },
        data: icmp_data
        },
        {
        name: 'Frag',
        type: 'bar',
        label: labelOption,
        emphasis: {
            focus: 'series'
        },
        data: fragment_data
        }
    ]
   };
  return option
}
var option = setOptions()
</script>

<style scoped>
</style>
