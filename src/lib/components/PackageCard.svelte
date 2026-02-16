<script lang="ts">
	const base = import.meta.env.BASE_URL.replace(/\/$/, '');

	interface Props {
		name: string;
		version: string;
		arch: string;
		size: number;
		filename: string;
		index: number;
	}

	let { name, version, arch, size, filename, index }: Props = $props();

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
	const sizeColor = $derived(getSizeColor(size));
	const downloadUrl = $derived(`${base}/x86_64/${filename}`);

	// 3D tilt & Spotlight tracking
	let cardElement: HTMLElement;
	let tiltX = $state(0);
	let tiltY = $state(0);
	let mouseX = $state(0);
	let mouseY = $state(0);
	let isHovering = $state(false);

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
</script>

<a
	href={downloadUrl}
	bind:this={cardElement}
	onmousemove={handleMouseMove}
	onmouseenter={handleMouseEnter}
	onmouseleave={handleMouseLeave}
	class="package-card glass-card relative block flex h-[160px] cursor-pointer flex-col justify-between p-5 no-underline"
	style="
		--index: {index};
		--mouse-x: {mouseX}px;
		--mouse-y: {mouseY}px;
		transform: perspective(1000px) rotateX({tiltX}deg) rotateY({tiltY}deg) {isHovering
		? 'translateY(-5px) scale(1.02)'
		: ''};
		transition: {isHovering
		? 'box-shadow 0.3s, border-color 0.3s'
		: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)'};
	"
>
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
</a>

<style>
	.package-card {
		transform-style: preserve-3d;
		/* Ensure border-color doesn't conflict during hover flow */
		border-color: var(--glass-border);
	}

	/* Spotlight Effect - Clips inside the border radius automatically */
	.package-card::before {
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

	.package-card:hover::before {
		opacity: 1;
	}

	/* Mouse-following Border Effect */
	.package-card::after {
		content: '';
		position: absolute;
		inset: -1.5px; /* Slightly larger to fully define the border area */
		padding: 1.5px; /* Border thickness */
		background: radial-gradient(
			250px circle at var(--mouse-x) var(--mouse-y),
			var(--color-accent),
			#8866ff 40%,
			transparent 80%
		);
		border-radius: inherit;
		/* Masking: only reveal the padding area (the border) */
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

	.package-card:hover::after {
		opacity: 1;
	}
</style>
