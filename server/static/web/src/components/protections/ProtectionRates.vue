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
const levels = ['low','medium','high']

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
    var rate_protections = {
        'Total': 'zombie',
        'Frag': 'fragmentation',
        'UDP': 'udpFlood',
        'ICMP': 'detectIcmp'
    }
    var legend = ['Total', 'UDP', 'ICMP', 'Frag']
    var series = []

    for (const [key, protection] of Object.entries(rate_protections)) {
        var data = []
        for (const level of levels){
            if (props.protections.protectionLevels[level][protection].enabled) data.push(props.protections.protectionLevels[level][protection][props.unit])
            else data.push('')
        }
        series.push({
            name: key,
            type: 'bar',
            barGap: 0,
            label: labelOption,
            emphasis: {
                focus: 'series'
            },
            data: data
        })
    }
    
    if (props.protections.protectionLevels.common.zombie.flexible['1'].filter.length > 0){
        var data = []
        for (const level of levels){
            if (props.protections.protectionLevels[level].zombie.flexible['1'].enabled) data.push(props.protections.protectionLevels[level].zombie.flexible['1'][props.unit])
            else data.push('')
        }
        series.splice(1, 0, {
            name: 'Flex1',
            type: 'bar',
            barGap: 0,
            label: labelOption,
            emphasis: {
                focus: 'series'
            },
            data: data
        })
        legend.splice(1, 0, 'Flex1');
    }
    if (props.protections.protectionLevels.common.zombie.flexible['2'].filter.length > 0){
        data = []
        for (const level of levels){
            if (props.protections.protectionLevels[level].zombie.flexible['2'].enabled) data.push(props.protections.protectionLevels[level].zombie.flexible['2'][props.unit])
            else data.push('')
        }
        series.splice(2, 0, {
            name: 'Flex2',
            type: 'bar',
            barGap: 0,
            label: labelOption,
            emphasis: {
                focus: 'series'
            },
            data: data
        })
        legend.splice(2, 0, 'Flex2');
    }
    // series.push({
    //     name: 'Frag',
    //     type: 'bar',
    //     barGap: 0,
    //     label: labelOption,
    //     emphasis: {
    //         focus: 'series'
    //     },
    //     data: [
    //     props.protections.protectionLevels.low.fragmentation[props.unit],
    //     props.protections.protectionLevels.medium.fragmentation[props.unit],
    //     props.protections.protectionLevels.high.fragmentation[props.unit]
    //     ]
    // })
    // series.push({
    //     name: 'UDP',
    //     type: 'bar',
    //     barGap: 0,
    //     label: labelOption,
    //     emphasis: {
    //         focus: 'series'
    //     },
    //     data: [
    //     props.protections.protectionLevels.low.udpFlood[props.unit],
    //     props.protections.protectionLevels.medium.udpFlood[props.unit],
    //     props.protections.protectionLevels.high.udpFlood[props.unit]
    //     ]
    // })
    // series.push({
    //     name: 'ICMP',
    //     type: 'bar',
    //     barGap: 0,
    //     label: labelOption,
    //     emphasis: {
    //         focus: 'series'
    //     },
    //     data: [
    //     props.protections.protectionLevels.low.detectIcmp[props.unit],
    //     props.protections.protectionLevels.medium.detectIcmp[props.unit],
    //     props.protections.protectionLevels.high.detectIcmp[props.unit]
    //     ]
    // })

    

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
        data: legend,
        top: 'bottom'
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
    series: series
   };
  return option
}
var option = setOptions()
</script>

<style scoped>
</style>
