
<template>
  <div class="dashboard">
    <div class="project-list-container">
      <ProjectList />
    </div>
    <div class="project-info-widget" v-if="projectInfo">
    <div class="tarining-status-header">
    <h4>학습 상태</h4>
    </div>
    <p> </p> 
    <p> </p> 
    <p> </p> 
    <p class="project-info-highlight">모델 학습 진행율: {{ projectInfo.progress ? `${projectInfo.progress}%` : '0' }}</p>
    <p class="project-info-highlight epoch">모델 훈련 횟수: {{ projectInfo.epoch === -1 ? '0' : (projectInfo.epoch !== undefined ? projectInfo.epoch : '0') }}</p>
    <p class="project-info-highlight accuracy">모델 정확도: {{
  typeof projectInfo.accuracy === 'number' ? 
  (projectInfo.accuracy > 100 ? '100%' : projectInfo.accuracy.toFixed(2) + '%') : '0%'
}}</p>

<p class="project-info-highlight loss">모델 Loss 값: {{ projectInfo.loss ? projectInfo.loss.toFixed(4) : '0' }}</p>
       
  </div>
  </div>
  <div class="project-info-widget-chart" v-if="projectInfo">
<canvas ref="lineChart1" class="canvas-size"></canvas>
<canvas ref="lineChart2" class="canvas-size"></canvas>
<canvas ref="pieChart1" class="canvas-size"></canvas>
<canvas ref="pieChart2" class="canvas-size"></canvas>
    </div>
</template>



<script setup>
import ProjectList from "./components/ProjectsList.vue";
import { onMounted, watch, computed, onUnmounted, ref , nextTick } from "vue";
import { useStore } from "vuex";
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);
const lineChart1 = ref(null);
const lineChart2 = ref(null);
const pieChart1 = ref(null);
const pieChart2 = ref(null);

let currentepoch = 0;

function generateLabels(data) {
  console.log(data);
  return data.map((_, index) => `epoch ${index + 1}`);
}
let myLineChart1 = null;
let myLineChart2 = null;
let myPieChart1 = null;
let myPieChart2 = null;


const setupCharts = () => {


  nextTick(() => {
    // 기존 차트 파괴
    if (myLineChart1) myLineChart1.destroy();
    if (myLineChart2) myLineChart2.destroy();
    if (myPieChart1) myPieChart1.destroy();
    if (myPieChart2) myPieChart2.destroy();

    // Setup line chart 1
    const lineChart1Ctx = lineChart1.value.getContext('2d');
    

    myLineChart1 = new Chart(lineChart1Ctx, {
      type: 'line',
      data: {
        labels: generateLabels(projectInfo.value.accuracyHistory),
        datasets: [{
          label: 'Accuracy',
          data: projectInfo.value.accuracyHistory,
          fill: false,
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        }]
      },
  options: {
    scales: {
      x: {
        ticks: {
          font: {
            size: 16 // x축 라벨의 글씨 크기
          }
        }
      },
      y: {
        ticks: {
          font: {
            size: 16 // y축 라벨의 글씨 크기
          }
        }
      }
    },
    plugins: {
      legend: {
        labels: {
          font: {
            size: 25 // 범례의 글씨 크기
          }
        }
      }
    }
  }
});



    // Setup line chart 2
    const lineChart2Ctx = lineChart2.value.getContext('2d');
    myLineChart2 = new Chart(lineChart2Ctx, {
      type: 'line',
      data: {
        labels: generateLabels(projectInfo.value.lossHistory),
        datasets: [{
          label: 'Loss',
          data: projectInfo.value.lossHistory,
          fill: false,
          borderColor: 'rgb(255, 99, 132)',
          tension: 0.1
        }]
      },options: {
    scales: {
      x: {
        ticks: {
          font: {
            size: 16 // x축 라벨의 글씨 크기
          }
        }
      },
      y: {
        ticks: {
          font: {
            size: 16 // y축 라벨의 글씨 크기
          }
        }
      }
    },
    plugins: {
      legend: {
        labels: {
          font: {
            size: 25 // 범례의 글씨 크기
          }
        }
      }
    }
  }
});


  let cpuUtilizationKeys = Object.keys(projectInfo.value.node_cpu_utilization_list);
  let gpuUtilizationKeys = Object.keys(projectInfo.value.node_gpu_utilization_list);

  let cpuUtilizationValues = Object.values(projectInfo.value.node_cpu_utilization_list);
  var gpuUtilizationValues = Object.values(projectInfo.value.node_gpu_utilization_list);

  if (gpuUtilizationValues.every(value => value === 0)) {
        // 모든 원소를 1로 변경
        gpuUtilizationValues.fill(1);
      }

    // GPU 키의 길이가 0인 경우 라벨 변경
    if (gpuUtilizationKeys.length === 0) {
      gpuUtilizationKeys = ["GPU 사용 대기"];
      gpuUtilizationValues = [1];  // 차트에 표시할 기본값 제공
    }

      if (cpuUtilizationKeys.length === 0) {
      cpuUtilizationKeys = ["CPU 사용 대기"];
      cpuUtilizationValues = [1];  // 차트에 표시할 기본값 제공
    }

    // Setup pie chart 1
    const pieChart1Ctx = pieChart1.value.getContext('2d');
    myPieChart1 = new Chart(pieChart1Ctx, {
      type: 'pie',
      data: {
        labels: cpuUtilizationKeys,
        datasets: [{
          label: 'Node CPU Utilization',
          data:cpuUtilizationValues,
          backgroundColor: ['rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 205, 86)', 'rgb(75, 192, 192)']
        }]
      },
  options: {
    plugins: {
      legend: {
        labels: {
          font: {
            size: 16  // 범례의 글씨 크기 설정
          }
        }
      },
      tooltip: {
        bodyFont: {
          size: 16  // 툴팁 본문의 글씨 크기 설정
        }
      }
    }
  }
});

    // Setup pie chart 2
    const pieChart2Ctx = pieChart2.value.getContext('2d');
    myPieChart2 = new Chart(pieChart2Ctx, {
      type: 'pie',
      data: {
        labels: gpuUtilizationKeys,
        datasets: [{
          label: 'Node GPU Utilization',
          data: gpuUtilizationValues,
          backgroundColor: ['rgb(75, 192, 192)', 'rgb(153, 102, 255)', 'rgb(255, 159, 64)', 'rgb(233, 30, 99)']
        }]
      },
       options: {
    plugins: {
      legend: {
        labels: {
          font: {
            size: 16  // 범례의 글씨 크기 설정
          }
        }
      },
      tooltip: {
        bodyFont: {
          size: 16  // 툴팁 본문의 글씨 크기 설정
        }
      }
    }
  }
});
  });
};























