<script lang="ts">
	import { onMount } from 'svelte';

	interface Props {
		text: string;
		speed?: number;
		delay?: number;
		class?: string;
	}

	let { text, speed = 80, delay = 300, class: className = '' }: Props = $props();

	let displayedText = $state('');
	let showCursor = $state(true);
	let isComplete = $state(false);

	onMount(() => {
		let currentIndex = 0;

		// Start typing after delay
		const startTimeout = setTimeout(() => {
			const typingInterval = setInterval(() => {
				if (currentIndex < text.length) {
					displayedText = text.slice(0, currentIndex + 1);
					currentIndex++;
				} else {
					clearInterval(typingInterval);
					isComplete = true;
					// Keep cursor blinking for a moment, then hide
					setTimeout(() => {
						showCursor = false;
					}, 2000);
				}
			}, speed);

			return () => clearInterval(typingInterval);
		}, delay);

		// Cursor blink effect
		const cursorInterval = setInterval(() => {
			if (!isComplete) {
				showCursor = !showCursor;
			}
		}, 530);

		return () => {
			clearTimeout(startTimeout);
			clearInterval(cursorInterval);
		};
	});
</script>

<span class="typewriter {className}" class:complete={isComplete}>
	<span class="typewriter-text">{displayedText}</span>
	{#if showCursor || !isComplete}
		<span class="typewriter-cursor" class:blinking={!isComplete}>|</span>
	{/if}
</span>

<style>
	.typewriter {
		display: inline;
	}

	.typewriter-text {
		background: linear-gradient(
			135deg,
			var(--color-text-primary) 0%,
			var(--color-accent) 50%,
			var(--color-text-primary) 100%
		);
		background-size: 200% auto;
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		transition: background-position 0.5s ease;
	}

	.typewriter:hover .typewriter-text {
		background-position: right center;
		animation: shimmer 2s linear infinite;
	}

	@keyframes shimmer {
		0% {
			background-position: 0% 50%;
		}
		100% {
			background-position: 100% 50%;
		}
	}

	.typewriter-cursor {
		display: inline-block;
		margin-left: 2px;
		font-weight: 300;
		color: var(--color-accent);
	}

	.typewriter-cursor.blinking {
		animation: blink 1s step-end infinite;
	}

	@keyframes blink {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0;
		}
	}

	.typewriter.complete .typewriter-cursor {
		animation: fade-out 0.5s ease-out forwards;
	}

	@keyframes fade-out {
		to {
			opacity: 0;
		}
	}
</style>
