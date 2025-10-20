<script setup>
import { computed, ref } from 'vue'
import ProjectList from './components/ProjectList.vue'
import EnvironmentConfig from './components/EnvironmentConfig.vue'
import InterfaceConsole from './components/InterfaceConsole.vue'
import ScenarioDesigner from './components/ScenarioDesigner.vue'
import TestSuiteRunner from './components/TestSuiteRunner.vue'

const sections = [
  {
    key: 'projects',
    label: '项目工作台',
    description: '集中管理项目与协作者，快速了解业务全貌。',
    icon: '📁',
    accent: '215 100% 61%',
    requiresProject: false,
  },
  {
    key: 'environments',
    label: '环境配置',
    description: '统一维护基础地址、变量与请求头，保障接口联调一致性。',
    icon: '🌐',
    accent: '172 66% 47%',
    requiresProject: true,
  },
  {
    key: 'interfaces',
    label: '接口调试',
    description: '维护接口定义并进行请求调试，支持 Swagger 导入。',
    icon: '🧩',
    accent: '283 85% 58%',
    requiresProject: true,
  },
  {
    key: 'scenarios',
    label: '场景编排',
    description: '串联多接口形成业务场景，配置断言与变量提取。',
    icon: '🎯',
    accent: '32 96% 61%',
    requiresProject: true,
  },
  {
    key: 'suites',
    label: '测试套件',
    description: '组织场景执行与报告输出，持续保障接口质量。',
    icon: '🚀',
    accent: '346 77% 56%',
    requiresProject: true,
  },
]

const activeTab = ref('projects')
const selectedProjectId = ref(null)

const activeSection = computed(
  () => sections.find((section) => section.key === activeTab.value) ?? sections[0]
)

const subtitle = computed(() => {
  if (!selectedProjectId.value) {
    return '请选择或创建一个项目开始'
  }
  return `当前项目 ID：${selectedProjectId.value}`
})

function switchTab(section) {
  if (section.requiresProject && !selectedProjectId.value) return
  activeTab.value = section.key
}
</script>

<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="sidebar__brand">
        <span class="sidebar__logo">FA</span>
        <div class="sidebar__meta">
          <h1>Fast API Test</h1>
          <p>MeterSphere 风格的 API 测试平台</p>
        </div>
      </div>
      <ul class="sidebar__nav">
        <li v-for="section in sections" :key="section.key">
          <button
            class="sidebar__nav-item"
            :data-active="activeTab === section.key"
            :disabled="section.requiresProject && !selectedProjectId"
            :style="{ '--accent': section.accent }"
            @click="switchTab(section)"
          >
            <span class="sidebar__nav-icon" aria-hidden="true">{{ section.icon }}</span>
            <span class="sidebar__nav-text">
              <strong>{{ section.label }}</strong>
              <small>{{ section.description }}</small>
            </span>
            <span
              v-if="section.requiresProject"
              class="sidebar__nav-chip"
              :data-ready="!!selectedProjectId"
            >
              项目
            </span>
          </button>
        </li>
      </ul>
    </aside>
    <main class="workspace">
      <header class="workspace__header">
        <div>
          <p class="workspace__overline">{{ activeSection.label }}</p>
          <h2>{{ activeSection.description }}</h2>
          <p class="workspace__subtitle">{{ subtitle }}</p>
        </div>
        <div class="workspace__status">
          <div class="workspace__status-card">
            <span class="workspace__status-label">当前标签页</span>
            <span class="workspace__status-value">{{ activeSection.icon }} {{ activeSection.label }}</span>
          </div>
          <div class="workspace__status-card" :data-empty="!selectedProjectId">
            <span class="workspace__status-label">项目上下文</span>
            <span class="workspace__status-value">
              <template v-if="selectedProjectId">#{{ selectedProjectId }}</template>
              <template v-else>未选择项目</template>
            </span>
          </div>
        </div>
      </header>
      <section class="workspace__content">
        <ProjectList v-if="activeTab === 'projects'" v-model="selectedProjectId" />
        <EnvironmentConfig v-else-if="activeTab === 'environments'" :project-id="selectedProjectId" />
        <InterfaceConsole v-else-if="activeTab === 'interfaces'" :project-id="selectedProjectId" />
        <ScenarioDesigner v-else-if="activeTab === 'scenarios'" :project-id="selectedProjectId" />
        <TestSuiteRunner v-else-if="activeTab === 'suites'" :project-id="selectedProjectId" />
      </section>
    </main>
  </div>
