<script lang="ts">
	import { onMount } from 'svelte';

	let canvas: HTMLCanvasElement;
	let ctx: CanvasRenderingContext2D | null;
	let width: number;
	let height: number;
	let particles: Particle[] = [];
	let mouse = { x: 0, y: 0 };

	// Configuration
	const particleCount = 60;
	const connectionDistance = 150;
	const mouseDistance = 200;

	class Particle {
		x: number;
		y: number;
		vx: number;
		vy: number;
		size: number;
		alpha: number;

		constructor() {
			this.x = Math.random() * width;
			this.y = Math.random() * height;
			this.vx = (Math.random() - 0.5) * 0.5;
			this.vy = (Math.random() - 0.5) * 0.5;
			this.size = Math.random() * 2 + 1;
			this.alpha = Math.random() * 0.5 + 0.2; // Initial alpha
		}

		update() {
			this.x += this.vx;
			this.y += this.vy;

			// Bounce off edges
			if (this.x < 0 || this.x > width) this.vx *= -1;
			if (this.y < 0 || this.y > height) this.vy *= -1;

			// Mouse interaction
			const dx = mouse.x - this.x;
			const dy = mouse.y - this.y;
			const distance = Math.sqrt(dx * dx + dy * dy);

			if (distance < mouseDistance) {
				const forceDirectionX = dx / distance;
				const forceDirectionY = dy / distance;
				const force = (mouseDistance - distance) / mouseDistance;
				const directionX = forceDirectionX * force * 0.5; // Push away slightly or pull? Let's pull slightly
				const directionY = forceDirectionY * force * 0.5;
				
                // Gentle attraction to mouse
				this.vx += directionX * 0.05;
				this.vy += directionY * 0.05;
			}
            
            // Limit speed
            const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
            if (speed > 1) {
                this.vx = (this.vx / speed);
                this.vy = (this.vy / speed);
            }
		}

		draw() {
			if (!ctx) return;
			ctx.beginPath();
			ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
			ctx.fillStyle = `rgba(148, 163, 184, ${this.alpha})`; // Slate-400 color
			ctx.fill();
		}
	}

	function init() {
		resize();
		for (let i = 0; i < particleCount; i++) {
			particles.push(new Particle());
		}
		animate();
	}

	function resize() {
		width = window.innerWidth;
		height = window.innerHeight;
		canvas.width = width;
		canvas.height = height;
	}

	function animate() {
		if (!ctx) return;
		ctx.clearRect(0, 0, width, height);

		particles.forEach((particle, index) => {
			particle.update();
			particle.draw();

			// Connect particles
			for (let j = index + 1; j < particles.length; j++) {
				const dx = particle.x - particles[j].x;
				const dy = particle.y - particles[j].y;
				const distance = Math.sqrt(dx * dx + dy * dy);

				if (distance < connectionDistance) {
					ctx!.beginPath();
					ctx!.strokeStyle = `rgba(148, 163, 184, ${0.15 * (1 - distance / connectionDistance)})`;
					ctx!.lineWidth = 1;
					ctx!.moveTo(particle.x, particle.y);
					ctx!.lineTo(particles[j].x, particles[j].y);
					ctx!.stroke();
				}
			}
            
            // Connect to mouse
            const dx = particle.x - mouse.x;
            const dy = particle.y - mouse.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
             if (distance < mouseDistance) {
                ctx!.beginPath();
                ctx!.strokeStyle = `rgba(6, 182, 212, ${0.2 * (1 - distance / mouseDistance)})`; // Cyan accent
                ctx!.lineWidth = 1;
                ctx!.moveTo(particle.x, particle.y);
                ctx!.lineTo(mouse.x, mouse.y);
                ctx!.stroke();
            }
		});

		requestAnimationFrame(animate);
	}

	onMount(() => {
		ctx = canvas.getContext('2d');
		init();

		window.addEventListener('resize', resize);
        
        const handleMouseMove = (e: MouseEvent) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        };
		window.addEventListener('mousemove', handleMouseMove);

		return () => {
			window.removeEventListener('resize', resize);
            window.removeEventListener('mousemove', handleMouseMove);
		};
	});
</script>

<canvas bind:this={canvas} class="pointer-events-none fixed inset-0 z-0 opacity-40"></canvas>

<style>
    /* No extra styles needed via CSS, handled in canvas */
</style>
