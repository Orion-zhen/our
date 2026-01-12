<script lang="ts">
	import './layout.css';
	import { onMount } from 'svelte';
	const base = import.meta.env.BASE_URL.replace(/\/$/, '');
	import Lenis from '@studio-freight/lenis';

	let { children } = $props();

	onMount(() => {
		// Initialize Lenis smooth scroll
		const lenis = new Lenis({
			duration: 1.2,
			easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
			orientation: 'vertical',
			smoothWheel: true
		});

		function raf(time: number) {
			lenis.raf(time);
			requestAnimationFrame(raf);
		}

		requestAnimationFrame(raf);

		return () => {
			lenis.destroy();
		};
	});
</script>

<svelte:head>
	<title>OUR - Orion User's Repository</title>
	<meta
		name="description"
		content="Orion User's Repository for Arch Linux - A personal software repository with useful AUR packages"
	/>
	<meta name="keywords" content="archlinux, repository, aur, packages, pacman" />
	<meta name="author" content="Orion-zhen" />
	<link rel="icon" href="{base}/favicon.svg" type="image/svg+xml" />
</svelte:head>

<div class="gradient-bg relative min-h-screen overflow-hidden">
	<!-- Decorative floating orbs -->
	<div class="orb orb-cyan fixed -top-48 -left-48 h-[500px] w-[500px]"></div>
	<div class="orb orb-purple fixed top-1/2 -right-32 h-[400px] w-[400px]"></div>
	<div class="orb orb-cyan fixed bottom-20 left-1/4 h-[300px] w-[300px] opacity-30"></div>

	{@render children()}
</div>
