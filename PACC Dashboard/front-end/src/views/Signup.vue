<script setup>
import { onBeforeUnmount, onBeforeMount } from "vue";
import { ref } from "vue";
import { useStore } from "vuex";
import axios from "axios";
import { useRouter } from "vue-router";

import Navbar from "@/examples/PageLayout/Navbar.vue";
import AppFooter from "@/examples/PageLayout/Footer.vue";
import ArgonInput from "@/components/ArgonInput.vue";
import ArgonButton from "@/components/ArgonButton.vue";
const body = document.getElementsByTagName("body")[0];

const router = useRouter();

const name = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");

const submitForm = async () => {
  if (password.value !== confirmPassword.value) {
    alert("비밀번호가 일치하지 않습니다.");
    return; // 비밀번호가 일치하지 않으면 여기서 처리를 중단합니다.
  }
  const formData = {
    name: name.value,
    email: email.value,
    password: password.value,
  };

  try {
    const response = await axios.post(
      "http://ec2-3-36-137-217.ap-northeast-2.compute.amazonaws.com:5000/api/signup",
      formData,
    );
    console.log(response.data);
    // 회원 가입 성공 메시지
    alert(
      "회원 가입에 성공하셨습니다. 확인을 누르시면 로그인 화면으로 이동합니다",
    );
    // 5초 후 로그인 페이지로 리디렉션
    setTimeout(() => {
      router.push("/signin");
    }, 0);
  } catch (error) {
    console.error(error);
    alert("회원 가입에 실패했습니다."); // 회원 가입 실패 메시지
  }
};

const store = useStore();
onBeforeMount(() => {
  store.state.hideConfigButton = true;
  store.state.showNavbar = false;
  store.state.showSidenav = false;
  store.state.showFooter = false;
  body.classList.remove("bg-gray-100");
});
onBeforeUnmount(() => {
  store.state.hideConfigButton = false;
  store.state.showNavbar = true;
  store.state.showSidenav = true;
  store.state.showFooter = true;
  body.classList.add("bg-gray-100");
});
</script>
<template>
  <div class="container top-0 position-sticky z-index-sticky">
    <div class="row">
      <div class="col-12">
        <navbar isBtn="bg-gradient-light" />
      </div>
    </div>
  </div>
  <main class="main-content mt-0">
    <div
      class="page-header align-items-start min-vh-50 pt-5 pb-11 m-3 border-radius-lg"
      :style="{
        backgroundImage:
          'url(' + require('@/assets/img/cloud_background.png') + ')',
        backgroundPosition: 'top',
      }"
    >
      <span class="mask bg-gradient-dark opacity-6"></span>
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-5 text-center mx-auto">
            <h1 class="text-white mb-4 mt-4">안녕하세요</h1>
            <p class="text-lead text-white">
              CCRC 연구센터 병렬학습 프레임워크 대시보드에 오신 것을 환영합니다.
              먼저 회원가입을 진행해주시길 바랍니다.
            </p>
          </div>
        </div>
      </div>
    </div>
    <div class="container">
      <div class="row mt-lg-n10 mt-md-n11 mt-n10 justify-content-center">
        <div class="col-xl-4 col-lg-5 col-md-7 mx-auto">
          <div class="card z-index-0">
            <div class="card-header text-center pt-4">
              <h5>사용자 정보를 입력해주세요</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="submitForm">
                <argon-input
                  id="name"
                  type="text"
                  placeholder="이름"
                  aria-label="Name"
                  v-model="name"
                />
                <argon-input
                  id="email"
                  type="email"
                  placeholder="이메일"
                  aria-label="Email"
                  v-model="email"
                />
                <argon-input
                  id="password"
                  type="password"
                  placeholder="비밀번호"
                  aria-label="Password"
                  v-model="password"
                />
                <argon-input
                  id="confirm_password"
                  type="password"
                  placeholder="비밀번호 확인"
                  aria-label="confirm_Password"
                  v-model="confirmPassword"
                />
                <div class="text-center">
                  <argon-button
                    type="submit"
                    fullWidth
                    color="dark"
                    variant="gradient"
                    class="my-4 mb-2"
                    >회원 가입</argon-button
                  >
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
  <app-footer />
</template>
