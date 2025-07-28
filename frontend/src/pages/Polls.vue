<template>
    <div>
        <h1 class="text-3xl font-bold">👌polls page</h1>
        
        <div v-if="pollsResource.list.data">
            <p v-for="poll in pollsResource.list.data" :key="poll.name">{{ poll.title }}</p>
        </div>
    </div>
</template>

<script setup>
import { createListResource } from 'frappe-ui';

const pollsResource = createListResource({
    doctype: 'Poll',
    fields: ['name', 'title', 'description', 'start_date', 'end_date'],
    auto: true,
});
</script>