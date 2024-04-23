<template>
  <div class="hyperparameter-settings">
    <h2>하이퍼 파라미터 설정</h2>
    <div class="hyperparameters">
      <div class="form-group">
        <label for="learningRate">학습률</label>
        <input
          type="text"
          id="learningRate"
          v-model="localHyperparameters.learningRate"
          @input="handleLearningRateInput($event.target.value)"
        />
      </div>
      <div class="form-group">
        <label for="batchSize">모델 학습 배치 사이즈</label>
        <input
          type="text"
          id="batchSize"
          v-model.number="localHyperparameters.batchSize"
          @input="emitUpdate"
          min="1"
          step="1"
        />
      </div>

      <div class="form-group">
        <label for="epochs">모델 학습 횟수</label>
        <input
          type="text"
          id="epochs"
          v-model.number="localHyperparameters.epochs"
          @input="emitUpdate"
          min="1"
          step="1"
        />
      </div>

      <div class="form-group">
        <label for="optimizer">최적화 함수</label>
        <select id="optimizer" v-model.number="localHyperparameters.optimizer">
          <option value="1">Adam</option>
          <option value="2">SGD</option>
        </select>
      </div>
      <div class="form-group">
        <label for="lossFunction">손실 함수</label>
        <select
          id="lossFunction"
          v-model.number="localHyperparameters.lossFunction"
        >
          <option value="1">Crossentropy</option>
          <option value="2">Mean Squared Error</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from "vue";

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      learningRate: "", // Default as number
      batchSize: "", // Default as number
      epochs: "", // Default as number
      optimizer: "",
      lossFunction: "",
    }),
  },
});

const emit = defineEmits(["update:modelValue"]);

const localHyperparameters = ref({ ...props.modelValue });

const handleLearningRateInput = (value) => {
  // 입력값이 유효한지 검사하는 정규식을 수정합니다.
  if (value === "" || /^0(\.\d+)?$|^\.\d+$/.test(value)) {
    localHyperparameters.value.learningRate = value;
    emitUpdate();
  }
};

watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      localHyperparameters.value = { ...newValue };
    }
  },
  { deep: true },
);

const emitUpdate = () => {
  // `parseFloat` 또는 `parseInt`를 사용하여 숫자로 변환
  const updatedHyperparameters = {
    learningRate: parseFloat(localHyperparameters.value.learningRate),
    batchSize: parseInt(localHyperparameters.value.batchSize),
    epochs: parseInt(localHyperparameters.value.epochs),
    optimizer: localHyperparameters.value.optimizer
      ? parseInt(localHyperparameters.value.optimizer, 10)
      : 1, // Providing default value as 1
    lossFunction: localHyperparameters.value.lossFunction
      ? parseInt(localHyperparameters.value.lossFunction, 10)
      : 1, // Providing default value as 1
  };

  emit("update:modelValue", updatedHyperparameters);
};
</script>

<style scoped>



.hyperparameter-settings {
  max-width: 100%;
  margin-top : 15px;
  margin-left : 8px;
}
.hyperparameter-settings h2 {
  font-size: 34px; /* 글꼴 크기를 설정합니다. */
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size : 20px;
}

.hyperparameters {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 20px;
}

.form-group {
  flex: 1;
  min-width: 160px; /* Adjust the minimum width as needed */
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
