<script setup>
import { computed, ref } from 'vue'
import ProjectList from './components/ProjectList.vue'
import EnvironmentConfig from './components/EnvironmentConfig.vue'
import InterfaceConsole from './components/InterfaceConsole.vue'
import ScenarioDesigner from './components/ScenarioDesigner.vue'
import TestSuiteRunner from './components/TestSuiteRunner.vue'

const tabs = [
  { key: 'projects', label: '项目', requiresProject: false },
  { key: 'environments', label: '环境', requiresProject: true },
  { key: 'interfaces', label: '接口', requiresProject: true },
  { key: 'scenarios', label: '场景', requiresProject: true },
  { key: 'suites', label: '测试套件', requiresProject: true },
]

const activeTab = ref('projects')
const selectedProjectId = ref(null)

const subtitle = computed(() => {
  if (!selectedProjectId.value) {
    return '请选择或创建一个项目开始'
  }
  return `当前项目 ID：${selectedProjectId.value}`
})

function switchTab(key, requiresProject) {
  if (requiresProject && !selectedProjectId.value) return
  activeTab.value = key
}
</script>

<template>
  <div class="app">
    <header class="app__header">
      <div>
        <h1>Fast API Test</h1>
        <p>{{ subtitle }}</p>
      </div>
    </header>
    <nav class="app__nav">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="{ active: activeTab === tab.key }"
        :disabled="tab.requiresProject && !selectedProjectId"
        @click="switchTab(tab.key, tab.requiresProject)"
      >
        {{ tab.label }}
      </button>
    </nav>
    <main class="app__main">
      <ProjectList v-if="activeTab === 'projects'" v-model="selectedProjectId" />
      <EnvironmentConfig v-else-if="activeTab === 'environments'" :project-id="selectedProjectId" />
      <InterfaceConsole v-else-if="activeTab === 'interfaces'" :project-id="selectedProjectId" />
      <ScenarioDesigner v-else-if="activeTab === 'scenarios'" :project-id="selectedProjectId" />
      <TestSuiteRunner v-else-if="activeTab === 'suites'" :project-id="selectedProjectId" />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  background: #f8fafc;
  color: #0f172a;
}
.app__header {
  display: flex;
  align-items: center;
  padding: 2rem 3rem 1rem;
}
.app__header h1 {
  margin: 0;
  font-size: 1.75rem;
}
.app__header p {
  margin: 0.25rem 0 0;
  color: #475569;
}
.app__nav {
  display: flex;
  gap: 0.75rem;
  padding: 0 3rem 1rem;
}
.app__nav button {
  border: none;
  background: transparent;
  padding: 0.5rem 1rem;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
  color: #1d4ed8;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}
.app__nav button.active {
  background: #1d4ed8;
  color: #fff;
}
.app__nav button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.app__nav button:not(.active):hover:not(:disabled) {
  border-color: rgba(29, 78, 216, 0.4);
}
.app__main {
  padding: 0 3rem 3rem;
  display: grid;
}
</style>
