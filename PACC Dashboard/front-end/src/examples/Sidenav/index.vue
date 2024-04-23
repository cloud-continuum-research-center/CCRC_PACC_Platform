<script setup>
import { computed } from "vue";
import { useStore } from "vuex";
import SidenavList from "./SidenavList.vue";
import logo from "@/assets/img/logo-ct-dark.png";
import logoWhite from "@/assets/img/logo-ct.png";

// 위에 로고 경로 수정 하면 메인 화면 로고 변경됨.

const store = useStore();
const isRTL = computed(() => store.state.isRTL);
const layout = computed(() => store.state.layout);
const sidebarType = computed(() => store.state.sidebarType);
const darkMode = computed(() => store.state.darkMode);
</script>
<template>
  <div
    v-show="layout === 'default'"
    class="min-height-300 position-absolute w-100"
    :class="`${darkMode ? 'bg-transparent' : 'bg-success'}`"
  />

  <aside
    class="my-3 overflow-auto border-0 sidenav navbar navbar-vertical navbar-expand-xs border-radius-xl"
    :class="`${isRTL ? 'me-3 rotate-caret fixed-end' : 'fixed-start ms-3'}    
      ${
        layout === 'landing' ? 'bg-transparent shadow-none' : ' '
      } ${sidebarType}`"
    id="sidenav-main"
  >
    <div class="sidenav-header">
      <i
        class="top-0 p-3 cursor-pointer fas fa-times text-secondary opacity-5 position-absolute end-0 d-none d-xl-none"
        aria-hidden="true"
        id="iconSidenav"
      ></i>

      <span class="ms-2 font-weight-bold me-2">PACC Platform</span>
      <router-link class="m-0 navbar-brand" to="/dashboard-default">
        <img
          :src="darkMode || sidebarType === 'bg-default' ? logoWhite : logo"
          class="navbar-brand-img h-100"
          alt="main_logo"
        />
      </router-link>
    </div>

    <hr class="mt-0 horizontal dark" />

    <sidenav-list />
  </aside>
</template>

<style scoped>


.top-0
{
  border: none; /* 테두리 없애기 */
  border-radius: 0; /* 테두리 모서리를 직사각으로 만듦 */
  margin: 0; /* 여백 없애기 */
}

.ms-2
{
  border: none; /* 테두리 없애기 */
  border-radius: 0; /* 테두리 모서리를 직사각으로 만듦 */
  margin-left: 20px !important; /* 왼쪽 여백을 0으로 설정 */
}

.my-3 {
  border: none !important; /* 테두리 없애기 */
  border-radius: 0 !important; /* 테두리 모서리를 직사각으로 만듦 */
  margin-left: 0 !important; /* 왼쪽 여백을 0으로 설정 */
  margin-top: 0 !important; /* 위쪽 여백을 3rem으로 설정 */
}

.sidenav {
  margin: 0; /* 여백 없애기 */
  overflow-y: auto; /* 내용이 넘칠 경우 스크롤 가능 */
  border: none; /* border-0 스타일 적용 */
  border-radius: 0; /* 테두리 모서리를 직사각으로 만듦 */
  width: 250px; /* 너비 설정 */
  background-color: #f8f9fa; /* 배경색 설정 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 그림자 추가 */
}



/* Span 태그 스타일 */
span.font-weight-bold {
  color: #344675; /* 폰트 색상 */
  font-size: 23px; /* 폰트 크기 */
  font-weight: bold; /* 폰트 두께 */
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1); /* 텍스트에 그림자 추가 */
  letter-spacing: 0.05em; /* 문자 간격 조정 */
  text-transform: uppercase; /* 모든 문자를 대문자로 변환 */
  margin-left: 20px; /* 오른쪽 여백 추가 */
}

/* Router-link 태그 스타일 */
.router-link {
  display: flex; /* Flexbox를 사용하여 내용을 중앙 정렬 */
  align-items: center; /* 세로 방향 중앙 정렬 */
  padding: 0.5rem 0; /* 상하 패딩 */
}

.navbar-brand-img {
  width: 160px !important; /* 너비를 150px로 설정 */
  height: 150px !important; /* 높이를 150px로 설정 */
  position: absolute; /* 절대 위치 설정 */
  top: 40px; /* 상단에서 20px 떨어진 위치 */
  left: 43px; /* 좌측에서 20px 떨어진 위치 */
  z-index: 10; /* 다른 요소들 위에 오도록 z-index 설정 */
  transition: transform 0.3s ease; /* 마우스 오버 시 애니메이션 */
}

.navbar-brand-img:hover {
  transform: scale(1.2); /* 마우스 오버 시 이미지 확대 */
}

/* min-height-300 position-absolute w-100 스타일 */
.min-height-300 {
  
  min-height: 300px; /* 최소 높이 설정 */
  position: absolute; /* 절대 위치 */
  width: 100%; /* 너비를 100%로 설정 */
  background-image: linear-gradient(to right, #000428, #004e92); /* 우주 같은 그라디언트 배경: 어두운 파란색에서 검정색으로 */
  background-size: cover; /* 배경 이미지 크기 조절 */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); /* 박스 그림자 추가: 좀 더 진한 그림자로 변경 */
  border-radius: 8px; /* 모서리 둥글게 처리 */
  opacity: 0.95; /* 약간의 투명도 */
  z-index: -1; /* z-index로 레이어 순서 조정 */
  background-attachment: fixed; /* 배경 고정: 스크롤 시 배경이 고정되도록 설정 */
  color: #ffffff; /* 텍스트 색상 */
  overflow: hidden; /* 내용이 넘칠 경우 숨김 */
  border: none !important; /* 테두리 없애기 */
  border-radius: 0 !important; /* 테두리 모서리를 직사각으로 만듦 */
  margin-left: 0 !important; /* 왼쪽 여백을 0으로 설정 */
  margin-top: 0 !important; /* 위쪽 여백을 3rem으로 설정 */
}

/* 사이드바 스타일링 */
.sidenav {
  margin: 0; /* 여백 없애기 */
  overflow-y: auto; /* 내용이 넘칠 경우 스크롤 가능 */
  border: none; /* border-0 스타일 적용 */
  border-radius: 1rem; /* border-radius-xl 스타일 적용 */
  width: 250px; /* 너비 설정 */
  background-color: #f8f9fa; /* 배경색 설정 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 그림자 추가 */
}


/* 배경 스타일링 */
.min-height-300 {
  min-height: 300px; /* 최소 높이 설정 */
  position: absolute; /* 절대 위치 설정 */
  width: 100%; /* 너비를 100%로 설정 */
  background-image: linear-gradient(to right, #000428, #004e92); /* 그라디언트 배경 */
  z-index: -1; /* 요소의 스택 순서 설정 */
  top: 0; /* 상단에 위치 */
  left: 0; /* 왼쪽에 위치 */
}

</style>