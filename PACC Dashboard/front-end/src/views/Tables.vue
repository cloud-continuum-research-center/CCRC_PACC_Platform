<script setup>
import { reactive, ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";
import ModelselectBox from "./components/ModelSelector.vue";
import DatasetselectBox from "./components/DatasetSelector.vue";
import HyperparameterselectBox from "./components/HyperparameterSelector.vue";
import NodeselectBox from "./components/NodeSelector.vue";
import axios from "axios";

const store = useStore();
const router = useRouter(); // Instantiate the router
const isCreatingProject = ref(false);
const creationSuccess = ref(false); // New ref to track creation success
const authToken = computed(() => store.state.authToken);

const projectData = reactive({
  model: {}, // Initially an object, later to be just a string of model_id
  dataset: {}, // Initially an object, later to be just a string of dataset_id
  hyperparameters: {}, // Already in the desired format
  nodes: [], // Initially an array of objects, later to be an array of node names
});

watch(
  projectData.hyperparameters,
  (newVal) => {
    console.log("Hyperparameters updated:", newVal);
  },
  { deep: true },
);

watch(creationSuccess, (newValue) => {
  if (newValue) {
    alert("프로젝트가 생성되었습니다."); // Alert the user about success
    creationSuccess.value = false; // Reset the creation success state
    router.push("/dashboard-default"); // Redirect to the Dashboard page
  }
});

// const handleSelectedNodeChange = (selectedNode) => {
//   const index = projectData.nodes.findIndex(node => node.id === selectedNode.id);
//   if (index > -1) {
//     // Node is already selected, remove it
//     projectData.nodes.splice(index, 1);
//   } else {
//     // Node is not selected, add it
//     projectData.nodes.push(selectedNode);
//   }
// };

const prepareDataForSubmission = () => {
  return {
    model: projectData.model.model_id,
    dataset: projectData.dataset.dataset_id,
    hyperparameters: {
      ...projectData.hyperparameters,
      optimizer: projectData.hyperparameters.optimizer,
      lossFunction: projectData.hyperparameters.lossFunction,
    },
    nodes: projectData.nodes.map((node) => node.name),
  };
};

const hyperparametersSelected = (newHyperparameters) => {
  projectData.hyperparameters = {
    ...projectData.hyperparameters,
    ...newHyperparameters,
  };
};

// Method to send data to backend
const createProject = async () => {
  try {
    isCreatingProject.value = true;
    const formattedData = prepareDataForSubmission(); // 전달 데이터 형식 변경
    lastSubmittedData.value = formattedData;
    const config = {
      headers: {
        Authorization: `Bearer ${authToken.value}`,
      },
    };

    const response = await axios.post(
      "http://ec2-3-36-137-217.ap-northeast-2.compute.amazonaws.com:5000/api/create-project",
      formattedData,
      config,
    );

    // 프로젝트 생성이 성공했다면, 노드 정보 업데이트
    if (response && response.status === 200) {
      console.log("Project created successfully:", response.data);
      // 프로젝트 생성 후 노드 정보 새로고침
      await store.dispatch("fetchNodes");
      creationSuccess.value = true; // Indicate that the project was created
      // 성공 메시지 처리 또는 사용자 인터페이스 업데이트 등의 추가적인 처리를 여기에 추가할 수 있습니다.
    }
    console.log(response.data);
    // Handle successful project creation (e.g., redirect or show message)
  } catch (error) {
    console.error("Failed to create project:", error);
    // Handle errors (e.g., show error message)
  } finally {
    isCreatingProject.value = false;
  }
};

const modelIdSelected = (modelId) => {
  if (modelId) {
    const fullModel = store.state.models.find(
      (model) => model.model_id === modelId,
    );
    if (fullModel) {
      projectData.model = fullModel; // Assign the full model object
    } else {
      console.error("Model not found!");
    }
  }
};

const datasetSelected = (datasetId) => {
  projectData.dataset = { dataset_id: datasetId };
};

const lastSubmittedData = ref(null); // 백엔드로 마지막으로 전송된 데이터를 저장
</script>

<template>
  <div class="container-fluid">
    <div class="py-5-container-fluid">
      <div class="row">
        <div class="col-12">
          <ModelselectBox @update:modelValue="modelIdSelected" />
        </div>
      </div>
    </div>

    <div class="py-2 container-fluid">
      <div class="row">
        <div class="col-12">
          <DatasetselectBox @update:modelValue="datasetSelected" />
        </div>
      </div>
    </div>

    <div class="py-2 container-fluid">
      <div class="row">
        <div class="col-12">
          <HyperparameterselectBox
            @update:modelValue="hyperparametersSelected"
          />
        </div>
      </div>
    </div>

    <div class="py-2 container-fluid">
      <div class="row">
        <div class="col-12">
          <NodeselectBox v-model="projectData.nodes" />
        </div>
      </div>
    </div>

    <div class="create-project-button-container">
      <button
        class="create-project-button"
        @click="createProject"
        :disabled="isCreatingProject"
      >
        {{ isCreatingProject ? "생성 중" : "프로젝트 생성" }}
      </button>
    </div>
    
  </div>
</template>
<style scoped>
.py-5-container-fluid {
  padding: 10px;
  height: 270px;
}

.container-fluid {
  padding: 10px; /* 모든 패딩 제거 */
}

.create-project-button-container {
  text-align: right; /* 버튼을 오른쪽 정렬 */
  padding: 0px 0px; /* 상단과 하단 여백 */
}

.create-project-button {
  padding: 10px 30px; /* 버튼 내부 패딩 */
  margin-top: 20px; /* 버튼 위쪽 여백 */
  margin-bottom: 0; /* 버튼 아래쪽 여백 제거 */
  background-color: #4CAF50; /* 진한 초록색 배경 */
  color: white; /* 텍스트 색상을 흰색으로 변경 */
  font-size: 18px; /* 글꼴 크기 증가 */
  font-weight: bold; /* 글꼴 두께를 굵게 */
  border: none; /* 테두리 제거 */
  border-radius: 8px; /* 둥근 모서리 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 그림자 추가 */
  cursor: pointer;
  transition: all 0.3s ease; /* 부드러운 전환 효과 */
}

.create-project-button:hover {
  background-color: #45a049; /* 호버 상태의 배경색 변경 */
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2); /* 호버 시 그림자 확대 */
}

.last-submitted-data-container {
  margin-top: 20px;
  background-color: #fbfafa;
  padding: 15px;
  border-radius: 5px;
}

button {
  border-radius: 5px; /* 버튼 모서리 둥글게 */
  background-color: #90ee90; /* 밝은 초록색 배경 */
  border: none; /* 테두리 없음 */
  padding: 10px 20px; /* 내부 패딩 */
  color: rgb(0, 0, 0); /* 글자 색상 */
  font-size: 16px; /* 글자 크기 */
  cursor: pointer; /* 커서 포인터 */
  transition: background-color 0.3s; /* 배경색 변경 애니메이션 */
  margin-right : 10px;
}

button:hover {
  background-color: #76c893; /* 버튼 호버 색상 변경 */
}
</style>
