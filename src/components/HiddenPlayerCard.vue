<script setup lang="ts">
defineProps<{
    imageUrl?: string;
    revealed: boolean;
}>();
</script>

<template>
    <div class="hidden-player-card">
        <div class="image-frame">
            <img v-if="imageUrl" :src="imageUrl" alt="Hidden NBA player" class="player-image" :class="{ revealed }" />
            <div v-else class="fallback-shape" />
        </div>
    </div>
</template>

<style scoped>
.hidden-player-card {
    max-width: 320px;
    margin: 24px auto 0;
}

.image-frame {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid #d4d4d8;
    min-height: 240px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.player-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: brightness(0) contrast(1.8);
    transform: scale(1.03);
    transition:
        filter 0.25s ease,
        transform 0.25s ease;
}

.player-image.revealed {
    filter: brightness(1) contrast(1) blur(0);
    transform: scale(1);
}

.fallback-shape {
    width: 140px;
    height: 220px;
    border-radius: 70px 70px 30px 30px;
    background: rgba(255, 255, 255, 0.85);
}
</style>
