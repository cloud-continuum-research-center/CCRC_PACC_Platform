<template>
  <div class="disk-gauge">
    <GaugeComponent
      :total-size="totalSize"
      :remaining-size="remainingSize"
      :node-name="nodeName"
    />
    <!-- nodeName is passed to GaugeComponent to potentially display which node this gauge represents -->
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import GaugeComponent from "./GaugeComponent.vue";

const props = defineProps({
  totalSize: Number, // Total size of the disk
  remainingSize: Number, // Remaining disk space
  nodeName: String, // Node name to possibly use in the gauge display or logging
});

onMounted(() => {
  console.log("Props in DiskGaugeComponent", props);
});
</script>
