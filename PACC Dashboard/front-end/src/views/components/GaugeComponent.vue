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
  totalSize: Number,
  remainingSize: Number,
  nodeName: String,
});

const chartCanvas = ref(null);
let myChart = null;

const createChartData = (totalSize, remainingSize) => {
  const usedSize = totalSize - remainingSize;
  return {
    labels: ["Used", "Free"],
    datasets: [
      {
        label: "Memory Usage",
        data: [usedSize, remainingSize],
        backgroundColor: ["#42A5F5", "#ddd"],
        borderWidth: 0,
      },
    ],
  };
};

const memoryUsageData = computed(() =>
  createChartData(props.totalSize, props.remainingSize),
); // Now using computed

// Chart.js chart configuration
// Chart.js chart configuration
const createChartConfig = (chartData, nodeName) => {
  const totalSize = chartData.datasets[0].data.reduce((a, b) => a + b, 0);

  return {
    type: "doughnut",
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "50%", // You may adjust this for better label positioning
      animation: {
        animateRotate: true,
        animateScale: false,
      },
      circumference: 180,
      rotation: 270,
      plugins: {
        tooltip: {
          enabled: false, // Disable default tooltips
        },
        datalabels: {
          color: "#000000", // Set color of the labels
          textAlign: "center",
          font: {
            weight: "bold",
            size: 18,
          },
          formatter: (value, context) => {
            // Display integer values instead of decimals
            if (context.dataIndex === 0) {
              // Used memory label
              return parseInt(value) + "MB";
            } else {
              // Remaining memory label
              return parseInt(value) + "MB";
            }
          },
          anchor: "center",
          align: "center",
          offset: -10, // Adjust offset as needed
          labels: {
            title: {
              font: {
                size: "18",
              },
            },
            value: {
              color: "black",
            },
          },
        },
        // Additional configuration for the center label
        centerLabel: {
          color: "#FF6384",
          font: {
            weight: "bold",
            size: "20", // Size of the center label
          },
          // You could create a custom plugin to handle this but for simplicity, we're defining the style here
        },
        title: {
          display: true,
          text: nodeName,
          position: "top",
          color: "#666",
          font: {
            size: 16,
          },
        },
      },
    },
    plugins: [
      ChartDataLabels,
      {
        // Plugin to render the center label
        afterDraw: (chart) => {
          let ctx = chart.ctx;
          ctx.save();
          const centerLabel =
            ((chartData.datasets[0].data[0] / totalSize) * 100).toFixed(2) +
            "%"; // Calculate percentage
          const centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
          const centerY = chart.chartArea.bottom - 40;
          ctx.font = "30px Arial";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillStyle = "90ee90"; // Center label color
          ctx.fillText(centerLabel, centerX, centerY);
          ctx.restore();
        },
      },
    ], // Register the plugin here
  };
};

onMounted(() => {
  if (chartCanvas.value) {
    const context = chartCanvas.value.getContext("2d");
    if (context) {
      const config = createChartConfig(memoryUsageData.value, props.nodeName);
      myChart = new Chart(context, config);
    } else {
      console.error("Failed to get canvas context");
    }
  } else {
    console.error("Canvas element not found");
  }
});

watch(
  () => [props.totalSize, props.remainingSize],
  (newValues) => {
    if (myChart) {
      const newChartData = createChartData(...newValues);
      myChart.data = newChartData;
      myChart.options = createChartConfig(newChartData, props.nodeName).options;
      myChart.update();
    }
  },
  { immediate: true },
);
</script>

<style>
.chart-container {
  overflow: visible; /* Ensures no clipping */
  opacity: 1; /* Checks that it's not hidden */
  position: relative;
  height: 40vh;
  width: calc(50vw - 40px);
}
</style>
