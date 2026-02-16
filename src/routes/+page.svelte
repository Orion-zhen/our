<script lang="ts">
	import { onMount, tick } from 'svelte';
	const base = import.meta.env.BASE_URL.replace(/\/$/, '');
	import gsap from 'gsap';
	import { ScrollTrigger } from 'gsap/ScrollTrigger';
	import Header from '$lib/components/Header.svelte';
	import PackageCard from '$lib/components/PackageCard.svelte';
	import Typewriter from '$lib/components/Typewriter.svelte';
	import CodeBlock from '$lib/components/CodeBlock.svelte';

	gsap.registerPlugin(ScrollTrigger);

	interface Package {
		name: string;
		version: string;
		arch: string;
		size: number;
		filename: string;
	}

	let packages = $state<Package[]>([]);
	let loading = $state(true);

	// Code snippets
	const pacmanConfCode = `[our]
# Uncomment this if you encounter GPG key error
# SigLevel = Optional TrustAll
Server = https://orion-zhen.github.io/our/$arch`;

	const appendConfCode = `sudo tee -a /etc/pacman.conf << EOF

[our]
# Uncomment this if you encounter GPG key error
# SigLevel = Optional TrustAll
Server = https://orion-zhen.github.io/our/\\$arch
EOF`;

	const syncCode = `sudo pacman -Syu`;

	onMount(async () => {
		// Load packages
		try {
			const res = await fetch(`${base}/packages.json`);
			packages = await res.json();
		} catch (e) {
			console.error('Failed to load packages:', e);
		} finally {
			loading = false;
		}

		// GSAP animations
		// Hero subtitle animation (title uses Typewriter)
		gsap.from('.hero-subtitle', {
			y: 40,
			opacity: 0,
			duration: 1,
			delay: 1.5,
			ease: 'power3.out'
		});

		// Section fade-in animations
		gsap.utils.toArray<HTMLElement>('.section-animate').forEach((section) => {
			gsap.from(section, {
				y: 50,
				opacity: 0,
				duration: 0.8,
				ease: 'power2.out',
				scrollTrigger: {
					trigger: section,
					start: 'top 85%',
					toggleActions: 'play none none none'
				}
			});
		});

		// Packages section title animation
		gsap.from('.packages-title', {
			y: 50,
			opacity: 0,
			duration: 0.8,
			ease: 'power2.out',
			scrollTrigger: {
				trigger: '.packages-section',
				start: 'top 85%'
			}
		});

		// Code blocks reveal
		gsap.utils.toArray<HTMLElement>('.code-block').forEach((block) => {
			gsap.from(block, {
				scale: 0.95,
				opacity: 0,
				duration: 0.6,
				ease: 'power2.out',
				scrollTrigger: {
					trigger: block,
					start: 'top 85%'
				}
			});
		});

		// Wait for DOM to update with packages, then setup card animation
		await tick();
		setupCardAnimation();
	});

	function setupCardAnimation() {
		const cards = gsap.utils.toArray<HTMLElement>('.package-card');
		if (cards.length === 0) return;

		// Dynamically determine column positions by looking at actual layout
		// This makes it work perfectly on mobile (1 col), tablet (2-3 col), and desktop (4 col)
		const xPositions = cards.map((c) => c.offsetLeft);
		const uniqueX = [...new Set(xPositions)].sort((a, b) => a - b);

		cards.forEach((card) => {
			// Get the actual column index (0 to N) based on horizontal position
			const columnIndex = uniqueX.indexOf(card.offsetLeft);
			const staggerOffset = columnIndex * 3;

			// Base thresholds (Percentage from top of viewport)
			const startPoint = 92 - staggerOffset;
			const endPoint = 72 - staggerOffset;
			const pulsePoint = endPoint - 1;

			// 1. Initial hidden state
			gsap.set(card, {
				opacity: 0,
				scale: 0.85,
				y: 60,
				filter: 'blur(15px)'
			});

			// 2. Scroll-linked Reveal
			gsap.to(card, {
				opacity: 1,
				scale: 1,
				y: 0,
				filter: 'blur(0px)',
				ease: 'none',
				scrollTrigger: {
					trigger: card,
					start: `top ${startPoint}%`,
					end: `top ${endPoint}%`,
					scrub: 1.2
				}
			});

			// 3. Activation Confirmation Pulse
			ScrollTrigger.create({
				trigger: card,
				start: `top ${pulsePoint}%`,
				onEnter: () => {
					const tl = gsap.timeline();
					tl.to(card, {
						borderColor: 'rgba(6, 182, 212, 0.8)',
						boxShadow: '0 0 25px rgba(6, 182, 212, 0.5)',
						backgroundColor: 'rgba(255, 255, 255, 0.1)',
						duration: 0.15,
						ease: 'power2.out'
					}).to(card, {
						borderColor: 'var(--glass-border)',
						boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
						backgroundColor: 'var(--glass-bg)',
						duration: 0.6,
						ease: 'power1.inOut'
					});
				},
				once: true
			});
		});

		ScrollTrigger.refresh();
	}
