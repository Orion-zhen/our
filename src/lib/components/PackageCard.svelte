<script lang="ts">
	const base = import.meta.env.BASE_URL.replace(/\/$/, '');

	interface Props {
		name: string;
		version: string;
		arch: string;
		size: number;
		filename: string;
		index: number;
		pkgdesc?: string;
		url?: string;
		license?: string | string[];
		installed_size?: number;
	}

	let {
		name,
		version,
		arch,
		size,
		filename,
		index,
		pkgdesc,
		url,
		license,
		installed_size
	}: Props = $props();

	// Format bytes to human readable
	function formatBytes(bytes: number, decimals = 1): { value: string; unit: string } {
		if (bytes === 0) return { value: '0', unit: 'Bytes' };
		const k = 1024;
		const sizes = ['Bytes', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		const value = parseFloat((bytes / Math.pow(k, i)).toFixed(decimals)).toString();
		return { value, unit: sizes[i] };
	}

	// Calculate color based on size (logarithmic scale)
	function getSizeColor(bytes: number): string {
		const minLog = Math.log(1000); // ~1KB
		const maxLog = Math.log(200000000); // ~200MB
		const logSize = Math.log(Math.max(bytes, 1000));
		const percent = Math.min(Math.max((logSize - minLog) / (maxLog - minLog), 0), 1);

		// Color stops: cyan -> purple -> amber
		if (percent < 0.5) {
			const t = percent * 2;
			return `hsl(${185 - t * 45}, 70%, ${45 + t * 5}%)`;
		} else {
			const t = (percent - 0.5) * 2;
			return `hsl(${140 - t * 110}, ${70 - t * 20}%, ${50 + t * 10}%)`;
		}
	}

	const formattedSize = $derived(formatBytes(size));
	const formattedInstalledSize = $derived(installed_size ? formatBytes(installed_size) : null);
	const sizeColor = $derived(getSizeColor(size));
	const downloadUrl = $derived(`${base}/x86_64/${filename}`);
	const licenseStr = $derived(Array.isArray(license) ? license.join(', ') : license);

	// 3D tilt & Spotlight tracking
	let cardElement: HTMLElement;
	let tiltX = $state(0);
	let tiltY = $state(0);
	let mouseX = $state(0);
	let mouseY = $state(0);
	let isHovering = $state(false);
	let flipped = $state(false);

	function handleMouseMove(e: MouseEvent) {
		if (!cardElement) return;
		const rect = cardElement.getBoundingClientRect();
		const x = e.clientX - rect.left;
		const y = e.clientY - rect.top;

		// Update mouse coordinates for spotlight
		mouseX = x;
		mouseY = y;

		const percentX = x / rect.width - 0.5;
		const percentY = y / rect.height - 0.5;
		tiltX = percentY * -15;
		tiltY = percentX * 15;
	}

	function handleMouseEnter() {
		isHovering = true;
	}

	function handleMouseLeave() {
		isHovering = false;
		tiltX = 0;
		tiltY = 0;
	}

	function handleCardClick(e: MouseEvent) {
		// Only flip if not clicking a link or button on the front side
		const target = e.target as HTMLElement;
		if (target.closest('.no-flip')) return;

		flipped = !flipped;
	}
</script>

<div
	class="package-card relative h-[160px]"
	style="--index: {index};"
>
	<div
		role="button"
		tabindex="0"
		bind:this={cardElement}
		onmousemove={handleMouseMove}
		onmouseenter={handleMouseEnter}
		onmouseleave={handleMouseLeave}
		onclick={handleCardClick}
		onkeydown={(e) => e.key === 'Enter' && handleCardClick(e as any)}
		class="card-stage relative h-full w-full cursor-pointer"
		style="
			--mouse-x: {mouseX}px;
			--mouse-y: {mouseY}px;
			transform: perspective(1000px) rotateX({tiltX}deg) rotateY({tiltY}deg) {isHovering
			? 'translateY(-5px) scale(1.02)'
			: ''};
			transition: {isHovering
			? 'box-shadow 0.3s, border-color 0.3s'
			: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)'};
			transform-style: preserve-3d;
		"
	>
		<div
			class="card-inner {flipped ? 'is-flipped' : ''}"
			style="transform: rotateY({flipped ? 180 : 0}deg);"
		>
			<!-- Back Face (Initial view - Original Layout) -->
			<div class="card-face card-back glass-card flex flex-col justify-between p-5">
				<div
					class="package-name relative z-20 text-lg leading-tight font-semibold break-all text-[var(--color-text-primary)]"
				>
					{name}
				</div>

				<div class="relative z-20 flex items-end justify-between">
					<div class="text-sm text-[var(--color-text-secondary)]">
						<div class="font-medium">{version}</div>
						<div class="text-xs text-[var(--color-text-muted)]">arch: {arch}</div>
					</div>

					<div
						class="rounded-md px-3 py-1 font-mono text-sm font-medium shadow-lg"
						style="background-color: {sizeColor}; color: #0a0a0f;"
					>
						{formattedSize.value}
						{formattedSize.unit}
					</div>
				</div>
			</div>

			<!-- Front Face (Rotated 180, Info Detail) -->
			<div
				class="card-face card-front glass-card flex flex-col justify-between p-4 outline-1 -outline-offset-1 outline-[var(--color-border)]"
			>
				<div class="scrollbar-hide overflow-y-auto pr-1 text-[11px] leading-relaxed">
					{#if pkgdesc}
						<p class="mb-2 line-clamp-2 font-medium text-[var(--color-text-primary)]" title={pkgdesc}>
							{pkgdesc}
						</p>
					{/if}

					<div class="mt-1 grid grid-cols-[max-content_1fr] gap-x-3 gap-y-1 text-[var(--color-text-muted)]">
						{#if licenseStr}
							<span class="opacity-70">License:</span>
							<span class="truncate text-[var(--color-text-secondary)] font-medium">{licenseStr}</span>
						{/if}
						{#if formattedInstalledSize}
							<span class="opacity-70">Installed:</span>
							<span class="text-[var(--color-text-secondary)] font-medium"
								>{formattedInstalledSize.value} {formattedInstalledSize.unit}</span
							>
						{/if}
						{#if url}
							<span class="opacity-70">Project:</span>
							<a
								href={url}
								target="_blank"
								rel="noopener noreferrer"
								class="no-flip truncate text-[var(--color-accent)] font-medium hover:underline"
							>
								{url.replace(/^https?:\/\//, '')}
							</a>
						{/if}
					</div>
				</div>

				<a
					href={downloadUrl}
					title="Download Package"
					class="no-flip absolute bottom-3 right-3 flex h-9 w-9 items-center justify-center rounded-full border border-white/10 bg-white/5 text-[var(--color-text-secondary)] shadow-lg backdrop-blur-md transition-all duration-300 ease-out hover:scale-110 hover:border-white/20 hover:bg-white/10 hover:text-[var(--color-text-primary)]"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="16"
						height="16"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="3"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
						<polyline points="7 10 12 15 17 10"></polyline>
						<line x1="12" y1="15" x2="12" y2="3"></line>
					</svg>
				</a>
			</div>
		</div>
	</div>
</div>

<style>
	.package-card {
		perspective: 1000px;
		/* Base GSAP target must be transparent and non-visual to avoid "ghosting" with the interactive layers */
		background: transparent !important;
		border: none !important;
		box-shadow: none !important;
		pointer-events: none; /* Let events pass to the stage */
	}

	.card-stage {
		pointer-events: auto; /* Re-enable events for interaction */
	}

	.package-card,
	.card-stage,
	.card-inner,
	.card-face {
		border-radius: 16px !important;
	}

	.card-inner {
		position: relative;
		width: 100%;
		height: 100%;
		transform-style: preserve-3d;
		transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
	}

	.card-face {
		position: absolute;
		inset: 0;
		backface-visibility: hidden;
		overflow: hidden;
		/* Force hardware acceleration for backdrop-filter stability */
		transform: translateZ(0);
	}

	.card-front {
		transform: rotateY(180deg) translateZ(0);
	}

	.card-back {
		transform: rotateY(0deg) translateZ(0);
	}

	/* Spotlight Effect */
	.card-face::before {
		content: '';
		position: absolute;
		inset: 0;
		background: radial-gradient(
			400px circle at var(--mouse-x) var(--mouse-y),
			rgba(255, 255, 255, 0.12),
			transparent 60%
		);
		pointer-events: none;
		opacity: 0;
		transition: opacity 0.5s;
		z-index: 10;
		border-radius: inherit;
	}

	.card-stage:hover .card-face::before {
		opacity: 1;
	}

	/* Mouse-following Border Effect */
	.card-face::after {
		content: '';
		position: absolute;
		inset: -1.5px;
		padding: 1.5px;
		background: radial-gradient(
			250px circle at var(--mouse-x) var(--mouse-y),
			var(--color-accent),
			#8866ff 40%,
			transparent 80%
		);
		border-radius: inherit;
		-webkit-mask:
			linear-gradient(#fff 0 0) content-box,
			linear-gradient(#fff 0 0);
		mask:
			linear-gradient(#fff 0 0) content-box,
			linear-gradient(#fff 0 0);
		mask-composite: exclude;
		-webkit-mask-composite: destination-out;
		opacity: 0;
		transition: opacity 0.4s ease;
		pointer-events: none;
		z-index: 5;
	}

	.card-stage:hover .card-face::after {
		opacity: 1;
	}
</style>

