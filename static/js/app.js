// DOM elements
const image1Input = document.getElementById('image1');
const image2Input = document.getElementById('image2');
const preview1 = document.getElementById('preview-1');
const preview2 = document.getElementById('preview-2');
const uploadBox1 = document.getElementById('upload-box-1');
const uploadBox2 = document.getElementById('upload-box-2');
const compareBtn = document.getElementById('compare-btn');
const resultSection = document.getElementById('result-section');
const scoreValue = document.getElementById('score-value');
const scoreText = document.getElementById('score-text');
const loadingOverlay = document.getElementById('loading-overlay');

// State
let selectedImages = {
    image1: null,
    image2: null
};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

function setupEventListeners() {
    // File input change events
    image1Input.addEventListener('change', (e) => handleFileSelect(e, 'image1'));
    image2Input.addEventListener('change', (e) => handleFileSelect(e, 'image2'));
    
    // Drag and drop events
    setupDragAndDrop(uploadBox1, image1Input, 'image1');
    setupDragAndDrop(uploadBox2, image2Input, 'image2');
    
    // Compare button
    compareBtn.addEventListener('click', compareImages);
}

function handleFileSelect(event, imageKey) {
    const file = event.target.files[0];
    if (file && isValidImageFile(file)) {
        selectedImages[imageKey] = file;
        displayImagePreview(file, imageKey);
        updateUploadBoxState(imageKey, true);
        updateCompareButtonState();
    }
}

function isValidImageFile(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    const validExtensions = ['.heic', '.heif'];
    
    const isValidType = validTypes.includes(file.type);
    const isValidExtension = validExtensions.some(ext => 
        file.name.toLowerCase().endsWith(ext)
    );
    
    if (!isValidType && !isValidExtension) {
        showError('対応している画像形式: JPEG, PNG, GIF, WebP, HEIC');
        return false;
    }
    
    // File size check (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('ファイルサイズは10MB以下にしてください');
        return false;
    }
    
    return true;
}

function displayImagePreview(file, imageKey) {
    const reader = new FileReader();
    const preview = imageKey === 'image1' ? preview1 : preview2;
    
    reader.onload = function(e) {
        // Skip HEIC files for preview (browser can't display them directly)
        if (file.name.toLowerCase().endsWith('.heic') || file.name.toLowerCase().endsWith('.heif')) {
            preview.innerHTML = `
                <div style="padding: 20px; text-align: center; background: #f0f8ff; border-radius: 10px;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">📷</div>
                    <div style="font-weight: 600; color: #2d3748;">${file.name}</div>
                    <div style="color: #718096; font-size: 0.9rem;">HEIC画像が選択されました</div>
                </div>
            `;
        } else {
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview" />`;
        }
        preview.classList.add('active');
    };
    
    reader.onerror = function() {
        showError('画像の読み込みに失敗しました');
    };
    
    reader.readAsDataURL(file);
}

function updateUploadBoxState(imageKey, hasImage) {
    const uploadBox = imageKey === 'image1' ? uploadBox1 : uploadBox2;
    if (hasImage) {
        uploadBox.classList.add('has-image');
    } else {
        uploadBox.classList.remove('has-image');
    }
}

function updateCompareButtonState() {
    const hasAllImages = selectedImages.image1 && selectedImages.image2;
    compareBtn.disabled = !hasAllImages;
    
    if (hasAllImages) {
        compareBtn.style.background = 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)';
        compareBtn.style.transform = 'scale(1.02)';
    }
}

function setupDragAndDrop(uploadBox, fileInput, imageKey) {
    uploadBox.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadBox.style.borderColor = '#4facfe';
        uploadBox.style.background = '#edf2f7';
    });
    
    uploadBox.addEventListener('dragleave', function(e) {
        e.preventDefault();
        if (!uploadBox.classList.contains('has-image')) {
            uploadBox.style.borderColor = '#cbd5e0';
            uploadBox.style.background = '#f7fafc';
        }
    });
    
    uploadBox.addEventListener('drop', function(e) {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (isValidImageFile(file)) {
                fileInput.files = files;
                selectedImages[imageKey] = file;
                displayImagePreview(file, imageKey);
                updateUploadBoxState(imageKey, true);
                updateCompareButtonState();
            }
        }
        uploadBox.style.borderColor = selectedImages[imageKey] ? '#48bb78' : '#cbd5e0';
        uploadBox.style.background = selectedImages[imageKey] ? '#f0fff4' : '#f7fafc';
    });
}

