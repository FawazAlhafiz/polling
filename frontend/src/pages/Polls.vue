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

        <!-- Voting Dialog -->
        <Dialog v-model="showVotingDialog">
            <template #body-title>
                <h3 class="text-xl font-semibold text-blue-600">
                    🗳️ Vote on Poll
                </h3>
            </template>
            
            <template #body-content>
                <div v-if="selectedPoll" class="space-y-6">
                    <!-- Poll Info -->
                    <div class="border-b border-gray-200 pb-4">
                        <h4 class="text-lg font-semibold text-gray-900 mb-2">
                            {{ selectedPoll.title }}
                        </h4>
                        <p v-if="selectedPoll.description" class="text-gray-600 text-sm">
                            {{ selectedPoll.description }}
                        </p>
                    </div>

                    <!-- Loading Poll Options -->
                    <div v-if="pollDetailResource.loading" class="text-center py-8">
                        <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                        <p class="mt-2 text-gray-600">Loading poll options...</p>
                    </div>

                    <!-- Poll Options -->
                    <div v-else-if="pollOptions.length" class="space-y-3">
                        <h4 class="font-medium text-gray-900 mb-3">Select your choice:</h4>
                        <div class="space-y-2">
                            <label 
                                v-for="option in pollOptions" 
                                :key="option.name || option.option_text"
                                class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                                :class="{ 'border-blue-500 bg-blue-50': selectedOption === option.option_text }"
                            >
                                <input 
                                    type="radio" 
                                    :value="option.option_text" 
                                    v-model="selectedOption"
                                    class="mr-3 text-blue-600 focus:ring-blue-500"
                                >
                                <div class="flex-1">
                                    <div class="font-medium text-gray-900">{{ option.option_text }}</div>
                                    <div v-if="option.description" class="text-sm text-gray-600 mt-1">
                                        {{ option.description }}
                                    </div>
                                </div>
                            </label>
                        </div>
                    </div>

                    <!-- No Options -->
                    <div v-else class="text-center py-8">
                        <div class="text-4xl mb-2">❌</div>
                        <p class="text-gray-600">No options available for this poll.</p>
                    </div>
                </div>
            </template>
            
            <template #actions="{ close }">
                <div class="flex justify-start flex-row-reverse gap-2">
                    <Button 
                        variant="solid"
                        @click="submitVote"
                        :disabled="!selectedOption || submittingVote"
                    >
                        <span v-if="submittingVote">Submitting...</span>
                        <span v-else>🗳️ Submit Vote</span>
                    </Button>
                    <Button 
                        variant="outline"
                        @click="close"
                    >
                        Cancel
                    </Button>
                </div>
            </template>
        </Dialog>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { createListResource, createResource, Dialog, Button } from 'frappe-ui';

// Function to get current user from cookies (HRMS approach)
function sessionUser() {
    let cookies = new URLSearchParams(document.cookie.split("; ").join("&"));

    return cookies.get("user_id");
}

const pollsResource = createListResource({
    doctype: 'Poll',
    fields: ['name', 'title', 'description', 'start_date', 'end_date', 'status'],
    auto: true,
});

const pollsList = computed(() => pollsResource.list.data || []);

// Voting Dialog State
const showVotingDialog = ref(false);
const selectedPoll = ref(null);
const selectedOption = ref('');
const submittingVote = ref(false);

// Poll Detail Resource (to get poll with options)
const pollDetailResource = createResource({
    url: 'frappe.client.get',
    auto: false,
});

const pollOptions = computed(() => {
    if (selectedPoll.value && selectedPoll.value.options) {
        return selectedPoll.value.options || [];
    }
    return [];
});

// Vote Submission Resource
const voteResource = createResource({
    url: 'frappe.client.insert',
    auto: false,
});

// Submit Vote Resource (to change status from Draft to Submitted)
const submitVoteResource = createResource({
    url: 'frappe.client.submit',
    auto: false,
});

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

// Voting Functions
const participateInPoll = async (poll) => {
    selectedOption.value = '';
    showVotingDialog.value = true;
    
    // Load full poll document with options
    try {
        const pollData = await pollDetailResource.submit({
            doctype: 'Poll',
            name: poll.name
        });
        selectedPoll.value = pollData;
    } catch (error) {
        console.error('Error loading poll details:', error);
        alert('Error loading poll details. Please try again.');
        closeVotingDialog();
    }
};

const closeVotingDialog = () => {
    showVotingDialog.value = false;
    selectedPoll.value = null;
    selectedOption.value = '';
    submittingVote.value = false;
};

const submitVote = async () => {
    if (!selectedOption.value || !selectedPoll.value) return;
    
    submittingVote.value = true;
    
    try {
        // Step 1: Insert the document (creates it in Draft status)
        const insertedVote = await voteResource.submit({
            doc: {
                doctype: 'Poll Vote',
                poll: selectedPoll.value.name,
                option: selectedOption.value, // This should be the option text or identifier
                voter: sessionUser(), // Current logged-in user
            }
        });
        
        // Step 2: Submit the document (changes status from Draft to Submitted)
        await submitVoteResource.submit({
            doc: insertedVote
        });
        
        // Show success message
        alert(`✅ Your vote has been submitted successfully!`);
        
        // Close dialog and cleanup
        showVotingDialog.value = false;
        selectedPoll.value = null;
        selectedOption.value = '';
        
        // Optionally refresh the polls list
        refreshPolls();
        
    } catch (error) {
        // Extract clean error message from error.exc
        let readableMessage = '';
        
        if (error?.exc) {
            // error.exc contains the full exception traceback
            // We want to get the second last line which contains the actual error message
            const excLines = error.exc.split('\n');
            const rawErrorMessage = excLines[excLines.length - 2].trim();
            
            // Extract message after the colon in patterns like:
            // "frappe.exceptions.ValidationError: You have already voted in this poll."
            if (rawErrorMessage.includes(':')) {
                readableMessage = rawErrorMessage.split(':').slice(1).join(':').trim();
            } else {
                readableMessage = rawErrorMessage;
            }
        }
        
        // Map specific poll validation errors to user-friendly messages
        let userFriendlyMessage = readableMessage || 'Error submitting vote. Please try again.';
        
        alert(`❌ ${userFriendlyMessage}`);
    } finally {
        submittingVote.value = false;
    }
};

const viewResults = (poll) => {
    // Navigate to poll results page
    console.log('Viewing results for poll:', poll.name);
    alert(`Viewing results for: ${poll.title}`);
    // You can implement navigation logic here
};
</script>