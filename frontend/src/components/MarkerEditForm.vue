<template>
  <div class="p-4 bg-white rounded-lg shadow">
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700">地點名稱</label>
        <input
          v-model="formData.location_name"
          type="text"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          required
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">描述</label>
        <textarea
          v-model="formData.description"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          rows="3"
        ></textarea>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">照片</label>
        <input
          type="file"
          @change="handleFileChange"
          accept="image/*"
          class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        <img
          v-if="formData.photo_url"
          :src="formData.photo_url"
          class="mt-2 h-32 w-auto object-cover rounded"
        />
      </div>

      <div class="flex justify-end space-x-2">
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          取消
        </button>
        <button
          type="submit"
          class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? '儲存中...' : '儲存' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const props = defineProps<{
  marker: {
    id?: string
    location_name: string
    description?: string
    photo_url?: string
    latitude: number
    longitude: number
  }
}>()

const emit = defineEmits<{
  (e: 'submit', data: any): void
  (e: 'cancel'): void
}>()

const isSubmitting = ref(false)
const formData = reactive({
  location_name: props.marker.location_name,
  description: props.marker.description || '',
  photo_url: props.marker.photo_url || '',
  photo_file: null as File | null
})

async function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    formData.photo_file = input.files[0]
    // 創建預覽
    formData.photo_url = URL.createObjectURL(input.files[0])
  }
}

async function handleSubmit() {
  try {
    isSubmitting.value = true
    
    // 如果有新照片，先上傳照片
    let photo_url = formData.photo_url
    if (formData.photo_file) {
      const formData = new FormData()
      formData.append('file', formData.photo_file)
      
      const response = await fetch('http://localhost:8000/records/upload-photo/', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        throw new Error('Failed to upload photo')
      }
      
      const result = await response.json()
      photo_url = result.url
    }
    
    // 發送更新的資料
    emit('submit', {
      ...props.marker,
      location_name: formData.location_name,
      description: formData.description,
      photo_url
    })
  } catch (error) {
    console.error('Error submitting form:', error)
  } finally {
    isSubmitting.value = false
  }
}
</script>
