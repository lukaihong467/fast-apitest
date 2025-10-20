<script setup>
import { reactive, ref, watch } from 'vue'
import { request } from '../api'

const props = defineProps({
  projectId: {
    type: Number,
    default: null,
  },
})

const suites = ref([])
const reports = ref([])
const cases = ref([])
const error = ref('')
const form = reactive({
  name: '',
  description: '',
  selectedCases: [],
})

watch(
  () => props.projectId,
  (value) => {
    suites.value = []
    reports.value = []
    cases.value = []
    if (value) {
      loadSuites()
      loadReports()
      loadCases()
    }
  },
  { immediate: true }
)

async function loadSuites() {
  if (!props.projectId) return
  try {
    suites.value = await request(`test-suites/?project=${props.projectId}`)
  } catch (err) {
    error.value = err.message
  }
}

async function loadReports() {
  if (!props.projectId) return
  try {
    reports.value = await request(`test-reports/?project=${props.projectId}`)
  } catch (err) {
    error.value = err.message
  }
}

async function loadCases() {
  if (!props.projectId) return
  try {
    cases.value = await request(`interface-cases/?project=${props.projectId}`)
  } catch (err) {
    error.value = err.message
  }
}

async function createSuite() {
  if (!props.projectId) return
  if (!form.name || !form.selectedCases.length) {
    error.value = '请填写名称并选择用例'
    return
  }
  try {
    const created = await request('test-suites/', {
      method: 'POST',
      body: JSON.stringify({
        project: props.projectId,
        name: form.name,
        description: form.description,
        cases: form.selectedCases.map((id) => Number(id)),
      }),
    })
    suites.value.push(created)
    Object.assign(form, {
      name: '',
      description: '',
      selectedCases: [],
    })
    error.value = ''
  } catch (err) {
    error.value = err.message
  }
}

async function runSuite(suiteId) {
  try {
    const report = await request(`test-suites/${suiteId}/run/`, {
      method: 'POST',
      body: JSON.stringify({}),
    })
    reports.value.unshift(report)
  } catch (err) {
    error.value = err.message
  }
}
</script>

<template>
  <section class="panel">
    <header class="panel__header">
      <h2>测试套件与报告</h2>
      <span v-if="projectId">项目 ID：{{ projectId }}</span>
    </header>
    <p v-if="!projectId" class="empty">请选择项目以管理测试套件。</p>
    <template v-else>
      <p v-if="error" class="panel__error">{{ error }}</p>
      <div class="grid">
        <div>
          <h3>测试套件</h3>
          <ul class="suite-list">
            <li v-for="suite in suites" :key="suite.id">
              <div class="suite-list__header">
                <strong>{{ suite.name }}</strong>
                <button type="button" @click="runSuite(suite.id)">运行</button>
              </div>
              <small>用例数量：{{ suite.case_count }}</small>
              <p>{{ suite.description }}</p>
            </li>
          </ul>
          <form class="form" @submit.prevent="createSuite">
            <h4>创建测试套件</h4>
            <label>
              名称
              <input v-model="form.name" placeholder="冒烟套件" />
            </label>
            <label>
              描述
              <textarea v-model="form.description" rows="3"></textarea>
            </label>
            <label>
              选择用例
              <select multiple v-model="form.selectedCases">
                <option v-for="item in cases" :key="item.id" :value="item.id">
                  {{ item.interface_name }} · {{ item.name }}
                </option>
              </select>
            </label>
            <button type="submit">保存套件</button>
          </form>
        </div>
        <div>
          <h3>执行报告</h3>
          <ul class="report-list">
            <li v-for="report in reports" :key="report.id">
              <div class="report-list__header">
                <strong>{{ report.suite_name }}</strong>
                <span class="status" :class="report.status">{{ report.status }}</span>
              </div>
              <small>{{ new Date(report.created_at).toLocaleString() }}</small>
              <p>{{ report.summary }}</p>
              <pre>{{ JSON.stringify(report.details, null, 2) }}</pre>
            </li>
          </ul>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.panel__header {
  display: flex;
  justify-content: space-between;
}
.panel__error {
  color: #b91c1c;
}
.grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}
.suite-list,
.report-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.75rem;
}
.suite-list li,
.report-list li {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.75rem 1rem;
}
.suite-list__header,
.report-list__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.25rem;
  gap: 0.5rem;
}
.status {
  text-transform: uppercase;
  font-size: 0.75rem;
  font-weight: 600;
}
.status.success {
  color: #16a34a;
}
.status.failed {
  color: #b91c1c;
}
.status.running {
  color: #f59e0b;
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
input,
textarea,
select {
  border-radius: 6px;
  border: 1px solid var(--border-color);
  padding: 0.5rem 0.75rem;
  font: inherit;
}
select {
  min-height: 140px;
}
button {
  align-self: flex-start;
  background-color: var(--accent-color);
  color: white;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  cursor: pointer;
}
button[type='button'] {
  background: none;
  color: var(--accent-color);
  border: 1px solid var(--accent-color);
  padding: 0.25rem 0.75rem;
}
pre {
  background: rgba(148, 163, 184, 0.15);
  padding: 0.5rem;
  border-radius: 6px;
  overflow-x: auto;
}
.empty {
  color: #6b7280;
}
</style>
