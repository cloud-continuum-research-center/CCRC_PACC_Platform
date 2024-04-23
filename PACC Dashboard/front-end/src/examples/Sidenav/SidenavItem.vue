<script setup>
import { computed } from "vue";
import { useStore } from "vuex";

const store = useStore();
const isRTL = computed(() => store.state.isRTL);
const sidebarMinimize = () => store.commit("sidebarMinimize");

const minimizeSidebar = () => {
  if (window.innerWidth < 1200) {
    sidebarMinimize();
  }
};

defineProps({
  to: {
    type: String,
    required: true,
  },
  navText: {
    type: String,
    required: true,
  },
});
</script>
<template>
  <router-link :to="to" class="nav-link" @click="minimizeSidebar">
    <div
      class="icon icon-shape icon-sm text-center d-flex align-items-center justify-content-center"
    >
      <slot name="icon"></slot>
    </div>
    <span class="nav-link-text" :class="isRTL ? ' me-1' : 'ms-1'">{{
      navText
    }}</span>
  </router-link>
</template>


<style scoped>
.nav-link {
  padding: 0.5rem 1rem;
  font-size: 1.5rem; /* 폰트 크기를 조금 더 크게 조정 */
  color: #5e6777; /* 세련된 짙은 회색으로 변경 */
  font-weight: 700; /* 글자 두껍게 */
  letter-spacing: 0.05em; /* 글자 간격 넓게 */
  border-radius: 0.375rem;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1); /* 텍스트에 부드러운 그림자 추가 */
}

.nav-link span {
  font-size: 1.2rem; /* 폰트 크기를 조금 더 크게 조정 */
}

.nav-link:hover {
  color: #344675; /* 호버 시 색상 변경 */
  background-color: #e3f2fd; /* 배경색도 약간 변경하여 피드백 강화 */
  transform: translateY(-2px); /* 약간 위로 이동 */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); /* 그림자 추가하여 더 돋보이게 */
}

</style>