</script>

<Header />

<main class="relative z-10">
	<!-- Hero Section -->
	<section class="flex min-h-screen items-center justify-center px-6 pt-20">
		<div class="max-w-4xl text-center">
			<h1 class="hero-title mb-6 text-5xl leading-tight font-extrabold md:text-7xl">
				<Typewriter text="Orion User's Repository" speed={60} delay={500} />
			</h1>
			<p
				class="hero-subtitle mx-auto max-w-2xl text-xl text-[var(--color-text-secondary)] md:text-2xl"
			>
				A personal software repository for Arch Linux, built with passion.
			</p>
		</div>
	</section>

	<!-- About Section -->
	<section class="section-animate px-6 py-20">
		<div class="mx-auto max-w-4xl">
			<h2 class="text-gradient mb-6 inline-block text-3xl font-bold">About This Repository</h2>
			<div class="glass-card p-8">
				<p class="text-lg leading-relaxed text-[var(--color-text-secondary)]">
					This repository includes a bunch of useful AUR packages that might not be listed in other
					popular Arch repositories, such as ags-hyprpanel-git, hyprshot-gui, clipse-git, etc. The
					repository builder is powered by GitHub Actions. It will automatically pull AUR packages,
					build them, and release to my GitHub page regularly.
				</p>
			</div>
		</div>
	</section>

	<!-- Usage Section -->
	<section class="section-animate px-6 py-20">
		<div class="mx-auto max-w-4xl">
			<h2 class="text-gradient mb-6 inline-block text-3xl font-bold">Usage</h2>
			<div class="glass-card space-y-6 p-8">
				<p class="text-[var(--color-text-secondary)]">
					Add the following to your <code>/etc/pacman.conf</code> file to enable the OUR repository:
				</p>
				<CodeBlock code={pacmanConfCode} language="ini" />

				<p class="text-[var(--color-text-secondary)]">
					Alternatively, run this command to append the configuration:
				</p>
				<CodeBlock code={appendConfCode} language="shell" />

				<p class="text-[var(--color-text-secondary)]">
					Then, refresh your package databases and synchronize:
				</p>
				<CodeBlock code={syncCode} language="shell" />

				<p class="font-medium text-[var(--color-accent)]">
					You can now install packages from the OUR repository. 🚀
				</p>
			</div>
		</div>
	</section>

	<!-- Packages Section -->
	<section class="packages-section px-6 py-20">
		<div class="mx-auto max-w-6xl">
			<h2 class="packages-title text-gradient mb-8 inline-block text-3xl font-bold">
				Available Packages
			</h2>

			{#if loading}
				<div class="glass-card p-8 text-center text-[var(--color-text-secondary)]">
					Loading packages...
				</div>
			{:else if packages.length === 0}
				<div class="glass-card p-8 text-center text-[var(--color-text-secondary)]">
					No packages found.
				</div>
			{:else}
				<div
					class="packages-container grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
				>
					{#each packages as pkg, i}
						<PackageCard
							name={pkg.name}
							version={pkg.version}
							arch={pkg.arch}
							size={pkg.size}
							filename={pkg.filename}
							index={i}
						/>
					{/each}
				</div>
			{/if}
		</div>
	</section>

	<!-- Request Section -->
	<section class="section-animate px-6 py-20">
		<div class="mx-auto max-w-4xl">
			<h2 class="text-gradient mb-6 inline-block text-3xl font-bold">Package Requests</h2>
			<div class="glass-card p-8">
				<p class="text-lg text-[var(--color-text-secondary)]">
					If you want to add a useful AUR package to this repository, you are welcome to make a
					package request by opening an issue on the
					<a
						href="https://github.com/Orion-zhen/our/issues"
						target="_blank"
						rel="noopener noreferrer"
						class="text-[var(--color-accent)] underline hover:text-[var(--color-accent-hover)]"
					>
						GitHub repository
					</a>.
				</p>
			</div>
		</div>
	</section>

	<!-- Footer -->
	<footer class="border-t border-[var(--color-border)] px-6 py-10">
		<div class="mx-auto max-w-4xl text-center text-[var(--color-text-muted)]">
			<p>
				Copyleft © 2025 Orion-zhen. Licensed under
				<a
					href="https://www.gnu.org/licenses/gpl-3.0.html"
					target="_blank"
					rel="noopener noreferrer">GPL-3.0</a
				>.
			</p>
		</div>
	</footer>
</main>
