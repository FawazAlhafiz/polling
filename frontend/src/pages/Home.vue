<template>
  <h1>Polling</h1>
</template>

<script setup>
import { Dialog } from "frappe-ui"
import { createResource } from "frappe-ui"
import { ref } from "vue"
import { session } from "../data/session"

const ping = createResource({
	url: "ping",
	auto: true,
})

const showDialog = ref(false)
</script>
