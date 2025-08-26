<template>
    <div class="max-w-4xl mx-auto p-6">
        <!-- Back Button -->
        <div class="mb-6">
            <button
                @click="goBack"
                class="inline-flex items-center text-blue-600 hover:text-blue-800 transition-colors"
            >
                ← Back to Polls
            </button>
        </div>

        <!-- Loading State -->
        <div v-if="pollResultResource.loading" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-4 text-gray-600">Loading poll results...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="pollResultResource.error" class="text-center py-12">
            <div class="text-6xl mb-4">❌</div>
            <h3 class="text-xl font-semibold text-gray-700 mb-2">Error Loading Results</h3>
            <p class="text-gray-500 mb-4">{{ pollResultResource.error }}</p>
            <button
                @click="pollResultResource.reload()"
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
                Try Again
            </button>
        </div>

        <!-- Results Content -->
        <div v-else-if="pollResult" class="space-y-8">
            <!-- Header -->
            <div class="text-center border-b border-gray-200 pb-6">
                <h1 class="text-3xl font-bold text-gray-800 mb-2">📊 Poll Results</h1>
                <h2 class="text-xl text-gray-600 mb-4">{{ pollResult.poll_title }}</h2>
                <div class="inline-flex items-center bg-gray-100 rounded-full px-4 py-2">
                    <span class="text-sm font-medium text-gray-700">
                        Total Votes: {{ pollResult.total_votes }}
                    </span>
                </div>
            </div>

            <!-- No Votes State -->
            <div v-if="pollResult.total_votes === 0" class="text-center py-12">
                <div class="text-6xl mb-4">🗳️</div>
                <h3 class="text-xl font-semibold text-gray-700 mb-2">No votes yet</h3>
                <p class="text-gray-500">Be the first to vote in this poll!</p>
            </div>

            <!-- Results Display -->
            <div v-else class="space-y-6">
                <!-- Visual Chart -->
                <div class="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-6">Vote Distribution</h3>
                    <div class="space-y-4">
                        <div
                            v-for="(option, index) in pollResult.options"
                            :key="option.option_text"
                            class="space-y-2"
                        >
                            <!-- Option Label -->
                            <div class="flex justify-between items-center">
                                <span class="font-medium text-gray-700">{{ option.option_text }}</span>
                                <span class="text-sm text-gray-500">
                                    {{ option.vote_count }} votes ({{ option.percentage }}%)
                                </span>
                            </div>
                            
                            <!-- Progress Bar -->
                            <div class="w-full bg-gray-200 rounded-full h-4">
                                <div
                                    class="h-4 rounded-full transition-all duration-500 ease-out"
                                    :class="getBarColor(index)"
                                    :style="{ width: option.percentage + '%' }"
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Detailed Statistics -->
                <div class="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-6">Detailed Statistics</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <div
                            v-for="(option, index) in pollResult.options"
                            :key="option.option_text"
                            class="text-center p-4 bg-gray-50 rounded-lg"
                        >
                            <div
                                class="w-16 h-16 rounded-full mx-auto mb-3 flex items-center justify-center text-white font-bold text-lg"
                                :class="getBarColor(index)"
                            >
                                {{ option.percentage }}%
                            </div>
                            <h4 class="font-medium text-gray-800 mb-1">{{ option.option_text }}</h4>
                            <p class="text-sm text-gray-600">{{ option.vote_count }} votes</p>
                        </div>
                    </div>
                </div>

                <!-- Winner/Leading Option -->
                <div v-if="winningOption" class="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200 p-6">
                    <div class="flex items-center justify-center">
                        <div class="text-center">
                            <div class="text-4xl mb-2">🏆</div>
                            <h3 class="text-lg font-semibold text-gray-800 mb-1">
                                {{ winningOption.percentage === getSecondHighest()?.percentage ? 'Leading Option' : 'Winning Option' }}
                            </h3>
                            <p class="text-xl font-bold text-green-700 mb-1">{{ winningOption.option_text }}</p>
                            <p class="text-sm text-gray-600">
                                {{ winningOption.vote_count }} votes ({{ winningOption.percentage }}%)
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Refresh Button -->
            <div class="text-center pt-6">
                <button
                    @click="pollResultResource.reload()"
                    class="px-6 py-2 border border-gray-300 text-gray-700 font-medium rounded-md hover:bg-gray-50 transition-colors"
                >
                    🔄 Refresh Results
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { createResource } from 'frappe-ui';

const route = useRoute();
const router = useRouter();

// Get poll ID from route params
const pollId = computed(() => route.params.id);

// Poll Result Resource
const pollResultResource = createResource({
    url: 'frappe.client.get',
    auto: false,
});

// Computed data
const pollResult = computed(() => pollResultResource.data);

const winningOption = computed(() => {
    if (!pollResult.value?.options?.length) return null;
    return pollResult.value.options.reduce((prev, current) =>
        prev.vote_count > current.vote_count ? prev : current
    );
});

// Load poll results on mount
onMounted(() => {
    if (pollId.value) {
        pollResultResource.submit({
            doctype: 'Poll Result',
            name: pollId.value
        });
    }
});

// Helper functions
const goBack = () => {
    router.push('/polls');
};

const getBarColor = (index) => {
    const colors = [
        'bg-blue-500',
        'bg-green-500', 
        'bg-yellow-500',
        'bg-purple-500',
        'bg-red-500',
        'bg-indigo-500',
        'bg-pink-500',
        'bg-gray-500'
    ];
    return colors[index % colors.length];
};

const getSecondHighest = () => {
    if (!pollResult.value?.options?.length) return null;
    const sorted = [...pollResult.value.options].sort((a, b) => b.vote_count - a.vote_count);
    return sorted[1] || null;
};
</script>
