<template>
  <div class="bg-white rounded-lg p-6 shadow-lg max-w-md w-full">
    <h3 class="text-2xl font-bold mb-6">{{ isEditing ? '編輯標記' : '新增標記' }}</h3>
    
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- 地點名稱 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          地點名稱
        </label>
        <input
          v-model="form.location_name"
          type="text"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
      </div>

      <!-- 描述 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          描述
        </label>
        <textarea
          v-model="form.description"
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        ></textarea>
      </div>

      <!-- 照片上傳 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          照片
        </label>
        <div class="mt-1 flex items-center space-x-4">
          <img
            v-if="form.photo_url"
            :src="form.photo_url"
            alt="預覽"
            class="h-20 w-20 object-cover rounded"
          >
          <input
            type="file"
            accept="image/*"
            @change="handlePhotoChange"
            class="mt-1"
          >
        </div>
        <p v-if="uploadError" class="mt-1 text-sm text-red-600">
          {{ uploadError }}
        </p>
      </div>

      <!-- 按鈕 -->
      <div class="flex justify-end space-x-3">
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
        >
          取消
        </button>
        <button
          type="submit"
          :disabled="isSubmitting"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {{ isSubmitting ? '保存中...' : '保存' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

const props = defineProps<{
  marker?: {
    id?: string
    location_name?: string
    description?: string
    latitude: number
    longitude: number
    photo_url?: string
    photo_path?: string
  }
}>()

const emit = defineEmits<{
  (e: 'save', data: any): void
  (e: 'cancel'): void
}>()

const isEditing = ref(!!props.marker?.id)
const isSubmitting = ref(false)
const uploadError = ref('')

const form = reactive({
  location_name: props.marker?.location_name || '',
  description: props.marker?.description || '',
  latitude: props.marker?.latitude,
  longitude: props.marker?.longitude,
  photo_url: props.marker?.photo_url || '',
  photo_path: props.marker?.photo_path || ''
})

// 處理照片上傳
const handlePhotoChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  
  const file = input.files[0]
  if (file.size > 10 * 1024 * 1024) {
    uploadError.value = '照片大小不能超過 10MB'
    return
  }

  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch('http://localhost:8000/api/upload-photo/', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('上傳照片失敗')
    }
    
    const data = await response.json()
    form.photo_url = data.photo_url  // 用於預覽
    form.photo_path = data.photo_path  // 用於保存到資料庫
    uploadError.value = ''
  } catch (error) {
    console.error('上傳照片時發生錯誤:', error)
    uploadError.value = '上傳照片失敗'
  }
}

// 處理表單提交
const handleSubmit = async () => {
  isSubmitting.value = true
  try {
    emit('save', {
      ...form,
      id: props.marker?.id,
      photo_path: form.photo_path  // 確保傳遞 photo_path
    })
  } finally {
    isSubmitting.value = false
  }
}
</script>
