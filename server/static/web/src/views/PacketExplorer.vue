<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  aed_id: String,
})

const filter = ref('')
const packets = ref([])
const pagination = ref({
  page: 1,
  page_size: 5000,
  total_packets: 0,
  total_pages: 1,
  has_next: false,
  has_prev: false,
})
const fromCache = ref(false)
const loading = ref(false)
const error = ref('')

function resetResults() {
  packets.value = []
  pagination.value = {
    page: 1,
    page_size: 5000,
    total_packets: 0,
    total_pages: 1,
    has_next: false,
    has_prev: false,
  }
  fromCache.value = false
}

function fetchPage(page = 1) {
  if (!props.aed_id) {
    error.value = 'Missing AED ID.'
    return
  }

  loading.value = true
  error.value = ''

  fetch('/aed_reviewer/api/' + props.aed_id + '/dumps/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      filter: filter.value,
      page,
    }),
  })
    .then(response => response.json())
    .then(data => {
      if (data.success === false) {
        error.value = data.message || 'Search failed.'
        resetResults()
        return
      }

      packets.value = data.packets || []
      pagination.value = data.pagination || pagination.value
      fromCache.value = data.from_cache === true
    })
    .catch(() => {
      error.value = 'Search failed.'
      resetResults()
    })
    .finally(() => {
      loading.value = false
    })
}

function onSearch() {
  fetchPage(1)
}

function goPrev() {
  if (pagination.value.has_prev) {
    fetchPage(pagination.value.page - 1)
  }
}

function goNext() {
  if (pagination.value.has_next) {
    fetchPage(pagination.value.page + 1)
  }
}

function goPage(page) {
  if (page >= 1 && page <= pagination.value.total_pages) {
    fetchPage(page)
  }
}

const pageButtons = computed(() => {
  const maxPages = Math.min(9, pagination.value.total_pages || 1)
  return Array.from({ length: maxPages }, (_, index) => index + 1)
})
</script>

<template>
  <div class="container-fluid">
    <div class="row mb-3">
      <div class="col-12 col-lg-8">
        <label class="form-label">FCAP Filter</label>
        <div class="input-group">
          <input
            v-model="filter"
            @keyup.enter="onSearch"
            type="text"
            class="form-control"
            placeholder="e.g., dst port 80 and src port 1024..65535"
          />
          <button class="btn btn-primary" @click="onSearch" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            <span v-else>Search</span>
          </button>
        </div>
        <div class="form-text">
          Examples: <code>proto tcp</code>, <code>dst net 192.168.1.0/24</code>, <code>not src port 22</code>
        </div>
      </div>
      <div class="col-12 col-lg-4 d-flex align-items-end justify-content-lg-end mt-3 mt-lg-0">
        <div class="text-end">
          <div class="fw-semibold">Matched Packets</div>
          <div class="display-6">{{ pagination.total_packets }}</div>
          <div class="text-muted" v-if="fromCache">From cache</div>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="d-flex justify-content-between align-items-center mb-2">
      <div class="text-muted">
        Page {{ pagination.page }} of {{ pagination.total_pages }}
      </div>
      <div v-if="pagination.total_pages > 1" class="btn-group">
        <button class="btn btn-outline-secondary" @click="goPrev" :disabled="!pagination.has_prev || loading">
          Previous
        </button>
        <button
          v-for="page in pageButtons"
          :key="page"
          class="btn btn-outline-secondary"
          :class="{ active: page === pagination.page }"
          :disabled="loading || page > pagination.total_pages"
          @click="goPage(page)"
        >
          {{ page }}
        </button>
        <button class="btn btn-outline-secondary" @click="goNext" :disabled="!pagination.has_next || loading">
          Next
        </button>
      </div>
    </div>

    <div class="table-responsive">
      <table class="table table-striped table-hover align-middle">
        <thead>
          <tr>
            <th>#</th>
            <th>Len</th>
            <th>Src IP</th>
            <th>Src Port</th>
            <th>Dst IP</th>
            <th>Dst Port</th>
            <th>Proto</th>
            <th>Flags</th>
            <th>Country</th>
            <th>Action</th>
            <th>PG ID</th>
            <th>PG Name</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!loading && packets.length === 0">
            <td colspan="12" class="text-center text-muted">No packets to display</td>
          </tr>
          <tr v-for="packet in packets" :key="packet['#'] + '-' + packet.src_ip + '-' + packet.dst_ip">
            <td>{{ packet['#'] ?? '-' }}</td>
            <td>{{ packet.len ?? '-' }}</td>
            <td>{{ packet.src_ip ?? '-' }}</td>
            <td>{{ packet.src_port ?? '-' }}</td>
            <td>{{ packet.dst_ip ?? '-' }}</td>
            <td>{{ packet.dst_port ?? '-' }}</td>
            <td>{{ packet.proto ?? '-' }}</td>
            <td>{{ packet.tcp_flags ?? '-' }}</td>
            <td>{{ packet.src_country ?? '-' }}</td>
            <td>{{ packet.action ?? '-' }}</td>
            <td>{{ packet.pg_id ?? '-' }}</td>
            <td>{{ packet.pg_name ?? '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="d-flex justify-content-between align-items-center mt-2">
      <div class="text-muted">
        Showing up to {{ pagination.page_size }} packets per page
      </div>
      <div v-if="pagination.total_pages > 1" class="btn-group">
        <button class="btn btn-outline-secondary" @click="goPrev" :disabled="!pagination.has_prev || loading">
          Previous
        </button>
        <button
          v-for="page in pageButtons"
          :key="'bottom-' + page"
          class="btn btn-outline-secondary"
          :class="{ active: page === pagination.page }"
          :disabled="loading || page > pagination.total_pages"
          @click="goPage(page)"
        >
          {{ page }}
        </button>
        <button class="btn btn-outline-secondary" @click="goNext" :disabled="!pagination.has_next || loading">
          Next
        </button>
      </div>
    </div>
  </div>
</template>
