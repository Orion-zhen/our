<script lang="ts">
	import { onMount } from 'svelte';
	import gsap from 'gsap';

	let { children, strength = 0.5 } = $props();
	let element: HTMLDivElement;
	let boundingRect: DOMRect;

	onMount(() => {
		const handleMouseMove = (e: MouseEvent) => {
			if (!element) return;
			boundingRect = element.getBoundingClientRect();

			const x = e.clientX - boundingRect.left - boundingRect.width / 2;
			const y = e.clientY - boundingRect.top - boundingRect.height / 2;

			gsap.to(element, {
				x: x * strength,
				y: y * strength,
				duration: 0.4,
				ease: 'power3.out'
			});
		};

		const handleMouseLeave = () => {
			gsap.to(element, {
				x: 0,
				y: 0,
				duration: 0.7,
				ease: 'elastic.out(1, 0.3)'
			});
		};

		element.addEventListener('mousemove', handleMouseMove);
		element.addEventListener('mouseleave', handleMouseLeave);

		return () => {
			if (element) {
				element.removeEventListener('mousemove', handleMouseMove);
				element.removeEventListener('mouseleave', handleMouseLeave);
			}
		};
	});
</script>

<div bind:this={element} class="inline-block cursor-pointer">
	{@render children()}
</div>
