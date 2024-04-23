<template>
  <div class="project-widget">
    <h4 class="project-widget-header">학습 모델 리스트</h4>
    <div class="project-widget-body">
      <div class="project-list-container">
        <ul class="project-list">
          <li
            v-for="(project, index) in lastFiveProjects"
            :key="index"
            @click="selectProject(project)"
            :class="{ 'is-selected': project.id === selectedProject.id }"
          >
            {{ index + 1 }}. {{ project.model_name }} 
          </li>
        </ul>
      </div>
      <div class="project-description-container">
        <h4>{{ selectedProject.model_name || "학습 모델 선택" }}</h4>
        <div v-if="selectedProject.project_nodes">
          
        <p class="project-detail dataset-name">학습 데이터 셋: {{ selectedProject.dataset_name }}</p>
        <p class="project-detail project-status">현재 상태: {{ selectedProject.status }}</p>
        <p class="project-detail start-time">시작 일시: {{ selectedProject.created_at }}</p>
        <p class="project-detail nodes-list">학습 노드: {{ parseNodes(selectedProject.project_nodes) }}</p>

        </div>
      </div>
      <button
        v-if="selectedProject.status === '학습 중'"
        @click="stopTraining(selectedProject.id)"
        class="stop-training-button"
      >
        학습 중단
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useStore } from "vuex";
import axios from "axios";
import { onMounted, onUnmounted } from 'vue';

let intervalId;

const store = useStore();
// Log the initial state of projects from the store
console.log(
  "Initial projects from the store:",
  store.getters.userProjects,
);

const projects = computed(() => {
  const projectsFromStore = store.getters.userProjects;
  console.log(
    "프로젝트 정보 가져옴:",
    projectsFromStore,
  ); // Log computed projects
  return projectsFromStore;
});

const lastFiveProjects = computed(() => {
  const totalProjects = projects.value.length;
  return projects.value.slice(Math.max(totalProjects - 5, 0)).reverse();
});


const selectedProject = ref({});

watch(
  () => store.getters.userProjects,
  (newProjects) => {
    console.log(
      " Watch triggered for projects update:",
      newProjects,
    ); // Log on update
    // Update logic as is
  },
  { deep: true },
);

watch(selectedProject, (newProject) => {
  console.log("선택된 프로젝트 갱신:", newProject);
});
const selectProject = (project) => {
  console.log("Project selected:", project);
  selectedProject.value = project;
  if (project.status !== "중단됨") {
    store.commit('setSelectedProjectId', project.id)
    const nodeNames = JSON.parse(project.project_nodes);
    store.dispatch("updateSelectedProjectNodeNames", nodeNames);
  }
};


let isFirst = false;

onMounted(() => {

  intervalId = setInterval(executePeriodically, 1000);

 
});

onUnmounted(() => {
  clearInterval(intervalId);
});

const executePeriodically = () => {

  if(isFirst==false){
    
     console.log("Mounted ProjectsList component");
  if (lastFiveProjects.value.length > 0 && isFirst == false) {
    console.log("Selecting the last project from the list");
    selectProject(lastFiveProjects.value[0]);
      isFirst = true;
      
  }
    return;
  }
  // 여기에 매초 실행하고 싶은 로직을 추가하세요.
};


const parseNodes = (nodesJson) => {
  try {
    return JSON.parse(nodesJson).join(", "); // Assuming the nodes are stored in a simple array
  } catch (e) {
    return "Error parsing nodes";
  }
};

const stopTraining = async () => {
  if (!selectedProject.value || !selectedProject.value.id) {
    console.error(
      "No project selected or selected project does not have an id",
    );
    return;
  }
  try {
    const response = await axios.post(
      "http://l163.180.117.23:5000/api/stop-training",
      { projectId: selectedProject.value.id },
      { headers: { Authorization: `Bearer ${store.state.authToken}` } },
    );
    if (response.data.success) {
      console.log("학습 중단 요청 성공", selectedProject.value.id);
      alert("학습 중단 요청이 성공했습니다."); // Alert for success
      // Refetch projects to update the list
      await store.dispatch("fetchProjects");
      // Update selectedProject to reflect the changes if it's still selected
      const updatedProject = store.getters.userProjects.find(
        (p) => p.id === selectedProject.value.id,
      );
      if (updatedProject) {
        selectedProject.value = updatedProject;
      }
    } else {
      // Handle case where response.data.success is false
      throw new Error("학습 중단 요청이 실패했습니다.");
    }
  } catch (error) {
    console.error("학습 중단 요청 실패", selectedProject.value.id, error);
    // Display an error message to the user
    alert("학습 중지 요청에 실패하였습니다."); // Use a more user-friendly error handling instead of alert
  }
};
</script>

