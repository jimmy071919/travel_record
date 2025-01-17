<template>
  <div class="min-h-screen bg-gray-100">
    <main class="max-w-7xl mx-auto px-8 py-8">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">旅行記錄</h1>
        <button class="btn btn-primary text-lg px-6 py-3">新增記錄</button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <!-- 記錄卡片 -->
        <div v-for="record in records" :key="record.id" class="bg-white rounded-lg shadow-lg overflow-hidden">
          <img 
            :src="record.photoUrl" 
            :alt="record.locationName"
            class="w-full h-56 object-cover"
          >
          <div class="p-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-3">{{ record.locationName }}</h3>
            <p class="text-lg text-gray-600 mb-4">{{ record.description }}</p>
            <div class="text-sm text-gray-500">
              {{ formatDate(record.createdAt) }}
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import dayjs from 'dayjs'

interface TravelRecord {
  id: string
  locationName: string
  description: string
  photoUrl: string
  createdAt: string
}

// 模擬數據
const records = ref<TravelRecord[]>([
  {
    id: '1',
    locationName: '台北101',
    description: '台北最高的建築物，夜景非常漂亮',
    photoUrl: 'https://example.com/taipei101.jpg',
    createdAt: '2025-01-16T12:00:00Z'
  }
])

const formatDate = (date: string) => {
  return dayjs(date).format('YYYY/MM/DD HH:mm')
}
</script>
