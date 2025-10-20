<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { API_BASE, request } from '../api'

const props = defineProps({
  projectId: {
    type: Number,
    default: null,
  },
})

const interfaces = ref([])
const cases = ref([])
const selectedInterface = ref(null)
const error = ref('')
const swaggerState = reactive({
  text: '',
  file: null,
  loading: false,
})

const interfaceForm = reactive({
  name: '',
  method: 'GET',
  path: '',
  description: '',
  request_params: '{}',
  request_body: '{}',
  headers: '{}',
})

const caseForm = reactive({
  name: '',
  description: '',
  environment: null,
  request_payload: '{}',
  assertions: '[]',
  extractions: '[]',
})

const httpMethods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']

watch(
  () => props.projectId,
  (value) => {
    interfaces.value = []
    cases.value = []
    selectedInterface.value = null
    error.value = ''
    if (value) {
      loadInterfaces()
    }
  },
  { immediate: true }
)

watch(selectedInterface, (value) => {
  if (value) {
    loadCases(value.id)
  } else {
    cases.value = []
  }
})

async function loadInterfaces() {
  if (!props.projectId) return
  try {
    interfaces.value = await request(`interfaces/?project=${props.projectId}`)
    if (interfaces.value.length) {
      selectedInterface.value = interfaces.value[0]
    }
  } catch (err) {
    error.value = err.message
  }
}

async function loadCases(interfaceId) {
  try {
    cases.value = await request(`interface-cases/?interface=${interfaceId}`)
  } catch (err) {
    error.value = err.message
  }
}

function parseJson(value, fallback) {
  try {
    return value ? JSON.parse(value) : fallback
  } catch (err) {
    throw new Error('JSON 字段格式错误')
  }
}

async function createInterface() {
  if (!props.projectId) return
  if (!interfaceForm.name || !interfaceForm.path) {
    error.value = '接口名称和路径不能为空'
    return
  }
  try {
    const payload = await request('interfaces/', {
      method: 'POST',
      body: JSON.stringify({
        project: props.projectId,
        name: interfaceForm.name,
        method: interfaceForm.method,
        path: interfaceForm.path,
        description: interfaceForm.description,
        request_params: parseJson(interfaceForm.request_params, {}),
        request_body: parseJson(interfaceForm.request_body, {}),
        headers: parseJson(interfaceForm.headers, {}),
      }),
    })
    interfaces.value.push(payload)
    selectedInterface.value = payload
    error.value = ''
    Object.assign(interfaceForm, {
      name: '',
      method: 'GET',
      path: '',
      description: '',
      request_params: '{}',
      request_body: '{}',
      headers: '{}',
    })
  } catch (err) {
    error.value = err.message
  }
}

async function createCase() {
  if (!selectedInterface.value) return
  try {
    const payload = await request('interface-cases/', {
      method: 'POST',
      body: JSON.stringify({
        interface: selectedInterface.value.id,
        name: caseForm.name,
        description: caseForm.description,
        environment: caseForm.environment || null,
        request_payload: parseJson(caseForm.request_payload, {}),
        assertions: parseJson(caseForm.assertions, []),
        extractions: parseJson(caseForm.extractions, []),
      }),
    })
    cases.value.push(payload)
    error.value = ''
    Object.assign(caseForm, {
      name: '',
      description: '',
      environment: null,
      request_payload: '{}',
      assertions: '[]',
      extractions: '[]',
    })
  } catch (err) {
    error.value = err.message
  }
}

const casePreview = computed(() =>
  cases.value.map((item) => ({
    id: item.id,
    name: item.name,
    assertions: item.assertions?.length || 0,
    extractions: item.extractions?.length || 0,
  }))
)

function onSwaggerFileChange(event) {
  const [file] = event.target.files || []
  swaggerState.file = file || null
}

async function importSwagger() {
  if (!props.projectId) return
  if (!swaggerState.file && !swaggerState.text) {
    error.value = '请上传 Swagger 文件或粘贴 JSON 文本'
    return
  }
  const formData = new FormData()
  formData.append('project', props.projectId)
  if (swaggerState.file) {
    formData.append('file', swaggerState.file)
  } else {
    formData.append('swagger', swaggerState.text)
  }
  try {
    swaggerState.loading = true
    const response = await fetch(`${API_BASE}swagger/import/`, {
      method: 'POST',
      body: formData,
    })
    const payload = await response.json().catch(() => ({}))
    if (!response.ok) {
      throw new Error(payload.detail || 'Swagger 导入失败')
    }
    await loadInterfaces()
    error.value = ''
    swaggerState.text = ''
    swaggerState.file = null
  } catch (err) {
    error.value = err.message
  } finally {
    swaggerState.loading = false
  }
}
</script>

