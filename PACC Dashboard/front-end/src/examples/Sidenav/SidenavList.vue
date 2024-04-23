<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useStore } from "vuex";

import SidenavItem from "./SidenavItem.vue";

const store = useStore();
const isRTL = computed(() => store.state.isRTL);

const getRoute = () => {
  const route = useRoute();
  const routeArr = route.path.split("/");
  return routeArr[1];
};
</script>
<template>
  <div
    class="collapse navbar-collapse w-auto h-auto h-100"
    id="sidenav-collapse-main"
  >
    <ul class="navbar-nav">
      <li class="nav-item">
        <sidenav-item
          to="/dashboard-default"
          :class="getRoute() === 'dashboard-default' ? 'active' : ''"
          :navText="isRTL ? 'لوحة القيادة' : '대시보드'"
        >
          <template v-slot:icon>
            <i class="ni ni-tv-2 text-primary text-sm opacity-10"></i>
          </template>
        </sidenav-item>
      </li>

      <li class="nav-item">
        <sidenav-item
          to="/tables"
          :class="getRoute() === 'tables' ? 'active' : ''"
          :navText="isRTL ? 'الجداول' : '학습 생성'"
        >
          <template v-slot:icon>
            <i
              class="ni ni-calendar-grid-58 text-warning text-sm opacity-10"
            ></i>
          </template>
        </sidenav-item>
      </li>

       <li class="nav-item">
        <sidenav-item
          to="/monitoring"
          :class="getRoute()"
          :navText="isRTL ? 'الجداول' : '모니터링 시스템'"
        >
           <template v-slot:icon>
      <!-- 아이콘 이미지를 추가합니다. -->
      <img src="@/assets/img/monitoring.png" alt="Monitoring Icon" class="icon-img">
    </template>
        </sidenav-item>
      </li>


    </ul>
  </div>
</template>

<style scoped>
.navbar-nav {
  padding: 0;
}
.nav-item {
  font-size: 1.875rem;
  padding: 0;
}
</style>