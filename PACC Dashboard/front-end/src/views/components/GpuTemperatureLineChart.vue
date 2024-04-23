<template>
  <div>
    <line-chart :node-data="gpuTemperatureData" data-type="gpuTemperature" />
  </div>
</template>

<script setup>
import { computed, watch } from "vue";
import { useStore } from "vuex";
import LineChart from "./LineChartComponent.vue"; // Assuming your line chart component is named LineChart.vue

const store = useStore();

// Prop to accept nodeName from parent or could be set statically here
const props = defineProps({
  nodeName: String,
});

// Compute the GPU temperature data for the specific node
const gpuTemperatureData = computed(() => {
  return store.getters.getNodeGpuTem(props.nodeName);
});

// gpuTemperatureData가 변경될 때마다 콘솔에 출력
watch(gpuTemperatureData, (newValue) => {
  console.log("Updated GPU Temperature Data:", newValue);
});
</script>

<style>
/* Style as necessary */
</style>
