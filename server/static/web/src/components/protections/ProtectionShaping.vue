<template>
    <table class="table table-hover table-striped">
        <thead>
            <tr>
                <th scope="col"></th>
                <th scope="col" v-for="level in levels">
                    <span class="text-capitalize">{{ level }}</span>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr class="text-capitalize">
                <th>Enabled</th>
                <td v-for="level in levels" :class="protections['protectionLevels'][level]['shaping']['enabled'] ? 'text-success': 'text-danger'">{{ protections['protectionLevels'][level]['shaping']['enabled'] }}</td>
            </tr>
            <tr class="text-capitalize">
                <th>Filter</th>
                <td v-for="level in levels" >{{ protections['protectionLevels'][level]['shaping']['filter'] }}</td>
            </tr>

        </tbody>
    </table>
    <div class="row">
        <div class="col">
            <v-chart v-if="protection_enabled" class="chart" :option="option_pps" />
        </div>
        <div class="col">
            <v-chart v-if="protection_enabled" class="chart" :option="option_bps" />
        </div>
    </div>
    
</template>

<script setup>

const props = defineProps({
  protections: Object,
  levels: Array,
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
import { ref, provide, watch, computed } from 'vue';

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

const protection_enabled = computed(() => {
    for (const level of props.levels){
        if (props.protections.protectionLevels[level]['shaping'].enabled) return true
    }
    return false
})

function setOptions(unit){
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
        'Shaping': 'shaping',
    }
    var legend = ['Shaping']
    var series = []

    for (const [key, protection] of Object.entries(rate_protections)) {
        var data = []
        for (const level of props.levels){
            if (props.protections.protectionLevels[level][protection].enabled) data.push(props.protections.protectionLevels[level][protection][unit])
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
  const option = {
    title: {
        text: unit
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
var option_pps = setOptions('pps')
var option_bps = setOptions('bps')

</script>

<style scoped>
</style>