</template>

<style scoped>
.shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 320px 1fr;
  background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.18), transparent 55%),
    radial-gradient(circle at bottom left, rgba(16, 185, 129, 0.15), transparent 45%),
    #eef2ff;
  color: #0f172a;
}

.sidebar {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 2.5rem 2rem;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(18px);
  border-right: 1px solid rgba(148, 163, 184, 0.35);
}

.sidebar__brand {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.sidebar__logo {
  display: grid;
  place-items: center;
  width: 3.25rem;
  height: 3.25rem;
  border-radius: 1.25rem;
  background: linear-gradient(135deg, #1d4ed8, #9333ea);
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.sidebar__meta h1 {
  margin: 0;
  font-size: 1.35rem;
}

.sidebar__meta p {
  margin: 0.35rem 0 0;
  color: #475569;
  font-size: 0.875rem;
}

.sidebar__nav {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.75rem;
}

.sidebar__nav-item {
  width: 100%;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 1.25rem;
  padding: 1rem 1.25rem;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1rem;
  align-items: center;
  background: rgba(255, 255, 255, 0.65);
  color: inherit;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.sidebar__nav-item[data-active='true'] {
  border-color: hsl(var(--accent));
  box-shadow: 0 16px 32px rgba(15, 23, 42, 0.12);
  transform: translateY(-2px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(226, 232, 240, 0.75));
}

.sidebar__nav-item:hover:not(:disabled) {
  border-color: hsl(var(--accent));
  transform: translateY(-1px);
}

.sidebar__nav-item:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.sidebar__nav-icon {
  font-size: 1.35rem;
}

.sidebar__nav-text {
  display: grid;
  gap: 0.35rem;
  text-align: left;
}

.sidebar__nav-text strong {
  font-size: 1rem;
}

.sidebar__nav-text small {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.3;
}

.sidebar__nav-chip {
  justify-self: end;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.6);
  background: rgba(241, 245, 249, 0.8);
  color: #475569;
  transition: all 0.2s ease;
}

.sidebar__nav-chip[data-ready='true'] {
  border-color: hsl(var(--accent));
  color: hsl(var(--accent));
  background: rgba(148, 163, 184, 0.1);
}

.workspace {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 2.25rem;
  padding: 3rem 3.5rem;
}

.workspace__header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 1.5rem;
}

.workspace__overline {
  margin: 0;
  font-size: 0.875rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #475569;
}

.workspace__header h2 {
  margin: 0.35rem 0 0.5rem;
  font-size: 1.75rem;
  max-width: 36rem;
}

.workspace__subtitle {
  margin: 0;
  color: #5f6c80;
  font-size: 0.95rem;
}

.workspace__status {
  display: flex;
  gap: 1rem;
  align-items: stretch;
}

.workspace__status-card {
  min-width: 11rem;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 1rem;
  padding: 0.85rem 1.2rem;
  display: grid;
  gap: 0.35rem;
  transition: border-color 0.2s ease;
}

.workspace__status-card[data-empty='true'] {
  border-style: dashed;
}

.workspace__status-label {
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  color: #64748b;
  text-transform: uppercase;
}

.workspace__status-value {
  font-size: 1.05rem;
  font-weight: 600;
}

.workspace__content {
  display: grid;
  align-items: start;
}

@media (max-width: 1080px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: sticky;
    top: 0;
    z-index: 10;
    flex-direction: column;
    gap: 1.5rem;
    border-right: none;
    border-bottom: 1px solid rgba(148, 163, 184, 0.35);
  }

  .workspace {
    padding: 2.5rem 1.75rem 3rem;
  }
}
</style>
