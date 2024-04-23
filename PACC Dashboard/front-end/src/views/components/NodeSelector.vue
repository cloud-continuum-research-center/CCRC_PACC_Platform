<template>
  <div class="node-selector-container">
    <!-- Header above the entire container -->
    <div class="node-header">
      <h2>학습 노드 선택</h2>
    </div>
    <!-- Main content area for node selection -->
    <div class="node-content">
      <!-- Node list on the far left -->
      <div class="node-list">
        <ul>
          <li
  v-for="node in nodes"
  :key="node.id"
  @click="toggleNodeSelection(node)"
  :class="{ selected: isNodeSelected(node), unselectable: node.status !== 0 }"
>
  {{ node.name }}
</li>

        </ul>
      </div>

      <div class="node-description" v-if="selectedNode">
        <h3>{{ selectedNode.name }} 설명</h3>
        <!-- Display additional node details -->
        <div class="node-details">
          <p>CPU 코어 갯수: {{ selectedNode.cpu_core_count }}</p>
          <p>총 메모리 크기: {{ selectedNode.total_memory_mb }} MB</p>
          <p>총 디스크 크기: {{ selectedNode.total_disk_mb }} MB</p>
         <p>
    <span class="status-label">상태: {{ nodeStatusDescription(selectedNode.status) }}</span> 
  </p>
          <p v-if="selectedNode.instance">
            인스턴스: {{ selectedNode.instance }}
          </p>
          <p v-if="selectedNode.gpu_info">
            GPU 정보: {{ selectedNode.gpu_info }}
          </p>

          </div>
      </div>
      <div class="node-description" v-else>
        <h3>학습 노드를 선택해주세요.</h3>
      </div>

      <!-- List of selected nodes on the far right -->
      <div class="selected-nodes">
        <h3>{{ sortedSelectedNodes.length > 0 ? '선택된 노드' : '선택된 노드가 없습니다.' }}</h3>
        <ul v-if="sortedSelectedNodes.length > 0">
          <li v-for="node in sortedSelectedNodes" :key="node.id">
            {{ node.name }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, computed, onMounted } from "vue";
import { useStore } from "vuex";

const store = useStore();

const nodes = computed(() => {
  const unsortedNodes = store.getters.userNodes || [];
  return unsortedNodes.sort((a, b) => a.name.localeCompare(b.name)); // Sort alphabetically by name
});

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [], // Provide a default empty array
  },
});

const isNodeSelected = (node) => {
  return props.modelValue.some(
    (selectedNode) => selectedNode.node_id === node.node_id,
  );
};

const emit = defineEmits(["update:modelValue"]);

onMounted(async () => {
  await store.dispatch("fetchNodes"); // 노드 정보 가져와서 마운트하기.
});

const selectedNode = ref(null);

const toggleNodeSelection = (node) => {
  if (node.status !== 0) {
    // If the node is not in a waiting state, display its details without selecting it
    selectedNode.value = node;
    console.error("Node is not in a waiting state and cannot be selected.");
    return; // Exit early without changing the selection
  }

  const isSelected = props.modelValue.some(
    (selectedNode) => selectedNode.node_id === node.node_id,
  );
  let newSelectedNodes = isSelected
    ? props.modelValue.filter(
        (selectedNode) => selectedNode.node_id !== node.node_id,
      )
    : [...props.modelValue, node];

  emit("update:modelValue", newSelectedNodes);

  // Set or unset the selectedNode for displaying details
  selectedNode.value = isSelected ? null : node;
};

const nodeStatusDescription = (status) => {
  const statusMap = {
    0: "대기중",
    1: "학습중",
    2: "학습완료",
  };
  return statusMap[status] || "Unknown status";
};

const sortedSelectedNodes = computed(() => {
  if (!Array.isArray(props.modelValue)) {
    return []; // Return an empty array if props.modelValue is not an array
  }
  // Proceed with sorting if props.modelValue is an array
  return [...props.modelValue].sort((a, b) => a.name.localeCompare(b.name));
});
</script>

<style scoped>
.node-list li:not(.unselectable):hover {
  background-color: #e3f2fd;
}
.status-label {
  color: red; /* 빨간색 텍스트 */
}
/* 선택할 수 없는 노드의 스타일 */
.node-list li.unselectable {
  background-color: #FF7F50; /* Coral */
  color: #333;
  font-weight: bold;
  cursor: not-allowed; /* 마우스 커서 변경 */
}
.node-list li.unselectable:hover {
  background-color: #FF7F50; /* 유지될 Coral 색상 */
}
.node-description h3
{
  font-size: 30px;
  margin-bottom: 5px;
  font-weight: bold;
}
.node-selector-container {
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}
.node-description p {
  font-size: 19px; /* 폰트 사이즈를 25px에서 16px로 변경 */
  margin-bottom: 5px; /* 위아래 간격을 적절하게 조절 */
  font-weight: bold;
}

.node-header {
  padding: 15px 20px;
  background-color: #f8f8f8;
  text-align: left;
  font-size: 20px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #ddd;
}

.node-header h2 {
  margin: 0;
  font-size: 34px;
}

.node-content {
  display: flex;
  flex-wrap: wrap; /* Enables the content to wrap onto the next line as needed */
}

.node-list,
.node-description,
.selected-nodes {
  padding: 20px;
  flex-basis: 33.3333%;
  flex-grow: 1;
  border-right: 1px solid #ddd;
}

.node-list ul,
.selected-nodes ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.node-list li,
.selected-nodes li {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  transition: background-color 0.3s;
  font-size: 20px;
  color: #333;
  font-weight: bold;
}


.node-list li:hover,
.node-list li.selected,
.selected-nodes li:hover {
  background-color: #e3f2fd;
}

/* Remove border from the last element of the main content */
.selected-nodes {
  border-right: none;
}

@media (max-width: 768px) {
  .node-content {
    flex-direction: column;
  }

  .node-list,
  .node-description,
  .selected-nodes {
    border-right: none;
    border-bottom: 1px solid #ddd;
    flex-basis: auto;
  }



  .selected-nodes {
    border-bottom: none;
  }
}

</style>
