<script setup>
import { reactive, ref, watch } from 'vue'
import { request } from '../api'

const props = defineProps({
  projectId: {
    type: Number,
    default: null,
  },
})

const environments = ref([])
const error = ref('')
const form = reactive({
  name: '',
  base_url: '',
  description: '',
  variables: '{}',
  headers: '{}',
  is_default: false,
})

watch(
  () => props.projectId,
  (value) => {
    if (value) {
      loadEnvironments()
    } else {
      environments.value = []
    }
  },
  { immediate: true }
)

async function loadEnvironments() {
  if (!props.projectId) return
  error.value = ''
  try {
    environments.value = await request(`environments/?project=${props.projectId}`)
  } catch (err) {
    error.value = err.message
  }
}

function parseJson(value) {
  try {
    return value ? JSON.parse(value) : {}
  } catch (err) {
    throw new Error('请输入合法的 JSON 字符串')
  }
}

async function createEnvironment() {
  if (!props.projectId) return
  try {
    const payload = {
      project: props.projectId,
      name: form.name,
      base_url: form.base_url,
      description: form.description,
      variables: parseJson(form.variables),
      headers: parseJson(form.headers),
      is_default: form.is_default,
    }
    await request('environments/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    await loadEnvironments()
    error.value = ''
    form.name = ''
    form.base_url = ''
    form.description = ''
    form.variables = '{}'
    form.headers = '{}'
    form.is_default = false
  } catch (err) {
    error.value = err.message
  }
}
</script>

<template>
  <section class="panel">
    <header class="panel__header">
      <div class="panel__title">
        <h2>环境配置</h2>
        <p>集中维护 API 请求的基础地址、变量与头信息。</p>
      </div>
      <span v-if="projectId" class="panel__context">当前项目 ID：{{ projectId }}</span>
    </header>
    <p v-if="!projectId" class="empty">请选择一个项目查看对应环境。</p>
    <template v-else>
      <p v-if="error" class="panel__error">{{ error }}</p>
      <ul class="env-list">
        <li v-for="env in environments" :key="env.id">
          <div class="env-list__title">
            {{ env.name }}
            <span v-if="env.is_default" class="badge">默认</span>
          </div>
          <small>Base URL: {{ env.base_url || '未配置' }}</small>
          <details>
            <summary>变量与请求头</summary>
            <pre>{{ JSON.stringify(env.variables, null, 2) }}</pre>
            <pre>{{ JSON.stringify(env.headers, null, 2) }}</pre>
          </details>
        </li>
      </ul>
      <form class="form" @submit.prevent="createEnvironment">
        <h3>新增环境</h3>
        <label>
          名称
          <input v-model="form.name" placeholder="测试环境" />
        </label>
        <label>
          Base URL
          <input v-model="form.base_url" placeholder="https://api.example.com" />
        </label>
        <label>
          描述
          <textarea v-model="form.description" rows="2"></textarea>
        </label>
        <label>
          环境变量(JSON)
          <textarea v-model="form.variables" rows="3" placeholder='{"token":"abc"}'></textarea>
        </label>
        <label>
          请求头(JSON)
          <textarea v-model="form.headers" rows="3" placeholder='{"Content-Type":"application/json"}'></textarea>
        </label>
        <label class="inline">
          <input type="checkbox" v-model="form.is_default" /> 设置为默认
        </label>
        <button class="primary" type="submit">保存环境</button>
      </form>
    </template>
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
  justify-content: space-between;
  align-items: flex-start;
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
.panel__context {
  align-self: center;
  background: rgba(37, 99, 235, 0.1);
  border-radius: 999px;
  padding: 0.35rem 0.9rem;
  font-size: 0.85rem;
  color: #1d4ed8;
}
.panel__error {
  color: #b91c1c;
}
.env-list {
  display: grid;
  gap: 0.75rem;
  list-style: none;
  padding: 0;
}
.env-list li {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.75rem 1rem;
}
.env-list__title {
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.badge {
  background-color: var(--accent-color);
  color: #fff;
  font-size: 0.75rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}
details {
  margin-top: 0.5rem;
}
pre {
  background: rgba(148, 163, 184, 0.15);
  padding: 0.5rem;
  border-radius: 6px;
  overflow-x: auto;
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
.inline {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.empty {
  color: #6b7280;
}
</style>
