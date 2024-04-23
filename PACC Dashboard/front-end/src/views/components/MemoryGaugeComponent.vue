<template>
  <div class="memory-gauge">
    <GaugeComponent
      :total-size="totalSize"
      :remaining-size="remainingSize"
      :node-name="nodeName"
    />
    <!-- Ensure nodeName is a defined prop on GaugeComponent -->
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import GaugeComponent from "./GaugeComponent.vue";

const props = defineProps({
  totalSize: Number,
  remainingSize: Number,
  nodeName: String,
});

onMounted(() => {
  console.log("Props in MemoryGaugeComponent", props);
});
</script>
