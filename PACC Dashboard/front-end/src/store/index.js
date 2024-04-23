import { createStore } from "vuex";
import axios from "axios";

export default createStore({
  state: {
    hideConfigButton: false,
    isPinned: false,
    showConfig: false,
    sidebarType: "bg-white",
    isRTL: false,
    mcolor: "",
    darkMode: false,
    isNavFixed: false,
    isAbsolute: false,
    showNavs: true,
    showSidenav: true,
    showNavbar: true,
    showFooter: true,
    showMain: true,
    layout: "default",
    authToken: sessionStorage.getItem("authToken") || null,
    userEmail: sessionStorage.getItem("userEmail") || null, // 변경: 초기 상태 설정
    models: [],
    datasets: [],
    projects: [], // Add a projects array to your state
    nodes: [], // State property for nodes
    nodesData: {},
    maxHistoricalEntries: 20,
    selectedProjectNodeNames: [],
    projectsInfo: {},
    selectedProjectId: null,
    monitoringData : {}
  },
  mutations: {
    toggleConfigurator(state) {
      state.showConfig = !state.showConfig;
    },
    sidebarMinimize(state) {
      let sidenav_show = document.querySelector("#app");
      if (state.isPinned) {
        sidenav_show.classList.add("g-sidenav-hidden");
        sidenav_show.classList.remove("g-sidenav-pinned");
        state.isPinned = false;
      } else {
        sidenav_show.classList.add("g-sidenav-pinned");
        sidenav_show.classList.remove("g-sidenav-hidden");
        state.isPinned = true;
      }
    },
    sidebarType(state, payload) {
      state.sidebarType = payload;
    },
    navbarFixed(state) {
      if (state.isNavFixed === false) {
        state.isNavFixed = true;
      } else {
        state.isNavFixed = false;
      }
    },
    setAuthToken(state, token) {
      state.authToken = token;
      sessionStorage.setItem("authToken", token);
    },
    setUserEmail(state, email) {
      state.userEmail = email;
      sessionStorage.setItem("userEmail", email); // 변경: 이메일 세션 스토리지에 저장
    },
    clearAuthToken(state) {
      state.authToken = null;
      state.userEmail = null;
      sessionStorage.removeItem("authToken");
      sessionStorage.removeItem("userEmail"); // 변경: 이메일 세션 스토리지에서 삭제
    },
    // 백엔드에서 모델, 데이터셋 자료 받아옴
    setModels(state, models) {
      state.models = models;
    },
    setDatasets(state, datasets) {
      state.datasets = datasets;
    },
    // 프로젝트 db에서 사용자 프로젝트 가져옴
    setProjects(state, projects) {
      state.projects = projects;
    },
    getMonitoringData(state, monitoringData) {
      state.monitoringData = monitoringData;
    },
    setNodes(state, nodes) {
      state.nodes = nodes; // 노드 데이터들 가져옴.
    },
    setRealTimeData(state, { nodeName, key, value }) {
      if (!state.nodesData[nodeName]) {
        state.nodesData[nodeName] = { realTime: {}, historical: {} };
      }
      state.nodesData[nodeName].realTime[key] = value;
    },

    addHistoricalDataEntry(state, { nodeName, key, value }) {
      try {
        if (!state.nodesData[nodeName]) {
          state.nodesData[nodeName] = { realTime: {}, historical: {} };
        }
        let dataArray = state.nodesData[nodeName].historical[key] || [];
        if (!Array.isArray(dataArray)) {
          dataArray = []; // If the existing data is not an array, initialize it as a new array
        }

        dataArray.push(value); // add new value to array
        console.log(`dddd: ${key} =`, [...dataArray]); // 데이터 복사본 로깅 // logging array status

        if (dataArray.length > state.maxHistoricalEntries) {
          dataArray.shift(); // remove oldest data
        }

        console.log(`ffff: ${key} =`, [...dataArray]); // 데이터 복사본 로깅 // Logging final array status
        state.nodesData[nodeName].historical[key] = dataArray;
      } catch (error) {
        console.error("Error in addHistoricalDataEntry mutation:", error);
      }
    },
    setSelectedProjectNodeNames(state, nodeNames) {
      state.selectedProjectNodeNames = nodeNames;
    },
    setProjectInfo(state, project) {
      // Directly set or update a single project by ID
      state.projectsInfo[project.id] = project;
    },
    setSelectedProjectId(state, projectId) {   // 선택된 노드 정보 저장
      state.selectedProjectId = projectId;
    }
  },
  actions: {
    toggleSidebarColor({ commit }, payload) {
      commit("sidebarType", payload);
    },
    signin({ commit }, credentials) {
      return new Promise((resolve, reject) => {
        axios
          .post("http://ec2-3-36-137-217.ap-northeast-2.compute.amazonaws.com:5000/api/signin", credentials)
          .then((response) => {
            commit("setAuthToken", response.data.access_token);
            commit("setUserEmail", response.data.email); // 이메일 저장
            resolve(); // Resolve the promise indicating success
          })
          .catch((error) => {
            console.error("Signin Error:", error);
            reject(error); // Reject the promise indicating failure
          });
      });
    },
    logout({ commit }) {
      commit("clearAuthToken");
    },
    async fetchModels({ commit }) {
      try {
        const response = await axios.get(
          "http://ec2-3-36-137-217.ap-northeast-2.compute.amazonaws.com:5000/api/data/models",
        );
        commit("setModels", response.data);
      } catch (error) {
        console.error("Error fetching models:", error);
      }
    },
    async fetchDatasets({ commit }) {
      try {
        const response = await axios.get(
          "http://ec2-3-36-137-217.ap-northeast-2.compute.amazonaws.com:5000/api/data/datasets",
        );
        commit("setDatasets", response.data);
      } catch (error) {
        console.error("Error fetching datasets:", error);
      }
    },
    fetchProjects({ commit, state }) {
      axios
        .post(
          "http://ec2-3-36-137-217.ap-northeast-2.compute.amazonaws.com:5000/api/data/projects",
          {
            email: state.userEmail, // send the stored email
          },
          {
            headers: {
              Authorization: `Bearer ${state.authToken}`, // send the stored authToken
            },
          },
        )
        .then((response) => {
          console.log("Fetched Projects:", response.data); // 로그를 추가하여 가져온 프로젝트 정보 출력
          commit("setProjects", response.data); // commit the projects to the state
        })
        .catch((error) => {
          console.error("Error fetching projects:", error);
        });
    },
    async fetchNodes({ commit }) {
      try {
        const response = await axios.get(
          "http://ec2-3-36-137-217.ap-northeast-2.compute.amazonaws.com:5000/api/data/nodes",
        );
        commit("setNodes", response.data); // Commit the node data to the state
      } catch (error) {
        console.error("Error fetching nodes:", error);
      }
    },
    async fetchData({ commit }) {
      // 백엔드에서 노들의 모니터링 정보 요청
      try {
        const response = await axios.get(
          "http://ec2-3-36-137-217.ap-northeast-2.compute.amazonaws.com:5000/api/data/nodemonitoring",
        )
        commit("getMonitoringData", response.data); // commit the projects to the state
      
      } catch (error) {
        console.error("Failed to fetch node data:", error);
      }
    },
    updateSelectedProjectNodeNames({ commit }, nodeNames) {
      commit("setSelectedProjectNodeNames", nodeNames);
    },
    fetchProjectInfoById({ commit, state }, projectId) {
      if (state.authToken && state.userEmail) { 
        axios.get(`http://ec2-3-36-137-217.ap-northeast-2.compute.amazonaws.com:5000/api/projects/${projectId}`, {
          headers: {
            Authorization: `Bearer ${state.authToken}`
          }
        })
        .then(response => {
          
          console.log("Project Info 111:", response.data); // 프로젝트 정보 콘솔에 출력
          commit('setProjectInfo', response.data);
        })
        .catch(error => {
          console.error(`Error fetching project ${projectId}:`, error);
        });
      }
    },
    
    updateSelectedProjectId({ commit }, projectId) {           //선택된 프로젝트 Id 저장 하는 함수
      commit('setSelectedProjectId', projectId);
    }
  },

  getters: {
    userProjects: (state) => state.projects, // Add a getter for the projects
    userNodes: (state) => state.nodes,
    getNodeData: (state) => (nodeName) =>
      state.nodesData[nodeName] || { realTime: {}, historical: {} },
    getNodeMemory: (state) => (nodeName) => {
      const node = state.nodesData[nodeName] || {
        realTime: {},
        historical: {},
      };
      return node.realTime.memoryFree || null; // 'memoryFree' 키를 사용하여 메모리 데이터에 접근
    },
    getNodeDisk: (state) => (nodeName) => {
      const node = state.nodesData[nodeName] || {
        realTime: {},
        historical: {},
      };
      return node.realTime.diskFree || null; // 'diskFre' 키를 사용하여 메모리 데이터에 접근
    },
    getNodeGpuTem: (state) => (nodeName) => {
      const node = state.nodesData[nodeName] || {
        realTime: {},
        historical: {},
      };
      return node.historical.gpuTemperature || null; // 'gpuTemperature' 키를 사용하여 메모리 데이터에 접근
    },
  },
});
