<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">旅行記錄</h1>
      <router-link 
        to="/map" 
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
      >
        新增記錄
      </router-link>
    </div>

    <!-- 記錄列表 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="record in records" 
        :key="record.id" 
        class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
      >
        <!-- 記錄卡片 -->
        <div class="relative">
          <!-- 照片 -->
          <img 
            v-if="record.photo_url" 
            :src="record.photo_url" 
            :alt="record.location_name"
            class="w-full h-48 object-cover"
          >
          <div v-else class="w-full h-48 bg-gray-200 flex items-center justify-center">
            <span class="text-gray-400">無照片</span>
          </div>
          
          <!-- 編輯和刪除按鈕 -->
          <div class="absolute top-2 right-2 space-x-2">
            <button 
              @click="editRecord(record)"
              class="p-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              <i class="fas fa-edit"></i>
            </button>
            <button 
              @click="deleteRecord(record.id)"
              class="p-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>

        <!-- 記錄內容 -->
        <div class="p-4">
          <h3 class="text-xl font-semibold mb-2">{{ record.location_name }}</h3>
          <p class="text-gray-600 mb-2">{{ record.description }}</p>
          <div class="text-sm text-gray-500">
            <p>位置：{{ record.latitude.toFixed(6) }}, {{ record.longitude.toFixed(6) }}</p>
            <p>時間：{{ formatDate(record.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 編輯對話框 -->
    <div v-if="editingRecord" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
        <h2 class="text-xl font-bold mb-4">編輯記錄</h2>
        
        <div class="space-y-4">
          <!-- 地點名稱 -->
          <div>
            <label class="block text-sm font-medium text-gray-700">地點名稱</label>
            <input 
              v-model="editingRecord.location_name"
              type="text"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
          </div>

          <!-- 描述 -->
          <div>
            <label class="block text-sm font-medium text-gray-700">描述</label>
            <textarea
              v-model="editingRecord.description"
              rows="3"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            ></textarea>
          </div>

          <!-- 照片 -->
          <div>
            <label class="block text-sm font-medium text-gray-700">照片</label>
            <div class="mt-1 flex items-center space-x-4">
              <img 
                v-if="editingRecord.photo_url" 
                :src="editingRecord.photo_url" 
                class="h-20 w-20 object-cover rounded"
              >
              <input 
                type="file" 
                accept="image/*"
                @change="handlePhotoChange"
                class="mt-1"
              >
            </div>
          </div>
        </div>

        <!-- 按鈕 -->
        <div class="mt-6 flex justify-end space-x-3">
          <button 
            @click="cancelEdit"
            class="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
          >
            取消
          </button>
          <button 
            @click="saveEdit"
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 記錄列表
const records = ref<any[]>([])

// 編輯中的記錄
const editingRecord = ref<any>(null)

// 載入記錄
const loadRecords = async () => {
  try {
    const response = await fetch('http://localhost:8000/records/')
    if (!response.ok) {
      throw new Error('載入記錄失敗')
    }
    records.value = await response.json()
  } catch (error) {
    console.error('載入記錄時發生錯誤:', error)
  }
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 編輯記錄
const editRecord = (record: any) => {
  editingRecord.value = { ...record }
}

// 取消編輯
const cancelEdit = () => {
  editingRecord.value = null
}

// 處理照片變更
const handlePhotoChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]
    
    // 檢查文件大小
    if (file.size > 10 * 1024 * 1024) {
      alert('照片大小不能超過 10MB')
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await fetch('http://localhost:8000/records/upload-photo/', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        throw new Error('上傳照片失敗')
      }
      
      const data = await response.json()
      editingRecord.value.photo_url = data.url
    } catch (error) {
      console.error('上傳照片時發生錯誤:', error)
      alert('上傳照片失敗')
    }
  }
}

// 保存編輯
const saveEdit = async () => {
  try {
    const response = await fetch(`http://localhost:8000/records/${editingRecord.value.id}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(editingRecord.value)
    })

    if (!response.ok) {
      throw new Error('保存記錄失敗')
    }

    // 更新記錄列表中的數據
    const index = records.value.findIndex(r => r.id === editingRecord.value.id)
    if (index !== -1) {
      records.value[index] = { ...editingRecord.value }
    }

    // 關閉編輯對話框
    editingRecord.value = null
  } catch (error) {
    console.error('保存記錄時發生錯誤:', error)
    alert('保存記錄失敗')
  }
}

// 刪除記錄
const deleteRecord = async (id: string) => {
  if (!confirm('確定要刪除這條記錄嗎？')) {
    return
  }

  try {
    const response = await fetch(`http://localhost:8000/records/${id}/`, {
      method: 'DELETE'
    })

    if (!response.ok) {
      throw new Error('刪除記錄失敗')
    }

    // 從列表中移除記錄
    records.value = records.value.filter(r => r.id !== id)
  } catch (error) {
    console.error('刪除記錄時發生錯誤:', error)
    alert('刪除記錄失敗')
  }
}

// 組件掛載時載入記錄
onMounted(() => {
  loadRecords()
})
</script>