const store = useStore();
const intervalId = ref(null); // Use a ref to keep track of the interval ID

let isFirst = false;

function startFetching(projectId) {
  if (intervalId.value) {
    clearInterval(intervalId.value); // Clear the current interval if it exists
  }

  
  intervalId.value = setInterval(() => {
  console.log("currentepoch " + currentepoch + " projectInfo.value.epoch " + projectInfo.value.epoch)
  store.dispatch("fetchProjectInfoById", projectId);

    if(projectInfo.value.epoch == -1){
      console.log("projectInfo.value.epoch == -1");
      return;
    }

    if(currentepoch == projectInfo.value.epoch){
        
      if(isFirst == false && projectInfo.value.currentstate == 2){
         setupCharts();
         isFirst = true;
          return;
        }          
        return;
     }
    currentepoch = projectInfo.value.epoch;
    
    setupCharts();
  }, 1000); // Fetch every 3 seconds
}






onMounted(() => {
  if (store.state.authToken && store.state.userEmail) {
    store.dispatch("fetchProjects");
    // Assuming project ID is already selected somewhere and stored in the state
    if (store.state.selectedProjectId) {
      startFetching(store.state.selectedProjectId);
    }
  }
  setupCharts();
});

watch(() => store.state.selectedProjectId, (newId) => {
  if (newId && store.state.authToken && store.state.userEmail) {
    store.dispatch("fetchProjectInfoById", newId); // Fetch immediately when ID changes
    startFetching(newId); // Start or restart the fetching interval
  } else {
    if (intervalId.value) {
      clearInterval(intervalId.value); // Clear the interval if the ID becomes invalid
      intervalId.value = null;
    }
  }
}, { immediate: true });

onUnmounted(() => {
  // Clean up the interval when the component is destroyed
  if (intervalId.value) {
    clearInterval(intervalId.value);
  }
  if (myLineChart1) myLineChart1.destroy();
  if (myLineChart2) myLineChart2.destroy();
  if (myPieChart1) myPieChart1.destroy();
  if (myPieChart2) myPieChart2.destroy();
});

