import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/",
		name: "Home",
		component: () => import("@/pages/Home.vue"),
		redirect: { name: "PollsListPage" },
	},
	{
		name: "Login",
		path: "/account/login",
		component: () => import("@/pages/Login.vue"),
	},
	{
		path: "/polls",
		name: "PollsListPage",
		component: () => import("@/pages/Polls.vue"),
	},
	{
		path: "/polls/:id/results",
		name: "PollResults",
		component: () => import("@/pages/PollResults.vue"),
		props: true,
	},
]

const router = createRouter({
	history: createWebHistory("/frontend"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	let isLoggedIn = session.isLoggedIn
	try {
		await userResource.promise
	} catch (error) {
		isLoggedIn = false
	}

	if (to.name === "Login" && isLoggedIn) {
		next({ name: "Home" })
	} else if (to.name !== "Login" && !isLoggedIn) {
		next({ name: "Login" })
	} else {
		next()
	}
})

export default router
