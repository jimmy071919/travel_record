<template>
  <div class="h-[calc(100vh-5rem)] w-full flex flex-col">
    <!-- 工具欄 -->
    <div class="bg-white shadow-md w-full">
      <div class="w-full px-8 py-4">
        <div class="flex items-center justify-center">
          <div class="container mx-auto flex justify-center space-x-4">
            <div class="flex space-x-4 items-center">
              <!-- 搜尋輸入框 -->
              <div class="relative">
                <input
                  v-model="searchQuery"
                  @keyup.enter="searchLocation"
                  type="text"
                  placeholder="輸入地點..."
                  class="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
                />
                <button
                  @click="searchLocation"
                  class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  :disabled="isSearching"
                >
                  <i class="fas fa-search"></i>
                </button>
              </div>
              <!-- 添加標記按鈕 -->
              <button
                @click="toggleMarkerMode"
                :class="['px-4 py-2 rounded-lg', isAddingMarker ? 'bg-red-500 text-white' : 'bg-blue-500 text-white']"
              >
                {{ isAddingMarker ? '取消添加' : '添加標記' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 地圖容器 -->
    <div ref="mapContainer" class="flex-1 relative"></div>

    <!-- 編輯表單對話框 -->
    <div v-if="editingMarker" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-4 max-w-lg w-full mx-4">
        <MarkerEditForm
          :marker="editingMarker"
          @submit="handleMarkerSubmit"
          @cancel="handleMarkerCancel"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import MarkerEditForm from '../components/MarkerEditForm.vue'
import { useRoute } from 'vue-router'

interface MarkerData {
  id?: string;
  location_name: string;
  latitude: number;
  longitude: number;
  description: string;
  photo_url?: string;
  created_at?: string;
  mapboxMarker?: mapboxgl.Marker;
}

const mapContainer = ref<HTMLElement | null>(null)
const map = ref<mapboxgl.Map | null>(null)
const isAddingMarker = ref(false)
const searchQuery = ref('')
const isSearching = ref(false)
const error = ref<string | null>(null)
const markers = ref<Array<MarkerData & { mapboxMarker?: mapboxgl.Marker }>>([])
const editingMarker = ref<MarkerData | null>(null)
const tempMarker = ref<mapboxgl.Marker | null>(null)

// 處理鍵盤事件
const handleKeyPress = (e: KeyboardEvent) => {
  if (e.key === 'Escape') {
    isAddingMarker.value = false
    editingMarker.value = null
  }
}

// Mapbox 訪問令牌
const MAPBOX_ACCESS_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN

// 設置 Mapbox token
mapboxgl.accessToken = MAPBOX_ACCESS_TOKEN

// 從後端刪除標記
async function deleteMarkerFromBackend(markerId: string) {
  try {
    const response = await fetch(`http://localhost:8000/records/${markerId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete marker');
    }
  } catch (error) {
    console.error('Error deleting marker:', error);
    throw error;
  }
}

// 刪除標記
async function deleteMarker(index: number) {
  if (markers.value[index]) {
    try {
      const marker = markers.value[index];
      
      // 確保標記有 id
      if (!marker.id) {
        console.error('Marker has no id');
        return;
      }

      // 從後端刪除標記
      await deleteMarkerFromBackend(marker.id);

      // 從地圖上移除標記
      if (marker.mapboxMarker) {
        marker.mapboxMarker.remove();
      }

      // 從陣列中移除標記
      markers.value.splice(index, 1);
    } catch (error) {
      console.error('Error deleting marker:', error);
      // 這裡可以加入錯誤提示給使用者
    }
  }
}

// 從後端更新標記
async function updateMarkerInBackend(markerId: string, markerData: Partial<MarkerData>) {
  try {
    const response = await fetch(`http://localhost:8000/records/${markerId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(markerData),
    });

    if (!response.ok) {
      throw new Error('Failed to update marker');
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating marker:', error);
    throw error;
  }
}

// 處理標記提交
const handleMarkerSubmit = async (markerData: MarkerData) => {
  try {
    // 保存到後端
    const savedMarker = await saveMarkerToBackend(markerData)

    // 創建永久標記
    const popup = new mapboxgl.Popup({
      offset: 25,
      closeButton: true,
      closeOnClick: false
    })
    .setHTML(`
      <div class="p-2">
        <h3 class="font-bold">${savedMarker.location_name}</h3>
        <p class="text-sm">${savedMarker.description || ''}</p>
        ${savedMarker.photo_url ? `<img src="${savedMarker.photo_url}" class="mt-2 h-32 w-auto object-cover rounded" />` : ''}
        <div class="mt-2 space-x-2">
          <button 
            class="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
            onclick="document.dispatchEvent(new CustomEvent('editMarker', { detail: ${markers.value.length} }))"
          >
            編輯
          </button>
          <button 
            class="px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
            onclick="document.dispatchEvent(new CustomEvent('deleteMarker', { detail: ${markers.value.length} }))"
          >
            刪除
          </button>
        </div>
      </div>
    `)

    const mapboxMarker = new mapboxgl.Marker()
      .setLngLat([markerData.longitude, markerData.latitude])
      .setPopup(popup)
      .addTo(map.value!)

    // 添加到標記列表
    markers.value.push({
      ...savedMarker,
      mapboxMarker
    })

    // 清理臨時標記和表單
    if (tempMarker.value) {
      tempMarker.value.remove()
      tempMarker.value = null
    }
    editingMarker.value = null
    isAddingMarker.value = false
  } catch (error) {
    console.error('保存標記時發生錯誤:', error)
    error.value = '保存標記失敗'
  }
}

// 處理取消標記
const handleMarkerCancel = () => {
  if (tempMarker.value) {
    tempMarker.value.remove()
    tempMarker.value = null
  }
  editingMarker.value = null
  isAddingMarker.value = false
}

// 從後端載入標記
async function loadMarkersFromBackend() {
  try {
    const response = await fetch('http://localhost:8000/records/')
    if (!response.ok) {
      throw new Error('載入標記失敗')
    }
    const data = await response.json()
    
    // 清除現有標記
    markers.value.forEach(marker => {
      if (marker.mapboxMarker) {
        marker.mapboxMarker.remove()
      }
    })
    markers.value = []

    // 添加所有標記到地圖
    for (const markerData of data) {
      const popup = new mapboxgl.Popup({
        offset: 25,
        closeButton: true,
        closeOnClick: false
      })
      .setHTML(`
        <div class="p-2">
          <h3 class="font-bold">${markerData.location_name}</h3>
          <p class="text-sm">${markerData.description || ''}</p>
          ${markerData.photo_url ? `<img src="${markerData.photo_url}" class="mt-2 h-32 w-auto object-cover rounded" />` : ''}
          <div class="mt-2 space-x-2">
            <button 
              class="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
              onclick="document.dispatchEvent(new CustomEvent('editMarker', { detail: ${markers.value.length} }))"
            >
              編輯
            </button>
            <button 
              class="px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
              onclick="document.dispatchEvent(new CustomEvent('deleteMarker', { detail: ${markers.value.length} }))"
            >
              刪除
            </button>
          </div>
        </div>
      `)

      const mapboxMarker = new mapboxgl.Marker()
        .setLngLat([markerData.longitude, markerData.latitude])
        .setPopup(popup)
        .addTo(map.value!)

      markers.value.push({
        ...markerData,
        mapboxMarker
      })
    }

    // 如果有標記，調整地圖視角到包含所有標記
    if (markers.value.length > 0) {
      const bounds = new mapboxgl.LngLatBounds()
      markers.value.forEach(marker => {
        bounds.extend([marker.longitude, marker.latitude])
      })
      map.value?.fitBounds(bounds, {
        padding: 50,
        maxZoom: 15
      })
    }
  } catch (error) {
    console.error('載入標記時發生錯誤:', error)
    error.value = '載入標記失敗'
  }
}

// 新增標記到後端
async function saveMarkerToBackend(markerData: MarkerData) {
  try {
    const response = await fetch('http://localhost:8000/records/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(markerData),
    });

    if (!response.ok) {
      throw new Error('Failed to save marker');
    }

    const savedMarker = await response.json();
    return savedMarker;
  } catch (error) {
    console.error('Error saving marker:', error);
    throw error;
  }
}

// 搜尋地點
const searchLocation = async () => {
  if (!searchQuery.value) return
  
  try {
    const response = await fetch(
      `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(searchQuery.value)}.json?access_token=${MAPBOX_ACCESS_TOKEN}&country=tw&language=zh-Hant`
    )
    
    if (!response.ok) {
      throw new Error('搜尋請求失敗')
    }
    
    const data = await response.json()
    
    if (!data || !data.features) {
      throw new Error('無效的搜尋結果')
    }
    
    // 如果有搜尋結果，移動到第一個結果的位置
    if (data.features.length > 0) {
      const [lng, lat] = data.features[0].center
      map.value?.flyTo({
        center: [lng, lat],
        zoom: 15,
        duration: 2000
      })
    } else {
      error.value = '找不到符合的地點'
    }
  } catch (err) {
    console.error('搜尋地點時發生錯誤:', err)
    error.value = '搜尋地點失敗'
  }
}

// 切換添加標記模式
const toggleMarkerMode = () => {
  isAddingMarker.value = !isAddingMarker.value
}

// 處理地圖點擊事件
const handleMapClick = (e: mapboxgl.MapMouseEvent) => {
  if (!isAddingMarker.value || !map.value) return

  const { lng: longitude, lat: latitude } = e.lngLat

  // 創建新的標記數據
  const newMarker: MarkerData = {
    location_name: "新標記",
    latitude,
    longitude,
    description: "",
    photo_url: null,
    created_at: new Date().toISOString()
  }

  // 顯示編輯表單
  editingMarker.value = newMarker

  // 創建臨時標記
  if (tempMarker.value) {
    tempMarker.value.remove()
  }

  tempMarker.value = new mapboxgl.Marker({
    draggable: true
  })
    .setLngLat([longitude, latitude])
    .addTo(map.value)

  // 監聽標記拖動結束事件
  tempMarker.value.on('dragend', () => {
    const newLngLat = tempMarker.value!.getLngLat()
    if (editingMarker.value) {
      editingMarker.value.longitude = newLngLat.lng
      editingMarker.value.latitude = newLngLat.lat
    }
  })
}

// RTL 插件狀態追踪
let rtlPluginLoaded = false

// 事件監聽器引用
let deleteMarkerListener: EventListener | null = null
let editMarkerListener: EventListener | null = null
let keyPressListener: EventListener | null = null

// 初始化地圖
const initializeMap = async () => {
  if (!mapContainer.value) return

  try {
    // 只在第一次加載 RTL 插件
    if (!rtlPluginLoaded) {
      try {
        await mapboxgl.setRTLTextPlugin(
          'https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-rtl-text/v0.2.3/mapbox-gl-rtl-text.js',
          null,
          true
        )
        rtlPluginLoaded = true
      } catch (error) {
        // 忽略重複加載的錯誤
        if (error.message !== 'setRTLTextPlugin cannot be called multiple times.') {
          throw error
        }
      }
    }

    // 如果已經有地圖實例，先移除它
    if (map.value) {
      map.value.remove()
    }

    // 初始化地圖
    map.value = new mapboxgl.Map({
      container: mapContainer.value,
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [121.5654, 25.0330], // 預設中心點（台北）
      zoom: 13,
      language: 'zh-Hant', // 設定為繁體中文
      localIdeographFontFamily: "'Noto Sans TC', 'Microsoft JhengHei', sans-serif" // 設定中文字體
    })

    // 添加控制項
    map.value.addControl(new mapboxgl.NavigationControl(), 'top-right')
    map.value.addControl(
      new mapboxgl.GeolocateControl({
        positionOptions: {
          enableHighAccuracy: true
        },
        trackUserLocation: true
      }),
      'top-right'
    )

    // 等待地圖載入完成
    await new Promise<void>((resolve) => {
      map.value!.on('load', () => resolve())
    })

    // 綁定地圖點擊事件
    map.value.on('click', handleMapClick)
    
    // 載入現有標記
    await loadMarkersFromBackend()
    
    // 綁定事件監聽器
    if (!keyPressListener) {
      keyPressListener = handleKeyPress as EventListener
      window.addEventListener('keydown', keyPressListener)
    }
    
    if (!deleteMarkerListener) {
      deleteMarkerListener = ((e: CustomEvent) => {
        deleteMarker(e.detail)
      }) as EventListener
      document.addEventListener('deleteMarker', deleteMarkerListener)
    }
    
    if (!editMarkerListener) {
      editMarkerListener = ((e: CustomEvent) => {
        editingMarker.value = { ...markers.value[e.detail] }
      }) as EventListener
      document.addEventListener('editMarker', editMarkerListener)
    }
    
  } catch (error) {
    console.error('初始化地圖時發生錯誤:', error)
    error.value = '初始化地圖時發生錯誤'
  }
}

// 組件卸載時清理資源
onUnmounted(() => {
  // 移除所有標記
  markers.value.forEach(marker => {
    if (marker.mapboxMarker) {
      marker.mapboxMarker.remove()
    }
  })
  
  // 移除臨時標記
  if (tempMarker.value) {
    tempMarker.value.remove()
  }
  
  // 移除事件監聽器
  if (keyPressListener) {
    window.removeEventListener('keydown', keyPressListener)
    keyPressListener = null
  }
  
  if (deleteMarkerListener) {
    document.removeEventListener('deleteMarker', deleteMarkerListener)
    deleteMarkerListener = null
  }
  
  if (editMarkerListener) {
    document.removeEventListener('editMarker', editMarkerListener)
    editMarkerListener = null
  }
  
  // 銷毀地圖實例
  if (map.value) {
    map.value.remove()
    map.value = null
  }
})

// 監聽路由變化，重新初始化地圖
const route = useRoute()
watch(
  () => route.path,
  () => {
    if (route.path === '/map') {
      nextTick(() => {
        initializeMap()
      })
    }
  }
)

// 在組件掛載時初始化
onMounted(() => {
  initializeMap()
})
</script>

<style>
.mapboxgl-map {
  width: 100%;
  height: 100%;
}

.mapboxgl-canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>
