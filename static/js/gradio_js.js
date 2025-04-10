function refresh() {
    document.body.classList.remove('dark');

    const style = document.createElement('style');
    style.innerHTML = `
        body, #root, .gradio-container {
            background: linear-gradient(135deg, 
                #ff9a9e 0%, 
                #fad0c4 20%, 
                #fff8dc 40%, 
                #a1c4fd 60%, 
                #c2e9fb 80%, 
                #ffecd2 100%) !important;
            font-family: 'Comic Sans MS', 'Marker Felt', 'Chalkboard', sans-serif !important;
            min-height: 100vh !important
        }
    `;
    document.head.appendChild(style);

    // 获取Gradio主容器
    const container = document.querySelector('.gradio-container');
    if (!container) return;
    
    // 1. 定义网格系统
    const gridSize = 4; // 4x4网格
    const occupied = Array(gridSize * gridSize).fill(false);
    
    // 2. 安全生成5个气球
    const balloonCount = 10;
    for (let i = 0; i < balloonCount; i++) {
        let attempt = 0;
        let cellIndex;
        
        // 3. 最大尝试次数防止死循环
        while (attempt++ < 100) {
            cellIndex = Math.floor(Math.random() * gridSize * gridSize);
            if (!occupied[cellIndex]) break;
        }
        
        // 4. 标记已占用网格
        occupied[cellIndex] = true;
        
        // 5. 计算实际位置（网格内随机）
        const row = Math.floor(cellIndex / gridSize);
        const col = cellIndex % gridSize;
        const left = (col * 100/gridSize + Math.random() * 80/gridSize + 10/gridSize) + '%';
        const top = (row * 100/gridSize + Math.random() * 80/gridSize + 10/gridSize) + '%';
        
        // 6. 创建气球
        const balloon = document.createElement('div');
        balloon.innerHTML = '🎈';
        balloon.style.position = 'absolute';
        balloon.style.left = left;
        balloon.style.top = top;
        balloon.style.fontSize = (30 + Math.random() * 20) + 'px';
        balloon.style.animation = `float ${3 + Math.random() * 4}s ease-in-out infinite`;
        balloon.style.zIndex = 999;
        balloon.style.pointerEvents = 'none';
        container.appendChild(balloon);
    }
}