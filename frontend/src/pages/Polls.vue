<template>
    <div class="max-w-6xl mx-auto p-6">
        <!-- Header -->
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-800 mb-2">📝 Polls</h1>
            <p class="text-gray-600">View and participate in available polls</p>
        </div>

        <!-- Loading State -->
        <div v-if="pollsResource.loading" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-4 text-gray-600">Loading polls...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="!pollsList.length" class="text-center py-12">
            <div class="text-6xl mb-4">📋</div>
            <h3 class="text-xl font-semibold text-gray-700 mb-2">No polls available</h3>
            <p class="text-gray-500">Check back later for new polls to participate in.</p>
        </div>

        <!-- Polls List -->
        <div v-else class="space-y-4">
            <div
                v-for="poll in pollsList"
                :key="poll.name"
                class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
                <!-- Poll Header -->
                <div class="flex justify-between items-start mb-4">
                    <div class="flex-1">
                        <h3 class="text-lg font-semibold text-gray-800 mb-2">
                            {{ poll.title }}
                        </h3>
                        <p v-if="poll.description" class="text-gray-600 text-sm">
                            {{ poll.description }}
                        </p>
                    </div>
                    <span 
                        class="px-3 py-1 text-xs font-medium rounded-full"
                        :class="getStatusColor(poll)"
                    >
                        {{ getPollStatus(poll) }}
                    </span>
                </div>

                <!-- Poll Dates -->
                <div class="flex flex-wrap gap-4 mb-4 text-sm text-gray-500">
                    <div v-if="poll.start_date" class="flex items-center">
                        <span class="mr-1">📅</span>
                        <span>Starts: {{ formatDate(poll.start_date) }}</span>
                    </div>
                    <div v-if="poll.end_date" class="flex items-center">
                        <span class="mr-1">⏰</span>
                        <span>Ends: {{ formatDate(poll.end_date) }}</span>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="flex gap-3">
                    <button
                        v-if="canParticipate(poll)"
                        @click="participateInPoll(poll)"
                        class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                    >
                        🗳️ Vote Now
                    </button>
                    <button
                        @click="viewResults(poll)"
                        class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50 transition-colors"
                    >
                        📊 View Results
                    </button>
                </div>
            </div>
        </div>

        <!-- Refresh Button -->
        <div class="mt-8 text-center" v-if="pollsList.length > 0">
            <button
                @click="refreshPolls"
                class="px-6 py-2 border border-gray-300 text-gray-700 font-medium rounded-md hover:bg-gray-50 transition-colors"
            >
                🔄 Refresh Polls
            </button>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { createListResource } from 'frappe-ui';

const pollsResource = createListResource({
    doctype: 'Poll',
    fields: ['name', 'title', 'description', 'start_date', 'end_date', 'status'],
    auto: true,
});

const pollsList = computed(() => pollsResource.list.data || []);

// Utility functions
const refreshPolls = () => {
    pollsResource.reload();
};

const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });
};

const getPollStatus = (poll) => {
    const now = new Date();
    const startDate = poll.start_date ? new Date(poll.start_date) : null;
    const endDate = poll.end_date ? new Date(poll.end_date) : null;
    
    if (endDate && now > endDate) {
        return 'Ended';
    } else if (startDate && now < startDate) {
        return 'Upcoming';
    } else {
        return 'Active';
    }
};

const getStatusColor = (poll) => {
    const status = getPollStatus(poll);
    switch (status) {
        case 'Active':
            return 'bg-green-100 text-green-800';
        case 'Upcoming':
            return 'bg-blue-100 text-blue-800';
        case 'Ended':
            return 'bg-gray-100 text-gray-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
};

const canParticipate = (poll) => {
    const now = new Date();
    const startDate = poll.start_date ? new Date(poll.start_date) : null;
    const endDate = poll.end_date ? new Date(poll.end_date) : null;
    
    // Can participate if poll is active (started but not ended)
    const hasStarted = !startDate || now >= startDate;
    const hasNotEnded = !endDate || now <= endDate;
    
    return hasStarted && hasNotEnded;
};

const participateInPoll = (poll) => {
    // Navigate to poll participation page
    console.log('Participating in poll:', poll.name);
    alert(`Participating in poll: ${poll.title}`);
    // You can implement navigation logic here
};

const viewResults = (poll) => {
    // Navigate to poll results page
    console.log('Viewing results for poll:', poll.name);
    alert(`Viewing results for: ${poll.title}`);
    // You can implement navigation logic here
};
</script>