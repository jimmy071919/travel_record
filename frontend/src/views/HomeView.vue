<template>
  <div class="min-h-screen bg-gray-100">
    <main class="max-w-7xl mx-auto px-8 py-8">
      <h1 class="text-4xl font-bold text-gray-900 mb-8">旅行回憶紀錄</h1>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <router-link 
          to="/map" 
          class="block p-8 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-200"
        >
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">地圖瀏覽</h2>
          <p class="text-lg text-gray-600">在互動式地圖上查看和添加您的旅行足跡</p>
        </router-link>
        
        <router-link 
          to="/records" 
          class="block p-8 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-200"
        >
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">旅行記錄</h2>
          <p class="text-lg text-gray-600">瀏覽您的所有旅行回憶</p>
        </router-link>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// Component logic here
</script>
