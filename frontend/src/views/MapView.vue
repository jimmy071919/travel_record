<template>
  <div class="h-[calc(100vh-5rem)] w-full flex flex-col">
    <!-- 工具欄 -->
    <div class="bg-white shadow-md w-full">
      <div class="w-full px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex space-x-4 items-center">
            <!-- 搜尋輸入框和建議列表 -->
            <div class="relative">
              <input
                v-model="searchQuery"
                @input="searchSuggestions"
                @keydown="handleKeydown"
                @blur="closeSuggestions"
                type="text"
                placeholder="輸入地點..."
                class="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
                :disabled="isSearching"
              />
              <button
                @click="searchLocation"
                class="absolute right-2 top-1/2 transform -translate-y-1/2"
                :disabled="isSearching"
              >
                <i :class="['fas', isSearching ? 'fa-spinner fa-spin' : 'fa-search']"></i>
              </button>

              <!-- 搜尋建議列表 -->
              <div
                v-if="showSuggestions && searchResults.length > 0"
                class="absolute z-50 w-full mt-1 bg-white rounded-lg shadow-lg border border-gray-200 max-h-60 overflow-y-auto"
              >
                <div
                  v-for="(result, index) in searchResults"
                  :key="result.id"
                  @mousedown="selectSuggestion(result)"
                  @mouseover="selectedIndex = index"
                  :class="[
                    'px-4 py-2 cursor-pointer hover:bg-gray-100',
                    selectedIndex === index ? 'bg-blue-50' : ''
                  ]"
                >
                  <div class="font-medium">{{ result.text }}</div>
                  <div class="text-sm text-gray-500">{{ result.place_name }}</div>
                </div>
              </div>
            </div>

            <!-- 添加標記按鈕 -->
            <button
              @click="toggleMarkerMode"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {{ isAddingMarker ? '取消新增' : '新增標記' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 錯誤提示 -->
    <div 
      v-if="error" 
      class="fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative"
      role="alert"
    >
      <span class="block sm:inline">{{ error }}</span>
      <button 
        @click="error = null"
        class="absolute top-0 bottom-0 right-0 px-4 py-3"
      >
        <i class="fas fa-times"></i>
      </button>
    </div>

    <!-- 地圖容器 -->
    <div ref="mapContainer" class="flex-1 w-full relative">
      <!-- 載入中提示 -->
      <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-50">
        <div class="text-lg font-semibold">載入中...</div>
      </div>
    </div>

    <!-- 編輯表單對話框 -->
    <MarkerEditForm
      v-if="editingMarker || newMarker"
      :marker="editingMarker || newMarker"
      @save="saveMarker"
      @cancel="cancelEdit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import mapboxgl from 'mapbox-gl'
import MarkerEditForm from '../components/MarkerEditForm.vue'
import { MAPBOX_CONFIG } from '../config'

// 設置 Mapbox token
mapboxgl.accessToken = MAPBOX_CONFIG.accessToken

// 狀態定義
const mapContainer = ref<HTMLElement | null>(null)
const map = ref<mapboxgl.Map | null>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const isSearching = ref(false)
const showSuggestions = ref(false)
const selectedIndex = ref(-1)
const isAddingMarker = ref(false)
const newMarker = ref<mapboxgl.Marker | null>(null)

// 初始化地圖
const initializeMap = () => {
  if (!mapContainer.value) return

  try {
    isLoading.value = true

    // 創建地圖實例
    map.value = new mapboxgl.Map({
      container: mapContainer.value,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: MAPBOX_CONFIG.defaultCenter,
      zoom: MAPBOX_CONFIG.defaultZoom,
      attributionControl: true,
      localIdeographFontFamily: "'Noto Sans TC', 'Microsoft YaHei', sans-serif"
    })

    // 添加導航控制
    map.value.addControl(new mapboxgl.NavigationControl(), 'top-right')
    
    // 添加比例尺
    map.value.addControl(new mapboxgl.ScaleControl(), 'bottom-right')

    // 等待地圖載入完成
    map.value.on('load', () => {
      isLoading.value = false
    })

    // 添加點擊事件監聽
    map.value.on('click', handleMapClick)

  } catch (err) {
    console.error('初始化地圖時發生錯誤:', err)
    error.value = '初始化地圖時發生錯誤'
    isLoading.value = false
  }
}

// 組件卸載時清理
onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
})

// 在組件掛載時初始化地圖
onMounted(() => {
  initializeMap()
})

// 處理地圖點擊
const handleMapClick = (e: mapboxgl.MapMouseEvent) => {
  if (!isAddingMarker.value) return

  const { lng, lat } = e.lngLat

  // 如果已經有臨時標記，先移除
  if (newMarker.value) {
    newMarker.value.remove()
  }

  // 創建新標記
  newMarker.value = new mapboxgl.Marker()
    .setLngLat([lng, lat])
    .addTo(map.value!)
}

// 切換添加標記模式
const toggleMarkerMode = () => {
  isAddingMarker.value = !isAddingMarker.value
  if (!isAddingMarker.value && newMarker.value) {
    newMarker.value.remove()
    newMarker.value = null
  }
}

// 搜尋地點
const searchLocation = async () => {
  if (!searchQuery.value) return

  try {
    isSearching.value = true
    const response = await fetch(
      `${MAPBOX_CONFIG.geocoding.endpoint}/${encodeURIComponent(searchQuery.value)}.json?` +
      `access_token=${MAPBOX_CONFIG.accessToken}&` +
      `language=${MAPBOX_CONFIG.language}&` +
      `country=${MAPBOX_CONFIG.geocoding.country}&` +
      `types=${MAPBOX_CONFIG.geocoding.types.join(',')}&` +
      `limit=${MAPBOX_CONFIG.geocoding.limit}`
    )

    if (!response.ok) {
      throw new Error('搜尋失敗')
    }

    const data = await response.json()
    searchResults.value = data.features
    showSuggestions.value = true
  } catch (err) {
    console.error('搜尋地點時發生錯誤:', err)
    error.value = '搜尋地點時發生錯誤'
  } finally {
    isSearching.value = false
  }
}

// 選擇搜尋建議
const selectSuggestion = (result: any) => {
  if (!map.value) return

  const [lng, lat] = result.center
  map.value.flyTo({
    center: [lng, lat],
    zoom: 15
  })

  showSuggestions.value = false
  searchQuery.value = result.text
}

// 關閉建議列表
const closeSuggestions = () => {
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}
</script>