// Computed property to display project info
const projectInfo = computed(() => {
  console.log("projectInfo updated", store.state.projectsInfo[store.state.selectedProjectId]);
  const data = store.state.projectsInfo[store.state.selectedProjectId] || {};

   let gpuUtilizationList = data.node_gpu_utilization || [];
  if (gpuUtilizationList.length > 0 && gpuUtilizationList.every(value => value === 0)) {
    gpuUtilizationList = gpuUtilizationList.map(() => 1);  // Replace all zeros with ones
  }

  let cpuUtilizationList = data.node_cpu_utilization || [];
  if (cpuUtilizationList.length > 0 && cpuUtilizationList.every(value => value === 0)) {
    cpuUtilizationList = cpuUtilizationList.map(() => 1);  // Replace all zeros with ones
  }

  return {
    progress: data.progress || 0,
    epoch: data.epoch || -1,
    accuracy: (data.accuracy && data.accuracy.length > 0) ? data.accuracy[data.accuracy.length - 1] : 0,
    loss: (data.loss && data.loss.length > 0) ? data.loss[data.loss.length - 1] : 0,
    accuracyHistory: data.accuracy || [],
    lossHistory: data.loss || [],
    currentstate: data.current_state || 0,
    node_cpu_utilization_list : cpuUtilizationList,
    node_gpu_utilization_list : gpuUtilizationList
  };
});
</script>


<style>

.project-info-widget
{
  margin-left: 20px;
}

.project-info-widget-chart {
  display: flex;
  gap: 20px;
  padding: 20px;
  align-items: flex-start; /* 요소들을 컨테이너의 왼쪽에 정렬 */
  justify-content: flex-start;

  justify-content: space-around; /* 공간을 균등하게 분배 */
}

.canvas-size {
  width: 350px !important; /* 너비 조정 */
  height: 350px !important; /* 높이 조정 */
}

.dashboard {
  display: flex;
  align-items: flex-start; /* 요소들을 컨테이너의 상단에 정렬 */
  justify-content: flex-start; /* 요소들을 컨테이너의 왼쪽에서 시작하도록 정렬 */
  gap: 20px; /* 요소들 사이의 간격 */
  padding: 20px; /* 대시보드 패딩 */
  
}


.project-list-container {
  min-width: 800px; /* 최소 너비 설정 */
  max-height: 500px; /* 최대 높이 설정 */
  height: 275px; /* 높이 100%로 설정 */

}

.project-info-widget {
  flex: 1; /* 유연하게 너비 조정 */
  flex-grow: 2; /* 컨테이너가 더 많은 공간을 차지하도록 설정 */
  padding: 20px; 
  margin-top: 0; /* 위쪽 마진 제거 */
  border: 1px solid #ccc; /* 테두리 설정 */
  border-radius: 12px;
  background-color: #fff;
  box-shadow: 0 25px 30px rgba(0, 0, 0, 0.07);
  height: 310px;
}


/* 헤더 스타일 */
h4 {
  margin-bottom: 20px; /* 여백을 더 줍니다 */
  font-size: 22px; /* 크기를 키웁니다 */
  font-weight: 600; /* 조금 더 강조된 두께 */
  color: #333; /* 색상은 약간 어두운 회색으로 조정 */
}

/* 단락 스타일 */
p {
  font-size: 18px; /* 텍스트 크기를 키웁니다 */
  color: #666; /* 색상은 좀 더 연한 회색으로 조정 */
  margin-bottom: 10px; /* 단락 사이의 여백을 조정 */
  line-height: 1.4; /* 줄 간격을 조정하여 가독성을 높입니다 */
}


.project-info-highlight {
  font-size: 20px; /* 크기 변경 */
  font-weight: 500; /* 더 강조된 폰트 두께 */
  font-weight: bold; /* 볼드체로 변경 */
  color: #1a237e; /* 진한 파란색으로 변경 */
}

.progress {
  font-size: 20px; /* 크기 변경 */
  font-weight: bold; /* 볼드체로 변경 */
  color: #4caf50; /* 진한 녹색으로 변경 */
}

.epoch {
  font-size: 20px; /* 크기 변경 */
  font-weight: bold; /* 볼드체로 변경 */
  color: #ff9800; /* 주황색으로 변경 */
}

.accuracy {
  font-size: 20px; /* 크기 변경 */
  font-weight: bold; /* 볼드체로 변경 */
  color: #009688; /* 테일 그린색으로 변경 */
}

.loss {
  font-size: 20px; /* 크기 변경 */
  font-weight: bold; /* 볼드체로 변경 */
  color: #f44336; /* 빨간색으로 변경 */
}


</style>
