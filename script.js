class ImageAnalyzer {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.selectedFile = null;
    }

    initializeElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.previewSection = document.getElementById('previewSection');
        this.previewImage = document.getElementById('previewImage');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsContent = document.getElementById('resultsContent');
        this.copyBtn = document.getElementById('copyBtn');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.toastContainer = document.getElementById('toastContainer');
    }

    bindEvents() {
        // 文件选择事件
        this.uploadBtn.addEventListener('click', () => this.fileInput.click());
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // 拖拽事件
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));

        // 按钮事件
        this.analyzeBtn.addEventListener('click', () => this.analyzeImage());
        this.resetBtn.addEventListener('click', () => this.resetUpload());
        this.copyBtn.addEventListener('click', () => this.copyResults());
    }

    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }

    processFile(file) {
        // 验证文件类型
        if (!file.type.startsWith('image/')) {
            this.showToast('请选择图片文件', 'error');
            return;
        }

        // 验证文件大小 (10MB)
        if (file.size > 10 * 1024 * 1024) {
            this.showToast('文件大小不能超过 10MB', 'error');
            return;
        }

        this.selectedFile = file;
        this.showPreview(file);
    }

    showPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.previewImage.src = e.target.result;
            this.uploadArea.style.display = 'none';
            this.previewSection.style.display = 'block';
            this.resultsSection.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }

    async analyzeImage() {
        if (!this.selectedFile) {
            this.showToast('请先选择图片', 'error');
            return;
        }

        this.showLoading(true);

        try {
            const formData = new FormData();
            formData.append('image', this.selectedFile);

            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.success) {
                this.showResults(result.analysis);
            } else {
                throw new Error(result.error || '分析失败');
            }

        } catch (error) {
            console.error('分析错误:', error);
            this.showToast('分析失败: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    showResults(analysis) {
        this.resultsContent.textContent = analysis;
        this.resultsSection.style.display = 'block';
        this.showToast('分析完成！', 'success');
    }

    resetUpload() {
        this.selectedFile = null;
        this.fileInput.value = '';
        this.uploadArea.style.display = 'block';
        this.previewSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
    }

    async copyResults() {
        try {
            await navigator.clipboard.writeText(this.resultsContent.textContent);
            this.showToast('结果已复制到剪贴板', 'success');
        } catch (error) {
            this.showToast('复制失败', 'error');
        }
    }

    showLoading(show) {
        this.loadingOverlay.style.display = show ? 'flex' : 'none';
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        this.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new ImageAnalyzer();
});