document.addEventListener('DOMContentLoaded', () => {

    // --- 1. 辅助函数：格式化文件大小 (无变化) ---
    function formatBytes(bytes, decimals = 1) {
        if (bytes === 0) return { value: '0', unit: 'Bytes', sizeClass: 'size-b' };
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const sizeClasses = ['size-b', 'size-kb', 'size-mb', 'size-gb', 'size-tb'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        const value = parseFloat((bytes / Math.pow(k, i)).toFixed(dm));
        const unit = sizes[i];
        const sizeClass = sizeClasses[i];
        return { value, unit, sizeClass };
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

            const flyInDirections = ['from-left', 'from-right', 'from-top', 'from-bottom'];
            const packageCardsHTML = packages.map((pkg, index) => {
                const formattedSize = formatBytes(pkg.size);
                const downloadUrl = `x86_64/${pkg.filename}`;
                const randomDirection = flyInDirections[index % flyInDirections.length];
                const delay = (index % 20) * 50; // Stagger animation delay

                return `
                    <a href="${downloadUrl}" 
                       class="package-card card-fly-in ${randomDirection}" 
                       title="Download ${pkg.name} ${pkg.version}"
                       style="transition-delay: ${delay}ms;">
                        <div class="package-name">${pkg.name}</div>
                        <div class="package-meta">
                            <div class="package-info">
                                <span class="package-version">v${pkg.version}</span>
                                <span class="package-arch">arch: ${pkg.arch}</span>
                            </div>
                            <div class="package-size ${formattedSize.sizeClass}">
                                ${formattedSize.value} ${formattedSize.unit}
                            </div>
                        </div>
                    </a>
                `;
            }).join('');

            packageListContainer.innerHTML = packageCardsHTML;

            // 重要：此时不再直接调用动画设置，而是等待主初始化流程来处理

        } catch (error) {
            console.error("Failed to load packages:", error);
            packageListContainer.innerHTML = '<p class="loading-text">Error loading packages. Check console.</p>';
        }
    }

    // --- 3. 动画逻辑 ---

    // 3.1 观察并动画化常规 section
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

    // 3.2 激活卡片动画的函数 (第二阶段)
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
            threshold: 0.1 // 稍微降低阈值，确保滚动时能快速触发
        });

        cards.forEach(card => cardObserver.observe(card));
    }

    // 3.3 设置“两阶段”观察者 (第一阶段)
    function setupLazyCardAnimation() {
        const packageSection = document.getElementById('packages');
        if (!packageSection) return;

        const containerObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                // 当整个 #packages 区块进入视口时
                if (entry.isIntersecting) {
                    // 激活真正的卡片动画观察者
                    activateCardAnimations();
                    // 任务完成，停止观察该区块
                    observer.unobserve(packageSection);
                }
            });
        }, { threshold: 0.05 }); // 只要区块有一点点可见就触发

        containerObserver.observe(packageSection);
    }

    // --- 4. 初始化流程 ---
    async function initialize() {
        // 首先加载包数据并渲染卡片到DOM中，但不触发动画
        await loadPackages();

        // 设置常规 section 的进入动画
        setupSectionAnimation();

        // 设置卡片区域的“懒加载”动画触发器
        setupLazyCardAnimation();

        // 最后，高亮代码
        hljs.highlightAll();
    }

    // 启动整个初始化流程
    initialize();
});