<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { request } from '../api'

const props = defineProps({
  modelValue: {
    type: Number,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue'])

const projects = ref([])
const loading = ref(false)
const error = ref('')
const form = reactive({
  name: '',
  description: '',
  owner: '',
})

const selectedId = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

async function loadProjects() {
  loading.value = true
  error.value = ''
  try {
    projects.value = await request('projects/')
    if (!selectedId.value && projects.value.length) {
      selectedId.value = projects.value[0].id
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function createProject() {
  if (!form.name) {
    error.value = '项目名称不能为空'
    return
  }
  try {
    const payload = await request('projects/', {
      method: 'POST',
      body: JSON.stringify(form),
    })
    projects.value.push(payload)
    selectedId.value = payload.id
    form.name = ''
    form.description = ''
    form.owner = ''
    error.value = ''
  } catch (err) {
    error.value = err.message
  }
}

onMounted(loadProjects)

</script>

<template>
  <section class="panel">
    <header class="panel__header">
      <div class="panel__title">
        <h2>项目管理</h2>
        <p>维护业务项目、负责人信息与基础统计。</p>
      </div>
      <button class="refresh" @click="loadProjects" :disabled="loading">刷新</button>
    </header>
    <p v-if="error" class="panel__error">{{ error }}</p>
    <ul class="project-list" v-if="projects.length">
      <li
        v-for="project in projects"
        :key="project.id"
        :class="{ active: project.id === selectedId }"
        @click="selectedId = project.id"
      >
        <div class="project-list__title">{{ project.name }}</div>
        <small>
          所有人: {{ project.owner || '未设置' }} · 接口 {{ project.interfaces || 0 }} ·
          环境 {{ project.environments || 0 }} · 用例 {{ project.cases || 0 }}
        </small>
      </li>
    </ul>
    <p v-else class="empty">暂无项目，请新建。</p>

    <form class="form" @submit.prevent="createProject">
      <label>
        名称
        <input v-model="form.name" placeholder="演示项目" />
      </label>
      <label>
        所有人
        <input v-model="form.owner" placeholder="测试负责人" />
      </label>
      <label>
        描述
        <textarea v-model="form.description" placeholder="项目介绍" rows="2"></textarea>
      </label>
      <button class="primary" type="submit" :disabled="loading">新建项目</button>
    </form>
  </section>
</template>

<style scoped>
.panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}
.panel__title h2 {
  margin: 0;
  font-size: 1.35rem;
}
.panel__title p {
  margin: 0.25rem 0 0;
  color: #6b7280;
  font-size: 0.9rem;
}
.panel__error {
  color: #b91c1c;
}
.project-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.5rem;
}
.project-list li {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}
.project-list li.active {
  border-color: var(--accent-color);
  background-color: rgba(59, 130, 246, 0.1);
}
.project-list__title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}
.form {
  display: grid;
  gap: 0.75rem;
}
label {
  display: grid;
  gap: 0.25rem;
  font-size: 0.875rem;
}
.refresh {
  align-self: flex-start;
  background: rgba(37, 99, 235, 0.08);
  color: #1d4ed8;
  border: 1px solid rgba(37, 99, 235, 0.25);
  border-radius: 999px;
  padding: 0.45rem 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}
.refresh:hover:not(:disabled) {
  border-color: rgba(37, 99, 235, 0.55);
  background: rgba(37, 99, 235, 0.12);
}
.refresh:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.empty {
  color: #6b7280;
}
</style>
