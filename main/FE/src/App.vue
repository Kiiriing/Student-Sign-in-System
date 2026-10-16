<script setup lang="ts">
</script>


<template>

<router-view />

</template>

<style>
/* 始终为垂直滚动条预留空间：列表筛选后内容变短、滚动条消失时，
   页面宽度不再变化，避免内容盒子被拉伸、布局横向抖动 */
html {
  scrollbar-gutter: stable;
}
</style>