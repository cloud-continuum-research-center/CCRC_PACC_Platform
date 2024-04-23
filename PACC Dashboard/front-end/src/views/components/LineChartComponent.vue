<template>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, defineProps, computed } from "vue";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";

const props = defineProps({
  nodeData: Object,
  dataType: String, // Add a prop to specify the type of data
});

const chartCanvas = ref(null);
let myChart = null;

const createChartData = (nodeData) => {
  if (!Array.isArray(nodeData)) {
    // nodeData가 배열이 아니면 빈 데이터셋을 반환합니다.
    return {
      labels: [],
      datasets: []
    };
  }

  const dataset = {
    label: 'GPU Temperature',
    data: nodeData,
    borderColor: 'hsl(200, 70%, 50%)',
    fill: false,
    pointRadius: 5
  };

  return {
    labels: nodeData.map((_, i) => i + 1),
    datasets: [dataset]
  };
};

const lineChartData = computed(() => createChartData(props.nodeData));

// Helper function to determine the correct unit
const getUnit = (dataType) => {
  switch (dataType) {
    case "gpuTemperature":
      return "°C";
    case "cpuUtilization":
      return "%";
    case "gpuUtilization":
      return "%";
    case "gpuPowerUsage":
      return "W";
    default:
      return "";
  }
};

const createChartConfig = (chartData, dataType) => ({
  type: "line",
  data: chartData,
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        title: {
          display: true,
          text: "Value",
        },
      },
    },
    plugins: {
      tooltip: {
        mode: "index",
        intersect: false,
      },
      datalabels: {
        color: "#444",
        display: "auto",
        font: {
          weight: "bold",
        },
        formatter: (value) => {
          const unit = getUnit(dataType);
          return `${value}${unit}`; // Now dynamically applying units
        },
      },
    },
  },
  plugins: [ChartDataLabels],
});

onMounted(() => {
  if (chartCanvas.value) {
    const context = chartCanvas.value.getContext("2d");
    if (context) {
      const config = createChartConfig(lineChartData.value, props.dataType);
      myChart = new Chart(context, config);
    } else {
      console.error("Failed to get canvas context");
    }
  } else {
    console.error("Canvas element not found");
  }
});

watch(
  () => [props.nodeData, props.dataType],
  (newValues) => {
    if (myChart) {
      const [newData, newType] = newValues;
      const newChartData = createChartData(newData);
      myChart.data = newChartData;
      myChart.options = createChartConfig(newChartData, newType).options;
      myChart.update();
    }
  },
  { immediate: true },
);
</script>

<style>
.chart-container {
  position: relative;
  height: 35vh; /* Adjust the height as needed */
  width: 35vw; /* Adjust the width to ensure each chart has enough space */
  margin-bottom: 20px; /* Add some space between the chart containers */
}

</style>
