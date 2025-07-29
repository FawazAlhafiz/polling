<template>
    <div>
        <h1 class="text-3xl font-bold">👌polls page</h1>
        
        <div v-if="pollsList">
            <p v-for="poll in pollsList" :key="poll.name">{{ poll.title }}</p>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { createListResource } from 'frappe-ui';

const pollsResource = createListResource({
    doctype: 'Poll',
    fields: ['name', 'title', 'description', 'start_date', 'end_date'],
    auto: true,
});

const pollsList = computed(() => pollsResource.list.data || []);
</script>