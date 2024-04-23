<template>
  <div class="model-selector-container">
    <!-- Header title for the model selection -->
    <h2 class="model-header">학습 모델 선택</h2>
    <!-- Model list and description container -->
    <div class="model-content">
      <div class="model-list">
        <ul>
          <li
            v-for="model in models"
            :key="model.model_id"
            @click="updateSelectedModel(model)"
            :class="{ selected: model.model_id === selectedModel.model_id }"
          >
            {{ model.name }}
          </li>
        </ul>
      </div>
      <div class="model-description">
        <h3>{{ selectedModel?.name || "No model selected" }}</h3>
        <p>{{ selectedModel?.description || "" }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, defineEmits } from "vue";
import { useStore } from "vuex";

const emit = defineEmits(["update:modelValue"]);

const store = useStore();
const models = computed(() => store.state.models);
const selectedModel = ref({});

onMounted(async () => {
  await store.dispatch("fetchModels");
  if (models.value.length > 0) {
    selectedModel.value = models.value[0]; // Set the first model as selected
    emit("update:modelValue", models.value[0].model_id); // Emit its model_id
  }
});

function updateSelectedModel(model) {
  if (model) {
    selectedModel.value = model;
    emit("update:modelValue", model.model_id); // Emit the model_id
  }
}
</script>

<style scoped>
.model-selector-container {
  border: 1px solid #e0e0e0; /* 경계선 설정 */
  background-color: #fff; /* 배경색 흰색 */
  border-radius: 12px; /* 모서리를 둥글게 */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* 그림자 효과 추가 */
  display: flex; /* flexbox 레이아웃 사용 */
  flex-direction: column; /* 자식 요소를 세로로 정렬 */
  overflow: hidden; /* 내용이 넘칠 경우 숨김 */
}
.model-list ul li
{
   font-size: 19px; /* 글꼴 크기 */

}

.model-header {
  text-align: left; /* 텍스트 왼쪽 정렬 */
  padding: 15px 20px; /* 패딩 설정 */
  background: #f8f8f8; /* 배경색 연한 회색 */
  font-size: 34px; /* 글꼴 크기 */
  font-weight: 600; /* 글꼴 두께 */
  color: #333; /* 글꼴 색상 */
  border-bottom: 1px solid #ddd; /* 하단에 경계선 추가 */
  margin-bottom: 0px;   /* 마진 0으로 안하면 리스트와 헤더 사이에 붕 뜸*/
}

.model-content {
  display: flex; /* flexbox 레이아웃 사용 */
}

.model-list ul {
  list-style-type: none; /* 리스트 스타일 없앰 */
  padding: 0; /* 패딩 없앰 */
  margin: 0; /* 마진 없앰 */
  width: 250px; /* 너비 설정 */
  border-right: 1px solid #ddd; /* 오른쪽에 경계선 추가 */
}

.model-list li {
  padding: 15px 20px; /* 패딩 설정 */
  cursor: pointer; /* 마우스 오버 시 포인터 모양 변경 */
  transition: background-color 0.3s; /* 배경색 변경 시 애니메이션 효과 */
  font-size: 16px; /* 글꼴 크기 */
  color: #333; /* 글꼴 색상 */
  border-bottom: 1px solid #eee; /* 아래쪽에 경계선 추가 */
  font-weight: bold;
}

.model-list li:hover,
.model-list li.selected {
  background-color: #e3f2fd; /* 배경색 변경 */
}

.model-description {
  padding: 20px; /* 패딩 설정 */
  flex-grow: 1; /* 남은 공간을 채움 */
  background-color: #fafafa; /* 배경색 연한 회색 */
  border-radius: 0 12px 12px 0; /* 오른쪽 모서리를 둥글게 */
}

.model-description p {
  font-size: 22px; /* 글꼴 크기 */
  color: #666; /* 글꼴 색상 */
  margin-bottom: 10px; /* 아래쪽 마진 추가 */
  line-height: 1.4; /* 줄 간격 설정 */
}

.model-description h3 {
  margin-top: 0; /* 위쪽 마진 제거 */
  font-size: 25px; /* 글꼴 크기 */
  color: #333; /* 글꼴 색상 */
}

@media (max-width: 768px) {
  .model-selector-container {
    flex-direction: column; /* 화면이 작을 때 세로로 배치 */
  }

  .model-list ul {
    width: auto; /* 너비를 자동으로 조정 */
    border-right: none; /* 경계선 제거 */
  }

  .model-list li {
    border-bottom: none; /* 경계선 제거 */
  }
}


</style>
