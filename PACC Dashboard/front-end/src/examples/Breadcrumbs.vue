<script setup>
import { computed } from "vue";
import { useStore } from "vuex";

const store = useStore();
const isRTL = computed(() => store.state.isRTL);
const isNavFixed = computed(() => store.state.isNavFixed);

defineProps({
  currentPage: {
    type: String,
    default: "",
  },
  currentDirectory: {
    type: String,
    default: "",
  },
});
</script>
<template>
  <nav aria-label="breadcrumb">
    <ol
      class="px-0 pt-1 pb-0 mb-0 bg-transparent breadcrumb"
      :class="`${isRTL ? '' : ' me-sm-6'} ${
        isNavFixed ? 'text-dark' : 'text-white'
      }`"
    >
      <li class="text-sm breadcrumb-item">
        <a
          v-if="isRTL"
          class="opacity-5 ps-2"
          href="#"
          :class="isNavFixed ? 'text-dark' : 'text-white'"
          >لوحات القيادة</a
        >
     
      </li>
      
    </ol>
    <h6
      class="mb-0 font-weight-bolder page-title"
      :class="isNavFixed ? 'text-dark' : 'text-white'"
    >
      {{ "Parallel Anything in Cloud Continuum" }}
    </h6>
  </nav>
</template>


<style scoped>
/* 기존 스타일 */
.text-sm {
  font-size: 0.875rem;
}

/* 새 페이지 타이틀 스타일 */
.page-title {
  font-size: 28px; /* 글자 크기를 28px로 늘림 */
  font-weight: 700; /* 폰트 가중치를 더 두껍게 */
  color: #ffffff; /* 글자 색상을 하얀색으로 설정 */
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); /* 텍스트에 그림자 추가 */
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* 폰트 패밀리 변경 */
  margin-left: 500px; /* 오른쪽으로 50픽셀 이동 */
}

</style>
