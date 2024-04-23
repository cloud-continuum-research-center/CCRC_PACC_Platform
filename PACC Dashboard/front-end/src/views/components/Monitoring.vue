<template>
  <div class="monitoring">
    <!-- 화면에 보여질 내용이 없으므로 빈 div를 사용합니다. -->
  </div>
</template>



<script>
import { useRouter } from 'vue-router';

export default {
  name: 'Monitoring',
  created() {
    // 컴포넌트가 생성되자마자 특정 URL로 새 탭에서 열립니다.
    window.open("http://13.124.158.135:3000/d/rYdddlPWk/metic-monitoring?orgId=1&refresh=1m", "_blank");
    
const router = useRouter();
    setTimeout(() => {
      router.push({ name: 'Dashboard' });
    }, 100);
  }
}
</script>

<style>
/* 스타일은 필요에 따라 추가하십시오 */
</style>