async function compareImages() {
    if (!selectedImages.image1 || !selectedImages.image2) {
        showError('2つの画像を選択してください');
        return;
    }
    
    // Show loading
    showLoading(true);
    compareBtn.disabled = true;
    
    try {
        const formData = new FormData();
        formData.append('image1', selectedImages.image1);
        formData.append('image2', selectedImages.image2);
        
        const response = await fetch('/api/compare/images', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'APIエラーが発生しました');
        }
        
        const result = await response.json();
        displayResult(result.similarity_score);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || '画像比較中にエラーが発生しました');
    } finally {
        showLoading(false);
        compareBtn.disabled = false;
    }
}

function displayResult(score) {
    // Convert to percentage (score is typically between -1 and 1, but ResNet features might be different)
    // Normalize score to 0-100% range
    let percentage;
    if (score >= 0 && score <= 1) {
        percentage = Math.round(score * 100);
    } else if (score >= -1 && score <= 1) {
        // If score is between -1 and 1, normalize to 0-100
        percentage = Math.round(((score + 1) / 2) * 100);
    } else {
        // For other ranges, try to normalize
        percentage = Math.max(0, Math.min(100, Math.round(Math.abs(score) * 100)));
    }
    
    // Animate score display
    animateScore(percentage);
    
    // Update description based on score
    let description;
    let color;
    
    if (percentage >= 90) {
        description = '🎉 素晴らしい！ほぼ同じです！';
        color = '#48bb78';
    } else if (percentage >= 70) {
        description = '😊 とても似ています！良い結果です！';
        color = '#38a169';
    } else if (percentage >= 50) {
        description = '🤔 ある程度似ています。もうちょっと..！';
        color = '#ed8936';
    } else if (percentage >= 30) {
        description = '😐 少し似ている部分があるかも..?';
        color = '#e53e3e';
    } else {
        description = '😅 あまり似ていないようです';
        color = '#c53030';
    }
    
    scoreText.textContent = description;
    resultSection.classList.add('active');
    
    // Update circle color based on score
    const scoreCircle = document.querySelector('.score-circle');
    scoreCircle.style.background = `linear-gradient(135deg, ${color} 0%, ${adjustColorBrightness(color, -20)} 100%)`;
    
    // Scroll to result
    setTimeout(() => {
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 500);
}

function animateScore(targetScore) {
    const scoreElement = scoreValue;
    let currentScore = 0;
    const increment = targetScore / 50; // 50 steps for smooth animation
    const duration = 1500; // 1.5 seconds
    const stepTime = duration / 50;
    
    const animation = setInterval(() => {
        currentScore += increment;
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(animation);
        }
        scoreElement.textContent = Math.round(currentScore);
    }, stepTime);
}

function adjustColorBrightness(hex, percent) {
    // Simple color brightness adjustment
    const num = parseInt(hex.replace("#", ""), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) + amt;
    const G = (num >> 8 & 0x00FF) + amt;
    const B = (num & 0x0000FF) + amt;
    return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
        (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
        (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
}

function showLoading(show) {
    if (show) {
        loadingOverlay.classList.add('active');
    } else {
        loadingOverlay.classList.remove('active');
    }
}

function showError(message) {
    // Simple error display - could be enhanced with a proper modal
    alert(`エラー: ${message}`);
}

// Additional utility functions for better UX
function resetComparison() {
    selectedImages.image1 = null;
    selectedImages.image2 = null;
    
    preview1.classList.remove('active');
    preview2.classList.remove('active');
    preview1.innerHTML = '';
    preview2.innerHTML = '';
    
    updateUploadBoxState('image1', false);
    updateUploadBoxState('image2', false);
    
    image1Input.value = '';
    image2Input.value = '';
    
    compareBtn.disabled = true;
    compareBtn.style.background = '';
    compareBtn.style.transform = '';
    
    resultSection.classList.remove('active');
    scoreValue.textContent = '0';
    scoreText.textContent = '画像をアップロードして採点してください';
}

// Optional: Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        showLoading(false);
    }
    
    if (e.key === 'Enter' && !compareBtn.disabled) {
        compareImages();
    }
});

// Prevent default drag behaviors on the page
document.addEventListener('dragover', function(e) {
    e.preventDefault();
});

document.addEventListener('drop', function(e) {
    e.preventDefault();
});