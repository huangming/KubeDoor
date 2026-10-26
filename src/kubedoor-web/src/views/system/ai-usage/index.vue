<script setup lang="ts">
import { withPrefix } from "@/prefix/path";
</script>
<template>
  <iframe
    class="w-full h-full"
    :src="withPrefix('/grafana/d/KubeDoor-AI/?kiosk')"
    frameborder="0"
  />
</template>