<template>
  <section class="panel">
    <header class="panel__header">
      <h2>接口定义与调试</h2>
      <span v-if="projectId">项目 ID：{{ projectId }}</span>
    </header>
    <p v-if="!projectId" class="empty">选择项目后可维护接口。</p>
    <template v-else>
      <p v-if="error" class="panel__error">{{ error }}</p>
      <form class="swagger" @submit.prevent="importSwagger">
        <label>
          上传 Swagger 文件
          <input type="file" accept=".json,.yaml,.yml" @change="onSwaggerFileChange" />
        </label>
        <label>
          或粘贴 OpenAPI JSON
          <textarea v-model="swaggerState.text" rows="3" placeholder="{ &quot;openapi&quot;: &quot;3.0.0&quot; }"></textarea>
        </label>
        <button type="submit" :disabled="swaggerState.loading">导入</button>
      </form>
      <div class="grid">
        <div>
          <h3>接口列表</h3>
          <ul class="interface-list">
            <li
              v-for="item in interfaces"
              :key="item.id"
              :class="{ active: selectedInterface?.id === item.id }"
              @click="selectedInterface = item"
            >
              <strong>{{ item.method }}</strong>
              <span>{{ item.name }}</span>
              <small>{{ item.path }}</small>
            </li>
          </ul>
          <form class="form" @submit.prevent="createInterface">
            <h4>新增接口</h4>
            <label>
              名称
              <input v-model="interfaceForm.name" placeholder="用户查询" />
            </label>
            <label>
              方法
              <select v-model="interfaceForm.method">
                <option v-for="method in httpMethods" :key="method">{{ method }}</option>
              </select>
            </label>
            <label>
              路径
              <input v-model="interfaceForm.path" placeholder="/api/users" />
            </label>
            <label>
              描述
              <textarea v-model="interfaceForm.description" rows="2"></textarea>
            </label>
            <label>
              Query/Params(JSON)
              <textarea v-model="interfaceForm.request_params" rows="2"></textarea>
            </label>
            <label>
              请求体(JSON)
              <textarea v-model="interfaceForm.request_body" rows="2"></textarea>
            </label>
            <label>
              请求头(JSON)
              <textarea v-model="interfaceForm.headers" rows="2"></textarea>
            </label>
            <button type="submit">保存接口</button>
          </form>
        </div>
        <div>
          <h3>接口用例</h3>
          <p v-if="!selectedInterface" class="empty">选择一个接口查看用例。</p>
          <template v-else>
            <ul class="case-list">
              <li v-for="item in casePreview" :key="item.id">
                <strong>{{ item.name }}</strong>
                <small>断言 {{ item.assertions }} · 提取 {{ item.extractions }}</small>
              </li>
            </ul>
            <form class="form" @submit.prevent="createCase">
              <h4>新增用例</h4>
              <label>
                名称
                <input v-model="caseForm.name" placeholder="成功请求" />
              </label>
              <label>
                描述
                <textarea v-model="caseForm.description" rows="2"></textarea>
              </label>
              <label>
                请求体(JSON)
                <textarea v-model="caseForm.request_payload" rows="3"></textarea>
              </label>
              <label>
                断言配置(JSON 数组)
                <textarea v-model="caseForm.assertions" rows="3" placeholder='[{"path":"$.status","expected":200}]'></textarea>
              </label>
              <label>
                提取配置(JSON 数组)
                <textarea v-model="caseForm.extractions" rows="3" placeholder='[{"name":"token","path":"$.data.token"}]'></textarea>
              </label>
              <button type="submit">保存用例</button>
            </form>
          </template>
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
.interface-list,
.case-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
  display: grid;
  gap: 0.5rem;
}
.interface-list li,
.case-list li {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.75rem;
  display: grid;
  gap: 0.25rem;
  cursor: pointer;
}
.interface-list li.active {
  border-color: var(--accent-color);
  background-color: rgba(59, 130, 246, 0.1);
}
.form {
  display: grid;
  gap: 0.75rem;
}
.swagger {
  display: grid;
  gap: 0.5rem;
  border: 1px dashed var(--border-color);
  padding: 0.75rem;
  border-radius: 8px;
  background: rgba(59, 130, 246, 0.05);
  margin-bottom: 1rem;
}
.swagger label {
  display: grid;
  gap: 0.25rem;
  font-size: 0.875rem;
}
.swagger button {
  justify-self: flex-start;
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