<style scoped>

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
  color: #333;
}

.project-detail {
  font-size: 16px; /* 크기 증가 */
  color: #000000; /* 더 진한 회색으로 변경 */
  margin-bottom: 8px; /* 여백 조절 */
  font-weight: bold;
}

.dataset-name {
  font-weight: bold; /* 더 강조된 폰트 두께 */
}

.project-status {
  color: #000000; /* 상태에 따라 다른 색상을 적용할 수 있습니다. 예: 진행 중일 때는 녹색 */
  font-weight: bold;
}

.start-time {
  color: #000000; /* 시작 시간을 빨간색으로 표시 */
  font-weight: bold;
}

.nodes-list {
  color: #000000; /* 노드 목록을 파란색으로 표시 */
  font-weight: bold;
}



.project-widget {
  border: 1px solid #e0e0e0; /* 더 섬세한 경계선 */
  border-radius: 12px; /* 더 둥근 모서리 */
  overflow: hidden;
  background-color: #fff;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1); /* 부드러운 그림자 추가 */
  margin: 0 auto; /* Center the widget */
  margin-bottom: 20px; /* Add bottom margin */
  max-width: 100%; /* Optionally add a max-width if you want to limit the size on larger screens */
}

.project-widget-header {
  background-color: #f5f5f5; /* 더 부드러운 배경색 */
  border-bottom: 1px solid #e0e0e0; /* 조화로운 경계선 */
  padding: 12px 16px;
  margin: 0;
  index: -1;
}

.project-widget-body {
  display: flex;
  flex-direction: row;
  position: relative; /* 부모 컨테이너에 상대적 위치 지정 */
}
.project-list-container {
  
  max-height: 250px; /* Set this to whatever height you want */
  overflow-y: auto; /* This will allow scrolling */
  max-width: 100%; /* Set the max width as needed */
  border-right: 1px solid #ddd;
  flex: 2;
  
}
.project-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 21px; /* 적절한 폰트 사이즈 */
}

.project-description-container {
  width: 450px; /* Set the width as needed */
  padding: 11px;
  font-size: 16px; /* 적절한 폰트 사이즈 */
}

.project-actions-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}


.stop-training-button {
  position: absolute; /* 절대 위치 지정 */
  top: 10px; /* 상단에서 10px 떨어진 위치 */
  right: 10px; /* 우측에서 10px 떨어진 위치 */
  height: 45px;
  width: 135px;
  border-radius: 25px;
  background-color: #778899;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 195px; /* Adds some space at the bottom */
  margin-right: -5px; /* Adds some space at the right */
}

.stop-training-button:hover {
  background-color: #ef5350; /* Slightly darker green color for the hover state */
}
button:hover {
  transform: scale(1.05); /* 약간 확대 */
}
.project-list li {
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.project-list li:hover {
  background-color: #f0f0f0; /* 마우스 오버 시 배경색 변경 */
}

.project-list li.is-selected {
  background-color: #e8f0f9; /* 선택된 항목의 배경색 변경 */
  font-weight: bold; /* 선택된 항목의 텍스트를 굵게 표시 */
}


button {
  border-radius: 5px; /* Adjust the pixel value to control the roundness */
  background-color: #90ee90; /* This is a light green color */
  border: none; /* Removes the default border */
  padding: 10px 20px; /* Adds some padding inside the button */
  color: rgb(0, 0, 0); /* Changes the text color to white */
  font-size: 16px; /* Adjust the font size as needed */
  cursor: pointer; /* Changes the cursor to a pointer when hovering over the button */
  transition: background-color 0.3s; /* Smooth transition for background color */
}

button:hover {
  background-color: #76c893; /* Slightly darker green color for the hover state */
}
</style>
