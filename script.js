document.addEventListener('DOMContentLoaded', () => {

    // --- 1. 辅助函数 ---

    // 格式化文件大小 (无变化)
    function formatBytes(bytes, decimals = 1) {
        if (bytes === 0) return { value: '0', unit: 'Bytes' };
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        const value = parseFloat((bytes / Math.pow(k, i)).toFixed(dm));
        const unit = sizes[i];
        return { value, unit };
    }

    // NEW: 升级版颜色插值函数，支持多点渐变
    /**
     * 在一个色谱上进行插值
     * @param {number} amount - 插值量 (0.0 to 1.0)
     * @param {Array<object>} colorStops - 颜色站点数组, e.g., [{ color: '#ff0000', pos: 0 }, ...]
     * @returns {string} - 计算出的HEX颜色
     */
    function interpolateColor(amount, colorStops) {
        // 确保站点按位置排序
        colorStops.sort((a, b) => a.pos - b.pos);

        // 找到正确的颜色区间
        let startStop = colorStops[0];
        let endStop = colorStops[colorStops.length - 1];

        for (let i = 0; i < colorStops.length - 1; i++) {
            if (amount >= colorStops[i].pos && amount <= colorStops[i + 1].pos) {
                startStop = colorStops[i];
                endStop = colorStops[i + 1];
                break;
            }
        }

        // 计算在当前区间的相对位置
        const range = endStop.pos - startStop.pos;
        const relativeAmount = (range === 0) ? 0 : (amount - startStop.pos) / range;

        // --- 内部线性插值 ---
        const c1 = startStop.color;
        const c2 = endStop.color;

        const from = c1.match(/#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})/i).slice(1).map(c => parseInt(c, 16));
        const to = c2.match(/#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})/i).slice(1).map(c => parseInt(c, 16));

        const pad = (s) => (s.length === 1 ? '0' + s : s);

        const r = Math.round(from[0] + (to[0] - from[0]) * relativeAmount).toString(16);
        const g = Math.round(from[1] + (to[1] - from[1]) * relativeAmount).toString(16);
        const b = Math.round(from[2] + (to[2] - from[2]) * relativeAmount).toString(16);

        return `#${pad(r)}${pad(g)}${pad(b)}`;
    }

    // 判断文本颜色以确保可读性 (无变化)
    function getTextColorForBg(hexcolor) {
        const rgb = parseInt(hexcolor.substring(1), 16);
        const r = (rgb >> 16) & 0xff;
        const g = (rgb >> 8) & 0xff;
        const b = (rgb >> 0) & 0xff;
        const luma = 0.2126 * r + 0.7152 * g + 0.0722 * b;
        return luma < 128 ? '#f4f4f5' : '#1a1a1b';
    }


    // --- 2. 核心功能：获取并渲染软件包数据 ---
    async function loadPackages() {
        const packageListContainer = document.getElementById('package-list');
        try {
            const response = await fetch('packages.json');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const packages = await response.json();

            if (!packages || packages.length === 0) {
                packageListContainer.innerHTML = '<p class="loading-text">No packages found.</p>';
                return;
            }

            // --- 颜色计算逻辑更新 ---
            const sizes = packages.map(p => p.size).filter(s => s > 0);
            const minSize = Math.min(...sizes);
            const maxSize = Math.max(...sizes);

            const logMin = Math.log(minSize);
            const logMax = Math.log(maxSize);

            // 定义我们的新色谱
            const colorSpectrum = [
                { color: '#0c4a6e', pos: 0.0 },   // Deep Sky Blue
                { color: '#0891b2', pos: 0.25 },  // Vibrant Cyan
                { color: '#c026d3', pos: 0.75 },  // Neon Fuchsia
                { color: '#f59e0b', pos: 1.0 }    // Warm Amber
            ];


            const flyInDirections = ['from-left', 'from-right', 'from-top', 'from-bottom'];
            const packageCardsHTML = packages.map((pkg, index) => {
                const formattedSize = formatBytes(pkg.size);
                const downloadUrl = `x86_64/${pkg.filename}`;
                const randomDirection = flyInDirections[index % flyInDirections.length];
                const delay = (index % 20) * 50;

                // 计算颜色
                let bgColor = '#3f3f46';
                let textColor = '#f4f4f5';
                if (pkg.size > 0) {
                    const logSize = Math.log(pkg.size);
                    const percent = (logSize - logMin) / (logMax - logMin);
                    // 使用新的插值函数
                    bgColor = interpolateColor(isNaN(percent) ? 0 : percent, colorSpectrum);
                    textColor = getTextColorForBg(bgColor);
                }

                const styleOverride = `
                    --size-bg-color: ${bgColor};
                    --size-text-color: ${textColor};
                    transition-delay: ${delay}ms;
                `;

                return `
                    <a href="${downloadUrl}" 
                       class="package-card card-fly-in ${randomDirection}" 
                       title="Download ${pkg.name} ${pkg.version}"
                       style="${styleOverride}">
                        <div class="package-name">${pkg.name}</div>
                        <div class="package-meta">
                            <div class="package-info">
                                <span class="package-version">v${pkg.version}</span>
                                <span class="package-arch">arch: ${pkg.arch}</span>
                            </div>
                            <div class="package-size">
                                ${formattedSize.value} ${formattedSize.unit}
                            </div>
                        </div>
                    </a>
                `;
            }).join('');

            packageListContainer.innerHTML = packageCardsHTML;

        } catch (error) {
            console.error("Failed to load packages:", error);
            packageListContainer.innerHTML = '<p class="loading-text">Error loading packages. Check console.</p>';
        }
    }

    // --- 3 & 4. 动画逻辑与初始化 (无变化) ---
    // 3.1 NEW: 卡片交互效果 (浮动与3D倾斜)
    function setupInteractiveCards() {
        const cards = document.querySelectorAll('.package-card');
        const maxTilt = 12; // 最大倾斜角度

        cards.forEach(card => {
            card.addEventListener('mouseenter', (e) => {
                // 鼠标进入时，立刻添加 is-interacting 类，禁用 transform 过渡
                card.classList.add('is-interacting');
            });

            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const percentX = (x / rect.width) - 0.5;
                const percentY = (y / rect.height) - 0.5;
                const tiltX = percentY * -1 * maxTilt;
                const tiltY = percentX * maxTilt;

                // 实时更新 transform，因为过渡已禁用，所以会立即生效
                requestAnimationFrame(() => {
                    card.style.transform = `translateY(-5px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.05, 1.05, 1.05)`;
                });
            });

            card.addEventListener('mouseleave', (e) => {
                // 鼠标离开时，移除 is-interacting 类，恢复 transform 过渡
                card.classList.remove('is-interacting');
                // 将 transform 重置，CSS 的 transition 会负责平滑归位
                card.style.transform = 'translateY(0) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
            });
        });
    }

    function setupSectionAnimation() {
        const sections = document.querySelectorAll('.fade-in-up');
        const sectionObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        sections.forEach(section => sectionObserver.observe(section));
    }

    function activateCardAnimations() {
        const cards = document.querySelectorAll('.card-fly-in');
        if (cards.length === 0) return;
        const cardObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            root: document.querySelector('.package-scroll-container'),
            threshold: 0.1
        });
        cards.forEach(card => cardObserver.observe(card));
    }

    function setupLazyCardAnimation() {
        const packageSection = document.getElementById('packages');
        if (!packageSection) return;
        const containerObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    activateCardAnimations();
                    observer.unobserve(packageSection);
                }
            });
        }, { threshold: 0.05 });
        containerObserver.observe(packageSection);
    }

    function setupCopyButtons() {
        // 定义图标SVG，嵌入代码中便于维护
        const copyIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg><span>Copy</span>`;
        const copiedIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" /></svg><span>Copied!</span>`;

        const codeBlocks = document.querySelectorAll('pre');

        codeBlocks.forEach(block => {
            const code = block.querySelector('code');
            if (!code) return; // 如果pre里没有code，则跳过

            const button = document.createElement('button');
            button.className = 'copy-button';
            button.innerHTML = copyIcon;

            block.appendChild(button);

            button.addEventListener('click', () => {
                const textToCopy = code.innerText;

                navigator.clipboard.writeText(textToCopy).then(() => {
                    // 复制成功
                    button.innerHTML = copiedIcon;
                    button.classList.add('copied');

                    // 2秒后恢复原状
                    setTimeout(() => {
                        button.innerHTML = copyIcon;
                        button.classList.remove('copied');
                    }, 2000);

                }).catch(err => {
                    // 复制失败
                    console.error('Failed to copy code: ', err);
                    button.querySelector('span').textContent = 'Error';
                });
            });
        });
    }

    // --- 4. 初始化流程 (更新) ---
    async function initialize() {
        // 首先加载包数据并渲染卡片
        await loadPackages();

        // 设置常规 section 的进入动画
        setupSectionAnimation();

        // 设置卡片区域的“懒加载”动画触发器
        setupLazyCardAnimation();

        // NEW: 在卡片加载后，为其绑定交互效果
        setupInteractiveCards();

        // 高亮代码
        hljs.highlightAll();

        // 然后再添加我们的复制按钮
        setupCopyButtons();
    }

    // 启动整个初始化流程
    initialize();
});