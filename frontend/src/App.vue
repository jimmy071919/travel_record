<template>
  <div class="min-h-screen flex flex-col">
    <!-- 導航欄 -->
    <nav class="bg-white shadow-lg">
      <div class="max-w-7xl mx-auto px-8">
        <div class="flex justify-between h-20">
          <div class="flex items-center space-x-12">
            <router-link to="/" class="flex items-center">
              <span class="text-2xl font-bold text-gray-800">旅行回憶</span>
            </router-link>
            
            <div class="flex space-x-8">
              <router-link 
                to="/map"
                class="inline-flex items-center px-4 py-2 text-lg font-medium text-gray-900 hover:text-blue-600 hover:border-b-2 hover:border-blue-600"
                :class="{ 'border-b-2 border-blue-600': $route.path === '/map' }"
              >
                地圖
              </router-link>
              
              <router-link 
                to="/records"
                class="inline-flex items-center px-4 py-2 text-lg font-medium text-gray-900 hover:text-blue-600 hover:border-b-2 hover:border-blue-600"
                :class="{ 'border-b-2 border-blue-600': $route.path === '/records' }"
              >
                記錄
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主要內容區域 -->
    <main class="flex-1">
      <router-view v-slot="{ Component }">
        <component :is="Component" />
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import HelloWorld from './components/HelloWorld.vue'
</script>

<style>
/* 全局樣式 */
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
}

#app {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mapboxgl-map {
  width: 100%;
  height: 100%;
}

.router-link-active {
  color: #2563eb;
  border-bottom: 2px solid #2563eb;
}
</style>
