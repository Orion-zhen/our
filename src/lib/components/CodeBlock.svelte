<script lang="ts">
	interface Props {
		code: string;
		language?: string;
	}

	let { code, language = 'shell' }: Props = $props();

	let copied = $state(false);
	let copyTimeout: ReturnType<typeof setTimeout>;

	async function copyToClipboard() {
		try {
			await navigator.clipboard.writeText(code);
			copied = true;
			clearTimeout(copyTimeout);
			copyTimeout = setTimeout(() => {
				copied = false;
			}, 2000);
		} catch (err) {
			console.error('Failed to copy:', err);
		}
	}

	// Simple syntax highlighting
	function highlightCode(text: string, lang: string): string {
		if (lang === 'shell' || lang === 'bash') {
			return text
				.split('\n')
				.map((line) => {
					// Comments
					if (line.trim().startsWith('#')) {
						return `<span class="hl-comment">${escapeHtml(line)}</span>`;
					}
					// Commands at start
					let result = line;
					// Highlight sudo, tee, pacman, etc.
					result = result.replace(
						/^(\s*)(sudo|tee|pacman|echo|cat|EOF)(\s)/g,
						'$1<span class="hl-command">$2</span>$3'
					);
					// Highlight flags
					result = result.replace(/(\s)(--?\w+)/g, '$1<span class="hl-flag">$2</span>');
					// Highlight URLs
					result = result.replace(/(https?:\/\/[^\s<]+)/g, '<span class="hl-string">$1</span>');
					// Highlight paths
					result = result.replace(/(\s)(\/[\w\/.${}-]+)/g, '$1<span class="hl-path">$2</span>');
					return result;
				})
				.join('\n');
		}

		if (lang === 'ini' || lang === 'conf') {
			return text
				.split('\n')
				.map((line) => {
					// Comments
					if (line.trim().startsWith('#')) {
						return `<span class="hl-comment">${escapeHtml(line)}</span>`;
					}
					// Section headers [section]
					if (/^\[.+\]$/.test(line.trim())) {
						return `<span class="hl-section">${escapeHtml(line)}</span>`;
					}
					// Key = Value
					const match = line.match(/^(\s*)(\w+)(\s*=\s*)(.*)$/);
					if (match) {
						return `${match[1]}<span class="hl-key">${match[2]}</span>${match[3]}<span class="hl-value">${escapeHtml(match[4])}</span>`;
					}
					// URLs
					let result = escapeHtml(line);
					result = result.replace(/(https?:\/\/[^\s]+)/g, '<span class="hl-string">$1</span>');
					return result;
				})
				.join('\n');
		}

		return escapeHtml(text);
	}

	function escapeHtml(text: string): string {
		return text
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;');
	}

	const highlightedCode = $derived(highlightCode(code, language));
</script>

<div class="code-block">
	<div class="code-header">
		<span class="code-language">{language}</span>
		<button class="copy-button" onclick={copyToClipboard} aria-label="Copy code">
			{#if copied}
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="16"
					height="16"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				>
					<polyline points="20 6 9 17 4 12"></polyline>
				</svg>
				<span>Copied!</span>
			{:else}
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="16"
					height="16"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				>
					<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
					<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
				</svg>
				<span>Copy</span>
			{/if}
		</button>
	</div>
	<pre class="code-content"><code>{@html highlightedCode}</code></pre>
</div>

<style>
	.code-block {
		position: relative;
		border-radius: 12px;
		overflow: hidden;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		transition: border-color 0.3s ease;
	}

	.code-block:hover {
		border-color: var(--color-border-hover);
	}

	.code-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.75rem 1rem;
		background: rgba(255, 255, 255, 0.03);
		border-bottom: 1px solid var(--color-border);
	}

	.code-language {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
	}

	.copy-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.4rem 0.75rem;
		font-size: 0.75rem;
		font-family: var(--font-sans);
		color: var(--color-text-secondary);
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid var(--color-border);
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.copy-button:hover {
		background: rgba(255, 255, 255, 0.1);
		color: var(--color-text-primary);
		border-color: var(--color-accent);
	}

	.copy-button svg {
		flex-shrink: 0;
	}

	.code-content {
		margin: 0;
		padding: 1.25rem 1.5rem;
		overflow-x: auto;
		background: transparent !important;
		border: none !important;
		border-radius: 0 !important;
	}

	.code-content code {
		font-family: var(--font-mono);
		font-size: 0.875rem;
		line-height: 1.6;
		color: var(--color-text-primary);
	}

	/* Syntax highlighting colors */
	:global(.hl-comment) {
		color: #6a737d;
		font-style: italic;
	}

	:global(.hl-command) {
		color: #f97316;
		font-weight: 500;
	}

	:global(.hl-flag) {
		color: #a78bfa;
	}

	:global(.hl-string) {
		color: #22d3ee;
	}

	:global(.hl-path) {
		color: #4ade80;
	}

	:global(.hl-section) {
		color: #f472b6;
		font-weight: 600;
	}

	:global(.hl-key) {
		color: #60a5fa;
	}

	:global(.hl-value) {
		color: #fbbf24;
	}
</style>
