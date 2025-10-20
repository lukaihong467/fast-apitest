<script setup>
import { reactive, ref, watch } from 'vue'
import { request } from '../api'

const props = defineProps({
  projectId: {
    type: Number,
    default: null,
  },
})

const scenarios = ref([])
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
    scenarios.value = []
    cases.value = []
    if (value) {
      loadScenarios()
      loadCases()
    }
  },
  { immediate: true }
)

async function loadScenarios() {
  if (!props.projectId) return
  try {
    scenarios.value = await request(`scenarios/?project=${props.projectId}`)
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

async function createScenario() {
  if (!props.projectId) return
  if (!form.name || !form.selectedCases.length) {
    error.value = '请填写名称并选择至少一个接口用例'
    return
  }
  try {
    const steps = form.selectedCases.map((caseId, index) => ({ interface_case: Number(caseId), order: index + 1 }))
    const created = await request('scenarios/', {
      method: 'POST',
      body: JSON.stringify({
        project: props.projectId,
        name: form.name,
        description: form.description,
        steps,
      }),
    })
    scenarios.value.push(created)
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
</script>

<template>
  <section class="panel">
    <header class="panel__header">
      <h2>场景编排</h2>
      <span v-if="projectId">项目 ID：{{ projectId }}</span>
    </header>
    <p v-if="!projectId" class="empty">请选择项目后管理场景。</p>
    <template v-else>
      <p v-if="error" class="panel__error">{{ error }}</p>
      <div class="grid">
        <div>
          <h3>场景列表</h3>
          <ul class="scenario-list">
            <li v-for="scenario in scenarios" :key="scenario.id">
              <strong>{{ scenario.name }}</strong>
              <small>步骤：{{ scenario.steps?.length || 0 }}</small>
              <p>{{ scenario.description }}</p>
            </li>
          </ul>
        </div>
        <div>
          <h3>创建场景</h3>
          <form class="form" @submit.prevent="createScenario">
            <label>
              名称
              <input v-model="form.name" placeholder="登录 + 查询场景" />
            </label>
            <label>
              描述
              <textarea v-model="form.description" rows="3"></textarea>
            </label>
            <label>
              选择用例（按顺序执行）
              <select multiple v-model="form.selectedCases">
                <option v-for="item in cases" :key="item.id" :value="item.id">
                  {{ item.interface_name }} · {{ item.name }}
                </option>
              </select>
            </label>
            <button type="submit">保存场景</button>
          </form>
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
.scenario-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.75rem;
}
.scenario-list li {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.75rem 1rem;
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
.empty {
  color: #6b7280;
}
</style>
