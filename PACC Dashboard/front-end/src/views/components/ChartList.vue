<template>
  <div class="chart-list-widget">
    <h4 class="chart-list-header">Chart List</h4>
    <div class="chart-list-body">
      <ul class="chart-name-list">
        <li
          v-for="(chartName, index) in chartNames"
          :key="index"
          @click="selectChart(chartName)"
          :class="{ selected: selectedChart === chartName }"
        >
          {{ chartName }}
        </li>
      </ul>
    </div>
  </div>
  <div class="chart-display-container">
    <div v-if="selectedChart === 'Memory Usage'">
      <h2 class="memory-gauge-header">Memory Usage</h2>
      <div class="memory-gauge-wrapper">
        <MemoryGauge
          v-for="node in filteredNodes"
          :key="'memory-' + node.id"
          :nodeName="node.name"
          :totalSize="node.total_memory_mb"
          :remainingSize="nodeFreeMemories[node.name]"
        />
      </div>
    </div>
    <div v-if="selectedChart === 'Disk Usage'">
      <h2 class="disk-gauge-header">Disk Usage</h2>
      <div class="disk-gauge-wrapper">
        <DiskGauge
          v-for="node in filteredNodes"
          :key="'disk-' + node.id"
          :nodeName="node.name"
          :totalSize="node.total_disk_mb"
          :remainingSize="nodeFreeDisk[node.name]"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useStore } from "vuex";
import MemoryGauge from "./MemoryGaugeComponent.vue";
import DiskGauge from "./DiskGaugeComponent.vue";

const store = useStore();
const selectedChart = ref(""); // 초기값은 선택되지 않은 상태

// 차트 이름 목록
const chartNames = ["Memory Usage", "Disk Usage"];

// 선택된 차트를 업데이트하는 함수
const selectChart = (chartName) => {
  selectedChart.value = chartName;
};

// Computed properties
const filteredNodes = computed(() =>
  store.getters.userNodes.filter((node) =>
    store.state.selectedProjectNodeNames.includes(node.name),
  ),
);
const nodeFreeMemories = computed(() => {
  return filteredNodes.value.reduce((acc, node) => {
    acc[node.name] = store.getters.getNodeMemory(node.name) || 0;
    return acc;
  }, {});
});

const nodeFreeDisk = computed(() => {
  return filteredNodes.value.reduce((acc, node) => {
    acc[node.name] = store.getters.getNodeDisk(node.name) || 0;
    return acc;
  }, {});
});
</script>

<style scoped>
.chart-list-widget {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background-color: #fff;
  margin: 0 auto;
  margin-bottom: 20px;
  width: calc(100% - 10px);
  max-width: 1200px;
}

.chart-list-header {
  background-color: #f9f9f9;
  padding: 12px 16px;
  margin: 0;
  border-bottom: 1px solid #ddd;
}

.chart-list-body {
  display: flex;
  /* Adjust width or flex properties as needed */
}

.chart-name-list {
  /* Adjust width or flex properties as needed */
  flex: 1; /* Take up a portion of the space, adjust as needed */
  /* ... existing styles ... */
}

.chart-display {
  flex: 2; /* Take up more space than the list, adjust as needed */
  /* Additional styles for layout */
  border-left: 1px solid #ddd;
  padding: 16px;
  overflow-y: auto;
}

.memory-gauge-header {
  width: 100%; /* Ensures the header spans the full width */
  text-align: center; /* Center the text */
  margin-top: 0;
  margin-bottom: 20px; /* Space before the gauges */
}

.memory-gauge-wrapper {
  display: flex;
  flex-wrap: wrap; /* Allows gauge containers to wrap */
  width: 100%; /* Takes full width */
}

.memory-gauge-container {
  flex: 1;
  min-width: calc(
    50% - 30px
  ); /* Minimum width for MemoryGauge components, accounting for the gap */
  max-width: calc(
    50% - 30px
  ); /* Maximum width for MemoryGauge components, accounting for the gap */
}

.disk-gauge-header {
  width: 100%; /* Ensures the header spans the full width */
  text-align: center; /* Center the text */
  margin-top: 0;
  margin-bottom: 20px; /* Space before the gauges */
}

.disk-gauge-wrapper {
  display: flex;
  flex-wrap: wrap; /* Allows gauge containers to wrap */
  width: 100%; /* Takes full width */
}

.disk-gauge-container {
  flex: 1;
  min-width: calc(
    50% - 30px
  ); /* Minimum width for MemoryGauge components, accounting for the gap */
  max-width: calc(
    50% - 30px
  ); /* Maximum width for MemoryGauge components, accounting for the gap */
}
</style>
