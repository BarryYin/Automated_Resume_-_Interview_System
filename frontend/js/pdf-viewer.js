// PDF查看器功能
class PDFViewer {
    constructor() {
        this.currentPDF = null;
        this.currentPage = 1;
        this.totalPages = 0;
        this.scale = 1.0;
    }

    // 显示PDF预览模态框
    showPDFModal(folder, filename) {
        const modal = document.createElement('div');
        modal.className = 'pdf-modal';
        modal.innerHTML = `
            <div class="pdf-modal-content">
                <div class="pdf-header">
                    <h3>简历预览 - ${filename}</h3>
                    <div class="pdf-controls">
                        <button id="prevPage" class="pdf-btn" disabled>上一页</button>
                        <span id="pageInfo">1 / 1</span>
                        <button id="nextPage" class="pdf-btn" disabled>下一页</button>
                        <button id="zoomOut" class="pdf-btn">缩小</button>
                        <span id="zoomLevel">100%</span>
                        <button id="zoomIn" class="pdf-btn">放大</button>
                        <button id="downloadPDF" class="pdf-btn primary">下载简历</button>
                        <button id="closePDF" class="pdf-btn">×</button>
                    </div>
                </div>
                <div class="pdf-viewer">
                    <div class="pdf-loading">
                        <div class="loading-spinner"></div>
                        <p>正在加载PDF...</p>
                    </div>
                    <canvas id="pdfCanvas"></canvas>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.setupPDFControls(folder, filename);
        this.loadPDF(folder, filename);
    }

    // 设置PDF控制按钮
    setupPDFControls(folder, filename) {
        const modal = document.querySelector('.pdf-modal');
        
        // 关闭按钮
        document.getElementById('closePDF').onclick = () => {
            document.body.removeChild(modal);
        };

        // 下载按钮
        document.getElementById('downloadPDF').onclick = () => {
            this.downloadPDF(folder, filename);
        };

        // 页面控制
        document.getElementById('prevPage').onclick = () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.renderPage();
            }
        };

        document.getElementById('nextPage').onclick = () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                this.renderPage();
            }
        };

        // 缩放控制
        document.getElementById('zoomIn').onclick = () => {
            this.scale = Math.min(this.scale + 0.2, 3.0);
            this.renderPage();
        };

        document.getElementById('zoomOut').onclick = () => {
            this.scale = Math.max(this.scale - 0.2, 0.5);
            this.renderPage();
        };

        // 点击背景关闭
        modal.onclick = (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        };
    }

    // 加载PDF文件
    async loadPDF(folder, filename) {
        try {
            // 显示加载状态
            const loading = document.querySelector('.pdf-loading');
            const canvas = document.getElementById('pdfCanvas');
            loading.style.display = 'flex';
            canvas.style.display = 'none';

            // 尝试从后端API加载
            const apiUrl = `http://localhost:8000/api/resume/${encodeURIComponent(folder)}/${encodeURIComponent(filename)}`;
            
            console.log('加载PDF:', apiUrl);
            
            // 如果支持PDF.js，直接使用PDF.js加载（会自动检查文件是否存在）
            if (window.pdfjsLib) {
                await this.loadWithPDFJS(apiUrl);
            } else {
                // 否则显示下载选项
                this.showDownloadOption(folder, filename);
            }
        } catch (error) {
            console.error('加载PDF失败:', error);
            this.showError(folder, filename);
        }
    }

    // 使用PDF.js加载PDF
    async loadWithPDFJS(url) {
        try {
            console.log('使用PDF.js加载:', url);
            const loadingTask = pdfjsLib.getDocument(url);
            
            loadingTask.onProgress = (progress) => {
                console.log(`加载进度: ${progress.loaded} / ${progress.total}`);
            };
            
            const pdf = await loadingTask.promise;
            console.log('PDF加载成功，总页数:', pdf.numPages);
            
            this.currentPDF = pdf;
            this.totalPages = pdf.numPages;
            this.currentPage = 1;
            
            await this.renderPage();
            
            // 隐藏加载状态
            document.querySelector('.pdf-loading').style.display = 'none';
            document.getElementById('pdfCanvas').style.display = 'block';
            
        } catch (error) {
            console.error('PDF.js加载失败:', error);
            console.error('错误详情:', error.message);
            throw error;
        }
    }

    // 渲染PDF页面
    async renderPage() {
        if (!this.currentPDF) return;

        const page = await this.currentPDF.getPage(this.currentPage);
        const canvas = document.getElementById('pdfCanvas');
        const context = canvas.getContext('2d');

        const viewport = page.getViewport({ scale: this.scale });
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
            canvasContext: context,
            viewport: viewport
        };

        await page.render(renderContext).promise;

        // 更新控制按钮状态
        this.updateControls();
    }

    // 更新控制按钮
    updateControls() {
        document.getElementById('prevPage').disabled = this.currentPage <= 1;
        document.getElementById('nextPage').disabled = this.currentPage >= this.totalPages;
        document.getElementById('pageInfo').textContent = `${this.currentPage} / ${this.totalPages}`;
        document.getElementById('zoomLevel').textContent = `${Math.round(this.scale * 100)}%`;
    }

    // 显示下载选项
    showDownloadOption(folder, filename) {
        const viewer = document.querySelector('.pdf-viewer');
        viewer.innerHTML = `
            <div class="pdf-download-option">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="#666">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                </svg>
                <h3>PDF简历文件</h3>
                <p>文件名: ${filename}</p>
                <p>由于浏览器限制，无法直接预览PDF文件</p>
                <button onclick="pdfViewer.downloadPDF('${folder}', '${filename}')" class="download-btn">
                    下载查看完整简历
                </button>
            </div>
        `;
    }

    // 显示错误信息
    showError(folder, filename) {
        const viewer = document.querySelector('.pdf-viewer');
        viewer.innerHTML = `
            <div class="pdf-error">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="#dc3545">
                    <path d="M12,2C17.53,2 22,6.47 22,12C22,17.53 17.53,22 12,22C6.47,22 2,17.53 2,12C2,6.47 6.47,2 12,2M15.59,7L12,10.59L8.41,7L7,8.41L10.59,12L7,15.59L8.41,17L12,13.41L15.59,17L17,15.59L13.41,12L17,8.41L15.59,7Z"/>
                </svg>
                <h3>无法加载PDF文件</h3>
                <p>文件: ${filename}</p>
                <p>请检查文件是否存在或联系管理员</p>
                <button onclick="pdfViewer.downloadPDF('${folder}', '${filename}')" class="download-btn">
                    尝试下载文件
                </button>
            </div>
        `;
    }

    // 下载PDF文件
    downloadPDF(folder, filename) {
        const apiUrl = `http://localhost:8000/api/resume/${encodeURIComponent(folder)}/${encodeURIComponent(filename)}`;
        
        const link = document.createElement('a');
        link.href = apiUrl;
        link.download = filename;
        link.target = '_blank';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('开始下载简历:', filename);
    }
}

// 创建全局PDF查看器实例
const pdfViewer = new PDFViewer();