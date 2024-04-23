<script setup>
import { computed } from "vue";
import { useStore } from "vuex";
import { useRouter, useRoute } from "vue-router"; // Correctly import both useRouter and useRoute
import Breadcrumbs from "../Breadcrumbs.vue";

const store = useStore();
const router = useRouter();
const route = useRoute(); // Use useRoute to access the current route information
const isRTL = computed(() => store.state.isRTL);
const userEmail = computed(() => store.state.userEmail);

const currentRouteName = computed(() => router.currentRoute.value.name);

const currentDirectory = computed(() => {
  const dir = route.path.split("/")[1];
  return dir.charAt(0).toUpperCase() + dir.slice(1);
});

const logout = () => {
  store
    .dispatch("logout")
    .then(() => {
      router.push("/signin");
    })
    .catch((error) => {
      console.error("Logout Error:", error);
    });
};
</script>
<template>
  <nav
    class="navbar navbar-main navbar-expand-lg px-0 mx-4 shadow-none border-radius-xl"
    :class="isRTL ? 'top-0 position-sticky z-index-sticky' : ''"
    v-bind="$attrs"
    id="navbarBlur"
    data-scroll="true"
  >
    <div class="px-3 py-1 container-fluid">
      <breadcrumbs
        :current-page="currentRouteName"
        :current-directory="currentDirectory"
      />

      <div
        class="mt-2 collapse navbar-collapse mt-sm-0 me-md-0 me-sm-4"
        :class="isRTL ? 'px-0' : 'me-sm-4'"
        id="navbar"
      >
        <div
          class="pe-md-3 d-flex align-items-center"
          :class="isRTL ? 'me-md-auto' : 'ms-md-auto'"
        >
          <span class="text-white">{{ userEmail }}</span>
        </div>

        <ul class="navbar-nav justify-content-end">
          <li class="nav-item d-flex align-items-center">
            <a
              class="px-0 nav-link font-weight-bold text-white"
              href="javascript:;"
              @click="logout"
            >
              <i
                class="fa fa-sign-out-alt"
                :class="isRTL ? 'ms-sm-2' : 'me-sm-2'"
              ></i>
              Log Out
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped>
/* 폰트 스타일을 위한 공통 클래스 */
.text-style {
  font-size: 16px;  /* 폰트 크기 설정 */
  font-weight: bold;  /* 폰트 가중치를 굵게 */
  color: #ffffff;  /* 폰트 색상을 흰색으로 */
}

/* 사용자 이메일과 로그아웃 링크에 적용 */
.nav-item .text-white, .nav-link {
  font-size: 16px;  /* 폰트 크기 설정 */
  font-weight: bold;  /* 폰트 가중치를 굵게 */
  color: #ffffff;  /* 폰트 색상을 흰색으로 */
}

/* 추가적으로 아이콘과 텍스트 간 간격 조절 */
.nav-item i {
  margin-right: 5px;  /* 오른쪽 마진 추가 */
}
</style>
