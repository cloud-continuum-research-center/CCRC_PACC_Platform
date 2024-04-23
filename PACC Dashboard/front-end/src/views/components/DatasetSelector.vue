<template>
  <div class="dataset-selector-container">
    <h2 class="dataset-header">학습 데이터 선택</h2>
    <div class="dataset-content">
      <div class="dataset-list">
        <ul>
          <li
            v-for="dataset in datasets"
            :key="dataset.dataset_id"
            @click="updateSelectedDataset(dataset)"
            :class="{
              selected: dataset.dataset_id === selectedDataset.dataset_id,
            }"
          >
            {{ dataset.name }}
          </li>
        </ul>
      </div>
      <div class="dataset-description">
        <h3>{{ selectedDataset?.name || "No dataset selected" }}</h3>
        <p>{{ selectedDataset?.description || "" }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineEmits } from "vue";
import { useStore } from "vuex";

const emit = defineEmits(["update:modelValue"]);

const store = useStore();
const datasets = computed(() => store.state.datasets);
const selectedDataset = ref({});

onMounted(async () => {
  await store.dispatch("fetchDatasets");
  if (datasets.value.length > 0) {
    selectedDataset.value = datasets.value[0]; // Set the first dataset as selected
    emit("update:modelValue", datasets.value[0].dataset_id); // Emit its dataset_id
  }
});

function updateSelectedDataset(dataset) {
  if (dataset) {
    selectedDataset.value = dataset;
    emit("update:modelValue", dataset.dataset_id); // Emit the dataset_id
  }
}
</script>

<style scoped>
.dataset-selector-container {
  border: 1px solid #e0e0e0; /* 테두리를 회색으로 설정합니다. */
  background-color: #fff; /* 배경색을 흰색으로 설정합니다. */
  border-radius: 12px; /* 테두리의 모서리를 둥글게 처리합니다. */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* 그림자를 추가하여 입체감을 줍니다. */
  display: flex; /* flexbox 레이아웃을 사용하여 자식 요소들을 효율적으로 정렬합니다. */
  flex-direction: column; /* 자식 요소들을 세로로 정렬합니다. */
  overflow: hidden; /* 컨테이너의 크기를 벗어나는 내용을 숨깁니다. */
  margin-top: 30px; /* 위쪽 마진을 추가합니다. */
}

.dataset-header {
  text-align: left; /* 텍스트를 왼쪽에 정렬합니다. */
  padding: 15px 20px; /* 헤더에 내부 여백을 추가합니다. */
  background: #f8f8f8; /* 헤더 배경색을 연한 회색으로 설정합니다. */
  font-size: 34px; /* 글꼴 크기를 설정합니다. */
  font-weight: 600; /* 글꼴 두께를 강조합니다. */
  color: #333; /* 글꼴 색상을 어두운 회색으로 설정합니다. */
  border-bottom: 1px solid #ddd; /* 헤더 아래에 경계선을 추가합니다. */
  margin-bottom: 0px;   /* 마진 0으로 안하면 리스트와 헤더 사이에 붕 뜸*/
}

.dataset-content {
  display: flex; /* 데이터셋 리스트와 설명을 가로로 나란히 정렬합니다. */
}

.dataset-list ul {
  list-style-type: none; /* 리스트의 기본 스타일을 없앱니다. */
  padding: 0; /* 내부 여백을 제거합니다. */
  margin: 0; /* 외부 여백을 제거합니다. */
  width: 250px; /* 너비를 설정합니다. */
  border-right: 1px solid #ddd; /* 오른쪽에 경계선을 추가합니다. */
}

.dataset-list li {
  font-weight: bold;
  padding: 15px 20px; /* 리스트 아이템에 내부 여백을 추가합니다. */
  cursor: pointer; /* 마우스 커서를 포인터로 변경합니다. */
  transition: background-color 0.3s; /* 배경색 변경시 트랜지션 효과를 적용합니다. */
  font-size: 19px; /* 글꼴 크기를 설정합니다. */
  color: #333; /* 글꼴 색상을 어두운 회색으로 설정합니다. */
  border-bottom: 1px solid #eee; /* 아래쪽에 경계선을 추가합니다. */
}

.dataset-list li:hover,
.dataset-list li.selected {
  background-color: #e3f2fd; /* 호버 또는 선택된 상태에서 배경색을 변경합니다. */
}

.dataset-description {
  
  padding: 20px; /* 설명 부분에 여백을 추가합니다. */
  flex-grow: 1; /* 남은 공간을 모두 채웁니다. */
  background-color: #fafafa; /* 배경색을 연한 회색으로 설정합니다. */
  border-radius: 0 12px 12px 0; /* 오른쪽 모서리를 둥글게 처리합니다. */
}

.dataset-description p
{
  font-size: 22px; /* 글꼴 크기 */
  color: #666; /* 글꼴 색상 */
  margin-bottom: 10px; /* 아래쪽 마진 추가 */
  line-height: 1.4; /* 줄 간격 설정 */

}
.dataset-description h3 {
  
  margin-top: 0; /* 위쪽 마진 제거 */
  font-size: 25px; /* 글꼴 크기 */
  color: #333; /* 글꼴 색상 */
}

@media (max-width: 768px) {
  .dataset-selector-container {
    flex-direction: column; /* 화면 크기가 작을 때 세로로 정렬합니다. */
  }

  .dataset-list ul {
    width: auto; /* 너비를 자동으로 조절합니다. */
    border-right: none; /* 오른쪽 경계선을 제거합니다. */
  }

  .dataset-list li {
    border-bottom: none; /* 아래쪽 경계선을 제거합니다. */
  }
}

</style>
