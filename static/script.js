// 提醒看板已被移除
function fetchExpiringCustomers() {
    // 此函数已被简化，不再显示提醒看板
    console.log('提醒看板功能已被移除');
}

// 快捷按钮链接配置
document.addEventListener('DOMContentLoaded', function() {
    // 配置快捷按钮的链接
    const shortcutLinks = {
        'btn-hetiao': 'https://bi.jdydevelop.com/webroot/decision#/?activeTab=6ed7a7e6-70b0-4814-9424-35d784d8e686',  // 业绩链接
        'btn-sa': 'https://dc.jdydevelop.com/sa?redirect_uri=%2Finfo_search%2Fuser_search',      // SA链接
        'btn-huikuan': 'https://crm.finereporthelp.com/WebReport/decision/view/report?viewlet=finance/jdy_confirm/bank_income_list_cofirm.cpt&op=write',  // 回款链接
        'btn-xiadan': 'https://open.work.weixin.qq.com/wwopen/developer#/sass/license/service/order/detail?orderid=OI00000FEA3AC66805CA325DABD6AN',   // 接口链接
        'btn-qiwei': 'https://crm.finereporthelp.com/WebReport/decision?#?activeTab=bf50447e-5ce2-4c7f-834e-3e1495df033a',                                           // kms链接
        'btn-daike': 'https://bi.finereporthelp.com/webroot/decision?#/directory?activeTab=4a3d1d52-2e58-4e0c-bb82-722b1a8bc6bf'    // 看板链接
    };
    
    // 内联快捷按钮的链接配置（与顶部快捷按钮使用相同的链接）
    const inlineShortcutLinks = {
        'btn-hetiao-inline': 'https://bi.finereporthelp.com/webroot/decision?#/directory?activeTab=4a3d1d52-2e58-4e0c-bb82-722b1a8bc6bf',  // 业绩进度链接
        'btn-sa-inline': 'https://dc.jdydevelop.com/sa?redirect_uri=%2Finfo_search%2Fuser_search',      // SA链接
        'btn-huikuan-inline': 'https://crm.finereporthelp.com/WebReport/decision/view/report?viewlet=finance/jdy_confirm/bank_income_list_cofirm.cpt&op=write',  // 回款链接
        'btn-xiadan-inline': 'https://open.work.weixin.qq.com/wwopen/developer#/sass/license/service/order/detail?orderid=OI00000FEA3AC66805CA325DABD6AN',   // 接口链接
        'btn-qiwei-inline': 'https://crm.finereporthelp.com/WebReport/decision?#?activeTab=bf50447e-5ce2-4c7f-834e-3e1495df033a',      // kms链接
        'btn-daike-inline': 'https://bi.finereporthelp.com/webroot/decision?#/directory?activeTab=12d9701c-b4b7-4ae7-b37f-ff3d418f4b8a'    // 客户归属链接
    };
    
    
    // 为顶部快捷按钮添加点击事件
    Object.keys(shortcutLinks).forEach(btnId => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.addEventListener('click', function() {
                window.open(shortcutLinks[btnId], '_blank');
            });
        }
    });
    
    // 为内联快捷按钮添加点击事件
    Object.keys(inlineShortcutLinks).forEach(btnId => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.addEventListener('click', function() {
                window.open(inlineShortcutLinks[btnId], '_blank');
            });
        }
    });
});

// 提醒看板已被移除，此函数不再使用
function showExpiringCustomersAlert() {
    console.log('提醒看板功能已被移除');
}

// 创建备忘录白板（替代原来的25-30天到期客户看板）
function showFutureExpiringCustomersDashboard(estherCustomers, otherCustomers) {
    // 检查是否已存在看板，如果存在则移除
    const existingDashboard = document.querySelector('.future-expiring-dashboard');
    if (existingDashboard) {
        existingDashboard.remove();
    }

    // 创建看板容器（保持原来的类名以维持样式）
    const dashboardContainer = document.createElement('div');
    dashboardContainer.className = 'future-expiring-dashboard';
    dashboardContainer.style.width = '335px';
    dashboardContainer.style.maxHeight = '600px'; // 增加高度，使其占据更多空间

    // 创建看板标题
    const dashboardHeader = document.createElement('div');
    dashboardHeader.className = 'dashboard-header';

    const memoTitle = document.createElement('h4');
    memoTitle.textContent = '备忘录';
    memoTitle.style.color = 'var(--text-color)';
    memoTitle.style.margin = '0';
    memoTitle.style.fontSize = '16px';

    const closeButton = document.createElement('button');
    closeButton.className = 'close-btn';
    closeButton.textContent = '×';
    closeButton.onclick = function() {
        dashboardContainer.remove();
    };

    dashboardHeader.appendChild(memoTitle);
    dashboardHeader.appendChild(closeButton);

    // 创建备忘录内容区域（使用原来的dashboard-body类名）
    const dashboardBody = document.createElement('div');
    dashboardBody.className = 'dashboard-body';
    dashboardBody.style.height = '540px'; // 增加内容区域高度

    const memoTextarea = document.createElement('textarea');
    memoTextarea.className = 'memo-textarea';
    memoTextarea.placeholder = '在这里记录您的备忘事项...\n\n• 待办事项\n• 重要提醒\n• 工作笔记\n• 客户跟进\n• 项目计划';
    memoTextarea.style.width = '100%';
    memoTextarea.style.height = '100%';
    memoTextarea.style.border = 'none';
    memoTextarea.style.outline = 'none';
    memoTextarea.style.resize = 'none';
    memoTextarea.style.padding = '15px';
    memoTextarea.style.fontSize = '14px';
    memoTextarea.style.lineHeight = '1.5';
    memoTextarea.style.backgroundColor = 'transparent';
    memoTextarea.style.color = 'var(--text-color)';
    memoTextarea.style.fontFamily = 'inherit';

    // 从本地存储加载备忘录内容
    const savedMemo = localStorage.getItem('memo-content');
    if (savedMemo) {
        memoTextarea.value = savedMemo;
    }

    // 自动保存备忘录内容
    memoTextarea.addEventListener('input', function() {
        localStorage.setItem('memo-content', this.value);
    });

    dashboardBody.appendChild(memoTextarea);

    // 组装看板
    dashboardContainer.appendChild(dashboardHeader);
    dashboardContainer.appendChild(dashboardBody);

    // 添加到页面
    document.body.appendChild(dashboardContainer);
}





// 页面加载完成后获取即将过期的客户并显示备忘录
document.addEventListener('DOMContentLoaded', function() {
    // 检查用户是否已登录（通过检查页面上的元素判断）
    if (document.getElementById('contractForm')) {
        // 延迟调用，确保页面完全加载
        setTimeout(() => {
            fetchExpiringCustomers();
            // 显示备忘录白板（替代原来的25-30天到期客户看板）
            showFutureExpiringCustomersDashboard([], []);
        }, 1000);
    }
    
    // 智能表单填充功能
    initClipboardFeature();
    
    // OCR功能增强
    enhanceOCRFeature();
});

// 初始化粘贴板功能
function initClipboardFeature() {
    const clipboardArea = document.getElementById('clipboardArea');
    const clipboardTextarea = document.getElementById('clipboardTextarea');
    const clipboardContent = clipboardArea?.querySelector('.clipboard-content');
    
    if (!clipboardArea || !clipboardTextarea || !clipboardContent) return;
    
    // 点击区域显示文本框
    clipboardContent.addEventListener('click', function() {
        clipboardContent.style.display = 'none';
        clipboardTextarea.style.display = 'block';
        clipboardTextarea.focus();
    });
    
    // 文本框失去焦点时的处理
    clipboardTextarea.addEventListener('blur', function() {
        if (!clipboardTextarea.value.trim()) {
            clipboardTextarea.style.display = 'none';
            clipboardContent.style.display = 'flex';
        }
    });
    
    // 支持粘贴事件 - 自动解析并填充
    clipboardTextarea.addEventListener('paste', function(e) {
        setTimeout(() => {
            if (clipboardTextarea.value.trim()) {
                parseClipboardText(clipboardTextarea.value.trim());
            }
        }, 100);
    });
    
    // 输入事件 - 实时解析
    clipboardTextarea.addEventListener('input', function(e) {
        const text = clipboardTextarea.value.trim();
        if (text.length > 10) { // 当输入内容足够长时自动解析
            parseClipboardText(text);
        }
    });
}

// 解析粘贴板文本并自动填充
function parseClipboardText(text) {
    
    
    // 发送到后端解析
    fetch('/parse_text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => {
        const contentType = response.headers.get('content-type');
        if (!response.ok || !contentType || !contentType.includes('application/json')) {
            throw new Error('文本解析服务不可用');
        }
        return response.json();
    })
    .then(data => {
        if (data.success && data.fields) {
            
            // 直接应用解析结果到表单
            const appliedCount = autoFillFields(data.fields);
            
            // 处理警告信息
            if (data.warnings && data.warnings.length > 0) {
                showOCRWarnings(data.warnings);
            }
        } else {
            console.error('解析失败:', data.error || '未知错误');
            showAutoFillError(data.error || '文本解析失败');
        }
    })
    .catch(error => {
        console.error('解析文本错误:', error);
        showAutoFillError('文本解析服务暂时不可用，当前为静态预览模式');
    });
}

// 自动填充字段到表单
function autoFillFields(fields) {
    let appliedCount = 0;
    const fieldMapping = {
        'company_name': '公司名称',
        'tax_number': '税号',
        'reg_address': '注册地址',
        'reg_phone': '注册电话',
        'bank_name': '开户行',
        'bank_account': '银行账号',
        'jdy_account': '简道云账号'
    };
    

    
    for (const [fieldName, value] of Object.entries(fields)) {
        const input = document.getElementById(fieldName);
        const fieldLabel = fieldMapping[fieldName] || fieldName;
        
        if (input && value && value.trim()) {
            const oldValue = input.value;
            input.value = value.trim();
            appliedCount++;
            
            // 添加视觉反馈
            input.classList.add('auto-filled');
            
            
            
            // 移除高亮效果
            setTimeout(() => {
                input.classList.remove('auto-filled');
            }, 3000);
            
            // 触发输入事件（用于公司名称搜索等）
            if (fieldName === 'company_name' || fieldName === 'jdy_account') {
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
            
            // 触发change事件
            input.dispatchEvent(new Event('change', { bubbles: true }));
        } else if (!input) {
            console.warn(`⚠️ 未找到字段 ${fieldName} 对应的输入框`);
        } else if (!value || !value.trim()) {
            console.warn(`⚠️ 字段 ${fieldLabel} 的值为空`);
        }
    }
    

    return appliedCount;
}

// 自动填充成功提示已移除，直接进行字段填充

// 显示OCR警告信息
function showOCRWarnings(warnings) {
    warnings.forEach((warning, index) => {
        const warningDiv = document.createElement('div');
        warningDiv.className = 'ocr-warning';
        
        // 简化的警告内容，去掉标题，只显示核心提醒
        warningDiv.innerHTML = `
            <div class="warning-icon">🧐</div>
            <div class="warning-content">
                <span class="warning-text">税号包含0/O,请注意检查</span>
            </div>
            <button class="close-btn" onclick="this.parentElement.remove()">×</button>
        `;
        
        // 优化样式 - 更小巧美观
        warningDiv.style.cssText = `
            position: fixed;
            top: ${20 + index * 60}px;
            right: 20px;
            background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
            border: 1px solid #ffd93d;
            border-radius: 12px;
            padding: 12px 16px;
            max-width: 280px;
            box-shadow: 0 6px 20px rgba(255, 193, 7, 0.2);
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 10px;
            animation: slideInRight 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            backdrop-filter: blur(10px);
            border-left: 4px solid #ffc107;
        `;
        
        // 添加优化的样式
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            .ocr-warning .warning-icon {
                font-size: 18px;
                flex-shrink: 0;
            }
            
            .ocr-warning .warning-content {
                flex: 1;
            }
            
            .ocr-warning .warning-text {
                font-size: 14px;
                color: #856404;
                font-weight: 500;
                line-height: 1.3;
            }
            
            .ocr-warning .close-btn {
                background: none;
                border: none;
                font-size: 16px;
                cursor: pointer;
                color: #856404;
                padding: 4px;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: all 0.2s ease;
                flex-shrink: 0;
            }
            
            .ocr-warning .close-btn:hover {
                background: rgba(133, 100, 4, 0.15);
                transform: scale(1.1);
            }
            
            .ocr-warning:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(255, 193, 7, 0.3);
                transition: all 0.3s ease;
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(warningDiv);
        
        // 8秒后自动移除
        setTimeout(() => {
            if (warningDiv.parentElement) {
                warningDiv.style.animation = 'slideOutRight 0.3s ease-in forwards';
                setTimeout(() => {
                    if (warningDiv.parentElement) {
                        warningDiv.remove();
                    }
                }, 300);
            }
        }, 8000);
    });
    
    // 添加退出动画
    const exitStyle = document.createElement('style');
    exitStyle.textContent = `
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(exitStyle);
}

// 显示自动填充错误提示
function showAutoFillError(errorMessage) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'auto-fill-error';
    errorDiv.innerHTML = `
        <div class="error-icon">❌</div>
        <div class="error-content">
            <h4>自动填充失败</h4>
            <p>${errorMessage}</p>
        </div>
        <button class="close-btn" onclick="this.parentElement.remove()">×</button>
    `;
    
    // 添加样式
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 15px;
        max-width: 350px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        display: flex;
        align-items: flex-start;
        gap: 10px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(errorDiv);
    
    // 5秒后自动移除
    setTimeout(() => {
        if (errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 5000);
}

// 增强OCR功能
function enhanceOCRFeature() {
    // OCR图片上传处理
    const imageFileInput = document.getElementById('imageFileInput');
    const imageUploadArea = document.getElementById('imageUploadArea');
    
    // 点击上传区域触发文件选择
    if (imageUploadArea) {
        imageUploadArea.addEventListener('click', function() {
            imageFileInput.click();
        });
    }
    
    if (imageFileInput) {
        imageFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const previewImage = document.getElementById('previewImage');
                    const imagePreview = document.getElementById('imagePreview');
                    const imageUploadArea = document.getElementById('imageUploadArea');
                    
                    // 显示图片预览
                    previewImage.src = e.target.result;
                    imagePreview.style.display = 'block';
                    imageUploadArea.style.display = 'none';
                    
                    // 自动开始OCR识别并填充
                    processImageForOCR(e.target.result);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // 拖拽上传功能
    if (imageUploadArea) {
        imageUploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            imageUploadArea.classList.add('dragover');
        });

        imageUploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            imageUploadArea.classList.remove('dragover');
        });

        imageUploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            imageUploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type.startsWith('image/')) {
                    imageFileInput.files = files;
                    imageFileInput.dispatchEvent(new Event('change'));
                } else {
                    alert('请上传图片文件');
                }
            }
        });
    }
    
    // 清除图片按钮
    const clearImageBtn = document.getElementById('clearImageBtn');
    if (clearImageBtn) {
        clearImageBtn.addEventListener('click', function() {
            const imagePreview = document.getElementById('imagePreview');
            const imageUploadArea = document.getElementById('imageUploadArea');
            const ocrProgress = document.getElementById('ocrProgress');
            
            imagePreview.style.display = 'none';
            imageUploadArea.style.display = 'block';
            ocrProgress.style.display = 'none';
            
            // 清空文件输入
            imageFileInput.value = '';
        });
    }
    
    // 支持粘贴图片
    document.addEventListener('paste', function(e) {
        const items = e.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const blob = items[i].getAsFile();
                const reader = new FileReader();
                reader.onload = function(e) {
                    const previewImage = document.getElementById('previewImage');
                    const imagePreview = document.getElementById('imagePreview');
                    const imageUploadArea = document.getElementById('imageUploadArea');
                    
                    // 显示图片预览
                    previewImage.src = e.target.result;
                    imagePreview.style.display = 'block';
                    imageUploadArea.style.display = 'none';
                    
                    // 自动开始OCR识别并填充
                    processImageForOCR(e.target.result);
                };
                reader.readAsDataURL(blob);
                break;
            }
        }
    });
}

// 处理图片OCR识别并自动填充
function processImageForOCR(imageSrc) {
    const ocrProgress = document.getElementById('ocrProgress');
    
    if (!ocrProgress) return;
    
    // 显示进度
    ocrProgress.style.display = 'block';
    
    // 将base64图片发送到后端
    fetch('/ocr_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: imageSrc })
    })
    .then(response => {
        const contentType = response.headers.get('content-type');
        if (!response.ok || !contentType || !contentType.includes('application/json')) {
            throw new Error('OCR识别服务不可用');
        }
        return response.json();
    })
    .then(data => {
        ocrProgress.style.display = 'none';
        
        if (data.success) {
            // 如果有字段信息，直接填充
            if (data.fields && Object.keys(data.fields).length > 0) {
                // 直接应用解析结果到表单
                const appliedCount = autoFillFields(data.fields);
                
                // 处理警告信息
                if (data.warnings && data.warnings.length > 0) {
                    showOCRWarnings(data.warnings);
                }
            } else if (data.text) {
                // 如果没有字段信息但有文本，使用文本解析
                parseClipboardText(data.text);
            }
        } else {
            console.error('OCR识别失败:', data.error);
            showAutoFillError(data.error || 'OCR识别失败');
        }
    })
    .catch(error => {
        console.error('OCR识别错误:', error);
        ocrProgress.style.display = 'none';
        showAutoFillError('OCR识别服务暂时不可用，当前为静态预览模式');
    });
}




// 根据集成模式显示下单流程提醒
function showOrderProcessTip(mode) {
    // 检查是否已存在提醒区域，如果存在则移除
    let tipElement = document.getElementById('integrationModeTip');
    if (!tipElement) {
        // 创建提醒区域元素
        tipElement = document.createElement('div');
        tipElement.id = 'integrationModeTip';
        tipElement.className = 'integration-mode-tip';
        
        // 将提醒区域添加到集成模式span元素后面，而不是整个info-row后面
        const integrationModeElement = document.getElementById('integrationMode');
        if (integrationModeElement) {
            // 为集成模式文本添加粉红色样式类
            integrationModeElement.classList.add('pink-text');
            
            // 将提醒区域添加到集成模式元素后面
            integrationModeElement.after(tipElement);
        }
    }
    
    // 确保mode是字符串，并且转换为小写进行比较，提高识别准确率
    const modeText = String(mode).toLowerCase().trim();
    
    // 根据集成模式显示不同的提醒信息
    if (modeText.includes('企微')) {
        tipElement.innerHTML = `
            <div class="tip-content">
                <strong>⚠️</strong>
                <p class="integration-tip-text">创建订单+企微接口</p>
            </div>
        `;
        tipElement.style.display = 'block';
    } else if (modeText.includes('钉钉')) {
        tipElement.innerHTML = `
            <div class="tip-content">
                <strong>⚠️</strong>
                <p class="integration-tip-text">直接在钉钉后台下单</p>
            </div>
        `;
        tipElement.style.display = 'block';
    } else {
        tipElement.style.display = 'none';
    }
}

function queryCustomer() {
    const jdyId = document.querySelector('[name="jdy_account"]').value.trim();
    if (!jdyId) {
        alert('请输入简道云账号');
        return;
    }

    fetch('/query_customer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ jdy_id: jdyId })
    })
    .then(response => {
        const contentType = response.headers.get('content-type');
        if (!response.ok || !contentType || !contentType.includes('application/json')) {
            throw new Error('客户查询服务不可用');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // 更新表单字段
        if (data.company_name && data.company_name !== 'nan') {
            document.querySelector('[name="company_name"]').value = data.company_name;
        }
        if (data.tax_number && data.tax_number !== 'nan') {
            document.querySelector('[name="tax_number"]').value = data.tax_number;
        }
        
        // 更新显示内容
        document.getElementById('accountEnterpriseName').textContent = data.account_enterprise_name || '暂无数据';
        const integrationMode = data.integration_mode || '暂无数据';
        document.getElementById('integrationMode').textContent = integrationMode;
        document.getElementById('expiryDate').textContent = data.expiry_date || '暂无数据';
        document.getElementById('uidArr').textContent = data.uid_arr || '0元';
        
        // 设置客户分类并处理战区名单的样式
        const customerClassification = document.getElementById('customerClassification');
        const classificationText = data.customer_classification || '暂无数据';
        
        // 检查是否是精确的"战区Name名单"
        if (classificationText === '战区Name名单') {
            // 移除可能存在的其他样式类
            customerClassification.classList.remove('pink-text', 'blue-text');
            
            // 直接设置内联样式，使用!important确保优先级
            customerClassification.style.color = '#1890ff !important'; // 明显的蓝色
            customerClassification.style.fontWeight = '500';
            customerClassification.style.padding = '2px 6px';
            customerClassification.style.borderRadius = '4px';
            customerClassification.style.backgroundColor = 'rgba(24, 144, 255, 0.1)';
            
            // 设置文本内容并添加提醒
            customerClassification.textContent = classificationText + ' ⚠️ 找销售 ';
        } else {
            // 重置所有样式
            customerClassification.classList.remove('pink-text', 'blue-text');
            customerClassification.style.color = '';
            customerClassification.style.fontWeight = '';
            customerClassification.style.padding = '';
            customerClassification.style.borderRadius = '';
            customerClassification.style.backgroundColor = '';
            
            // 只显示原始文本，不添加提醒
            customerClassification.textContent = classificationText;
        }
        
        document.getElementById('salesPerson').textContent = data.sales || '暂无数据';
        document.getElementById('salesCnEn').textContent = data.sales_cn_en || '暂无数据';
        document.getElementById('jdySales').textContent = data.jdy_sales || '暂无数据';
        
        // 显示结果区域
        document.getElementById('customerInfo').style.display = 'block';
        
        // 显示下单流程提醒
        showOrderProcessTip(integrationMode);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('客户查询服务暂时不可用，当前为静态预览模式');
    });
}

// 创建智能计算器
function createSmartCalculator() {
    // 检查是否已存在计算器，如果存在则移除
    const existingCalculator = document.getElementById('smart-calculator');
    if (existingCalculator) {
        existingCalculator.remove();
    }

    // 创建计算器容器
    const calculatorContainer = document.createElement('div');
    calculatorContainer.id = 'smart-calculator';
    calculatorContainer.className = 'smart-calculator';

    // 创建计算器头部
    const calculatorHeader = document.createElement('div');
    calculatorHeader.className = 'calculator-header';
    calculatorHeader.textContent = '智能计算器';

    // 创建计算器显示区域
    const calculatorDisplay = document.createElement('div');
    calculatorDisplay.className = 'calculator-display';

    // 创建结果显示区域
    const displayInput = document.createElement('input');
    displayInput.type = 'text';
    displayInput.readOnly = true;
    displayInput.className = 'calculator-input';
    displayInput.value = '0';

    calculatorDisplay.appendChild(displayInput);

    // 创建计算器按钮区域
    const calculatorButtons = document.createElement('div');
    calculatorButtons.className = 'calculator-buttons';

    // 定义计算器按钮
    const buttons = [
        ['7', '8', '9', '÷'],
        ['4', '5', '6', '×'],
        ['1', '2', '3', '-'],
        ['0', '.', '=', '+'],
        ['AC', 'C']
    ];

    // 创建按钮
    buttons.forEach(row => {
        const buttonRow = document.createElement('div');
        buttonRow.className = 'calculator-row';
        
        row.forEach(buttonText => {
            const button = document.createElement('button');
            button.className = 'calculator-button';
            button.textContent = buttonText;
            
            // 根据按钮类型添加不同的样式
            if (['÷', '×', '-', '+'].includes(buttonText)) {
                button.classList.add('operator-button');
            } else if (buttonText === '=') {
                button.classList.add('equals-button');
            } else if (['AC', 'C'].includes(buttonText)) {
                button.classList.add('clear-button');
            }
            
            buttonRow.appendChild(button);
        });
        
        calculatorButtons.appendChild(buttonRow);
    });

    // 组装计算器
    calculatorContainer.appendChild(calculatorHeader);
    calculatorContainer.appendChild(calculatorDisplay);
    calculatorContainer.appendChild(calculatorButtons);
    document.body.appendChild(calculatorContainer);

    // 添加计算器事件处理
    const calculatorButtonElements = calculatorContainer.querySelectorAll('.calculator-button');
    const display = displayInput;
    let firstOperand = '';
    let operator = '';
    let waitingForSecondOperand = false;

    calculatorButtonElements.forEach(button => {
        button.addEventListener('click', function() {
            const value = this.textContent;
            handleButtonClick(value);
        });
    });

    // 添加回车键执行等于操作，但只在计算器显示或按钮区域被点击后才捕获键盘事件
    let calculatorActive = false;
    
    // 监听计算器容器的点击事件，标记计算器为活动状态
    calculatorContainer.addEventListener('click', function() {
        calculatorActive = true;
    });
    
    // 监听整个文档的点击事件，如果点击不在计算器上，则标记计算器为非活动状态
    document.addEventListener('click', function(e) {
        if (!calculatorContainer.contains(e.target)) {
            calculatorActive = false;
        }
    });
    
    // 修改键盘事件处理，使计算器输入框可以正常接收键盘输入
    document.addEventListener('keydown', function(e) {
        // 特殊处理：如果焦点在计算器输入框上，允许输入数字和小数点
        if (e.target === displayInput) {
            if ('0123456789.'.includes(e.key)) {
                e.preventDefault();
                handleButtonClick(e.key);
            } else if (e.key === 'Backspace') {
                e.preventDefault();
                display.value = display.value.slice(0, -1) || '0';
            } else if (e.key === 'Enter') {
                e.preventDefault();
                handleButtonClick('=');
            } else if (e.key === ' ') {
                // 空格键在输入框中也实现乘法操作
                e.preventDefault();
                handleButtonClick('×');
            }
            return;
        }
        
        // 如果是在其他文本输入区域（textarea, input等），则不处理计算器快捷键
        if (e.target.matches('textarea, input:not(.calculator-input), [contenteditable="true"]')) {
            return;
        }
        
        // 只有当计算器活动时才处理键盘事件
        if (calculatorActive) {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleButtonClick('=');
            } else if ('0123456789.'.includes(e.key)) {
                handleButtonClick(e.key);
            } else if (['+', '-', '*', '/'].includes(e.key)) {
                handleButtonClick(e.key.replace('*', '×').replace('/', '÷'));
            } else if (e.key.toLowerCase() === 'c') {
                handleButtonClick('C');
            } else if (e.key.toLowerCase() === 'escape') {
                handleButtonClick('AC');
            } else if (e.key === 'Backspace') {
                // Backspace键实现删除单个字符的功能
                display.value = display.value.slice(0, -1) || '0';
            } else if (e.key === ' ') {
                // 空格键实现乘法操作
                e.preventDefault();
                handleButtonClick('×');
            }
        }
    });

    function handleButtonClick(value) {
        if (/\d/.test(value)) {
            // 数字按钮
            if (waitingForSecondOperand) {
                display.value = value;
                waitingForSecondOperand = false;
            } else {
                display.value = display.value === '0' ? value : display.value + value;
            }
            return;
        }

        if (value === '.') {
            // 小数点按钮
            if (waitingForSecondOperand) {
                display.value = '0.';
                waitingForSecondOperand = false;
                return;
            }
            if (display.value.indexOf('.') === -1) {
                display.value += '.';
            }
            return;
        }

        if (['+', '-', '×', '÷'].includes(value)) {
            // 操作符按钮
            performCalculation();
            operator = value;
            
            // 从显示的式子中提取结果值
            const currentDisplay = display.value;
            const resultMatch = currentDisplay.match(/=\s*(.+)$/);
            if (resultMatch) {
                firstOperand = resultMatch[1];
            } else {
                firstOperand = currentDisplay;
            }
            
            waitingForSecondOperand = true;
            return;
        }

        if (value === '=') {
            // 等于按钮
            performCalculation();
            // 保存当前结果作为下一次计算的第一个操作数
            const currentResult = display.value;
            // 从显示的式子中提取结果值
            const resultMatch = currentResult.match(/=\s*(.+)$/);
            if (resultMatch) {
                firstOperand = resultMatch[1];
            } else {
                firstOperand = currentResult;
            }
            operator = '';
            waitingForSecondOperand = true;
            return;
        }

        if (value === 'C') {
            // 清空输入（根据用户需求修改）
            display.value = '0';
            return;
        }

        if (value === 'AC') {
            // 全部清除
            display.value = '0';
            firstOperand = '';
            operator = '';
            waitingForSecondOperand = false;
            return;
        }
    }

    function performCalculation() {
        if (operator && firstOperand !== '') {
            const secondOperand = display.value;
            let result;
            
            try {
                // 将操作符转换为JavaScript操作符
                const op = operator === '×' ? '*' : operator === '÷' ? '/' : operator;
                
                // 对所有运算都使用更精确的计算方式
                const num1 = parseFloat(firstOperand);
                const num2 = parseFloat(secondOperand);
                
                if (op === '+') {
                    result = num1 + num2;
                } else if (op === '-') {
                    result = num1 - num2;
                } else if (op === '*') {
                    result = num1 * num2;
                } else if (op === '/') {
                    result = num1 / num2;
                }
                
                // 格式化结果 - 更好的小数处理
                let formattedResult;
                if (Number.isInteger(result) || (Math.abs(result) >= 1e15 || Math.abs(result) < 1e-10)) {
                    // 整数或非常大的/小的数使用科学计数法
                    formattedResult = result.toString();
                } else {
                    // 对于普通小数，使用toLocaleString确保更好的格式化
                    // 或者使用正则表达式去掉末尾的0
                    formattedResult = result.toFixed(12).replace(/\.?0+$/, '');
                    // 确保小数点后至少保留6位有效数字
                    if (formattedResult.includes('.')) {
                        const parts = formattedResult.split('.');
                        if (parts[1].length < 6) {
                            formattedResult = result.toFixed(6).replace(/\.?0+$/, '');
                        }
                    }
                }
                
                // 显示完整的运算式子
                display.value = `${firstOperand} ${operator} ${secondOperand} = ${formattedResult}`;
            } catch (error) {
                display.value = '错误';
            }
        }
    }
}

// 悬浮球功能 =====
document.addEventListener('DOMContentLoaded', function() {
    const assistBall = document.getElementById('assistBall');
    const assistPanel = document.getElementById('assistPanel');
    const assistClose = document.getElementById('assistClose');
    const assistId = document.getElementById('assistId');
    const assistMemo = document.getElementById('assistMemo');
    const assistAsk = document.getElementById('assistAsk');
    const assistAnswer = document.getElementById('assistAnswer');
    
    // 悬浮球点击事件
    assistBall.addEventListener('click', function() {
        toggleAssistPanel();
    });
    
    // 关闭按钮点击事件
    assistClose.addEventListener('click', function() {
        closeAssistPanel();
    });
    
    // 键盘快捷键 Ctrl/⌘ + Shift + K
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'K') {
            e.preventDefault();
            toggleAssistPanel();
        }
    });
    
    // 点击面板外部关闭
    document.addEventListener('click', function(e) {
        if (!assistPanel.contains(e.target) && !assistBall.contains(e.target)) {
            closeAssistPanel();
        }
    });
    
    // 自动识别简道云账号
    function autoDetectJdyAccount() {
        const jdyAccountInput = document.querySelector('[name="jdy_account"]');
        if (jdyAccountInput && jdyAccountInput.value.trim()) {
            assistId.value = jdyAccountInput.value.trim();
        }
    }
    
    // 推进阶段按钮事件
    document.getElementById('btnStageContract').addEventListener('click', function() {
        updateStage('合同', assistId.value.trim());
    });
    
    document.getElementById('btnStageInvoice').addEventListener('click', function() {
        updateStage('开票', assistId.value.trim());
    });
    
    document.getElementById('btnStageAdvanceInvoice').addEventListener('click', function() {
        updateStage('提前开', assistId.value.trim());
    });
    
    document.getElementById('btnStageInvalid').addEventListener('click', function() {
        updateStage('无效', assistId.value.trim());
    });
    
    document.getElementById('btnStageUpsell').addEventListener('click', function() {
        updateStage('增购', assistId.value.trim());
    });
    
    document.getElementById('btnStageLost').addEventListener('click', function() {
        updateStage('失联', assistId.value.trim());
    });
    
    document.getElementById('btnStagePaid').addEventListener('click', function() {
        updateStage('回款', assistId.value.trim());
    });
    
    // 未签订合同客户功能
    document.getElementById('btnRefreshUnsigned').addEventListener('click', function() {
        fetchUnsignedCustomers();
    });
    
    // 绑定自动监控按钮事件
    // 停止监控按钮已移除
    
    const btnCheckNow = document.getElementById('btnCheckNow');
    if (btnCheckNow) {
        btnCheckNow.addEventListener('click', function() {
            // 立即检查监控状态
            updateMonitorStatus();
        });
    }
    
    // 问答功能
    document.getElementById('btnAsk').addEventListener('click', function() {
        askQuestion();
    });
    
    document.getElementById('btnClear').addEventListener('click', function() {
        clearAssistPanel();
    });
    
    // 初始化时加载未签订合同客户
    fetchUnsignedCustomers();
    
    // 初始化监控状态
    initializeMonitorStatus();
    
    // 创建智能计算器
    createSmartCalculator();
    
    // 面板打开时自动识别账号
    function onPanelOpen() {
        autoDetectJdyAccount();
    }
    
    function toggleAssistPanel() {
        if (assistPanel.classList.contains('open')) {
            closeAssistPanel();
        } else {
            openAssistPanel();
        }
    }
    
    function openAssistPanel() {
        assistPanel.classList.add('open');
        assistPanel.setAttribute('aria-hidden', 'false');
        onPanelOpen();
    }
    
    function closeAssistPanel() {
        assistPanel.classList.remove('open');
        assistPanel.setAttribute('aria-hidden', 'true');
    }
    
    function updateStage(stage, jdyId, force = false) {
        if (!jdyId) {
            assistAnswer.textContent = '请先填写简道云账号';
            return;
        }
        
        assistAnswer.textContent = `正在推进到"${stage}"阶段...`;
        
        // 调用优化的状态更新API
        fetch('/update_stage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                jdy_id: jdyId,
                stage: stage,
                force: force
            })
        })
        .then(response => {
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('阶段推进服务不可用');
            }
            return response.json().then(data => ({ data, status: response.status }));
        })
        .then(({ data, status }) => {
            if (data.success) {
                // 成功更新
                const message = data.message || `已推进到"${stage}"阶段`;
                const updatedCount = data.updated_count || 1;
                assistAnswer.textContent = `✅ ${message} (更新了${updatedCount}条记录)`;
                
                // 如果有冲突解决信息，显示额外提示
                if (data.conflicts_resolved > 0) {
                    assistAnswer.textContent += ` [解决了${data.conflicts_resolved}个冲突]`;
                }
            } else {
                // 处理不同类型的错误
                handleStageUpdateError(data, stage, jdyId);
            }
        })
        .catch(error => {
            console.error('推进阶段错误:', error);
            assistAnswer.textContent = `❌ 推进失败: 网络连接错误或服务不可用`;
        });
    }
    
    // 处理状态更新错误
    function handleStageUpdateError(data, stage, jdyId) {
        const errorType = data.error_type || 'unknown';
        const errorMessage = data.error || '未知错误';
        
        switch (errorType) {
            case 'validation':
            case 'validation_failed':
                // 状态校验失败，提供重试选项
                assistAnswer.innerHTML = `
                    ❌ 状态校验失败: ${errorMessage}<br>
                    <button onclick="updateStage('${stage}', '${jdyId}', true)" 
                            style="margin-top: 5px; padding: 4px 8px; background: #ffc107; border: none; border-radius: 3px; cursor: pointer;">
                        强制推进
                    </button>
                    <button onclick="showStageHistory('${jdyId}')" 
                            style="margin-top: 5px; margin-left: 5px; padding: 4px 8px; background: #17a2b8; color: white; border: none; border-radius: 3px; cursor: pointer;">
                        查看历史
                    </button>
                `;
                break;
                
            case 'conflict':
                // 状态冲突，提供解决选项
                assistAnswer.innerHTML = `
                    ⚠️ 状态冲突: ${errorMessage}<br>
                    <button onclick="updateStage('${stage}', '${jdyId}', true)" 
                            style="margin-top: 5px; padding: 4px 8px; background: #dc3545; color: white; border: none; border-radius: 3px; cursor: pointer;">
                        强制解决冲突
                    </button>
                    <button onclick="showStageHistory('${jdyId}')" 
                            style="margin-top: 5px; margin-left: 5px; padding: 4px 8px; background: #17a2b8; color: white; border: none; border-radius: 3px; cursor: pointer;">
                        查看详情
                    </button>
                `;
                break;
                
            case 'customer_not_found':
                assistAnswer.textContent = `❌ 未找到客户记录: ${jdyId}`;
                break;
                
            case 'file_not_found':
                assistAnswer.textContent = `❌ 数据文件不存在，请联系管理员`;
                break;
                
            default:
                assistAnswer.textContent = `❌ 推进失败: ${errorMessage}`;
        }
    }
    
    // 显示状态变更历史
    function showStageHistory(jdyId) {
        fetch(`/stage_history?jdy_id=${jdyId}&limit=10`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.history.length > 0) {
                let historyHtml = `<div style="max-height: 200px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-top: 10px; border-radius: 5px; background: #f9f9f9;"><h4>状态变更历史 (${jdyId})</h4>`;
                
                data.history.forEach(entry => {
                    const timestamp = new Date(entry.timestamp).toLocaleString('zh-CN');
                    const statusIcon = entry.success ? '✅' : '❌';
                    historyHtml += `
                        <div style="margin-bottom: 8px; padding: 5px; border-left: 3px solid ${entry.success ? '#28a745' : '#dc3545'}; background: white;">
                            <div style="font-size: 12px; color: #666;">${timestamp}</div>
                            <div>${statusIcon} ${entry.old_stage} → ${entry.new_stage}</div>
                            ${entry.error_msg ? `<div style="color: #dc3545; font-size: 12px;">${entry.error_msg}</div>` : ''}
                        </div>
                    `;
                });
                
                historyHtml += '</div>';
                assistAnswer.innerHTML = historyHtml;
            } else {
                assistAnswer.textContent = '暂无状态变更历史记录';
            }
        })
        .catch(error => {
            console.error('获取状态历史失败:', error);
            assistAnswer.textContent = '获取状态历史失败';
        });
    }
    
    // 获取未签订合同客户
    function fetchUnsignedCustomers(statusFilter = 'all') {
        const unsignedList = document.getElementById('unsignedCustomersList');
        if (!unsignedList) return;
        
        unsignedList.innerHTML = '<div class="loading" style="text-align: center; color: #666; padding: 10px;">加载中...</div>';
        
        const url = `/get_unsigned_customers?status=${statusFilter}`;
        fetch(url, {
            credentials: 'same-origin'
        })
        .then(response => {
            if (response.status === 302 || response.url.includes('/login')) {
                unsignedList.innerHTML = '<div style="text-align: center; color: #666; padding: 10px;">请先登录</div>';
                return null;
            }
            const contentType = response.headers.get('content-type');
            if (!response.ok || !contentType || !contentType.includes('application/json')) {
                throw new Error('API服务不可用');
            }
            return response.json();
        })
        .then(data => {
            if (!data) return;
            
            if (data.error) {
                unsignedList.innerHTML = `<div style="text-align: center; color: #e74c3c; padding: 10px;">${data.error}</div>`;
                return;
            }
            
            // 更新状态筛选器
            updateStatusFilter(data.available_statuses, data.current_filter);
            
            if (!data.customers || data.customers.length === 0) {
                const filterLabel = getFilterLabel(statusFilter);
                unsignedList.innerHTML = `<div style="text-align: center; color: #666; padding: 10px;">😊 最近30天内没有符合"${filterLabel}"条件的客户</div>`;
                return;
            }
            
            // 显示客户列表
            let html = `<div style="font-size: 12px; color: #666; margin-bottom: 8px; text-align: center;">共找到 ${data.total_count} 个客户 (${data.query_date}) | 当前筛选: ${getFilterLabel(data.current_filter)}</div>`;
            
            // 添加导出按钮
            html += `<div style="margin-bottom: 10px; text-align: center;">
                <button id="exportUnsignedCustomers" class="btn btn-secondary" style="padding: 5px 10px; font-size: 12px;">📊 导出所有客户列表</button>
            </div>`;
            
            data.customers.forEach(customer => {
                const stageClass = getStageClass(customer.customer_stage);
                html += `
                    <div style="border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px; margin-bottom: 6px; background: #f9f9f9;">
                        <div style="font-size: 12px; color: #e74c3c; font-weight: bold; margin-bottom: 4px;">${customer.expiry_date}</div>
                        <div style="font-size: 11px; color: #333; line-height: 1.3;">
                            <div style="margin-bottom: 2px;"><strong>公司:</strong> ${customer.company_name}</div>
                            <div style="margin-bottom: 2px;"><strong>账号:</strong> ${customer.jdy_account}</div>
                            <div style="margin-bottom: 2px;"><strong>销售:</strong> ${customer.sales_person}</div>
                            <div style="margin-bottom: 2px;"><strong>状态:</strong> <span class="${stageClass}">${customer.customer_stage}</span></div>
                            ${customer.integration_mode ? `<div style="margin-bottom: 2px;"><strong>集成模式:</strong> ${getIntegrationModeTip(customer.integration_mode)}</div>` : ''}
                        </div>
                    </div>
                `;
            });
            
            unsignedList.innerHTML = html;
            
            // 为导出按钮添加点击事件
            document.getElementById('exportUnsignedCustomers').addEventListener('click', function() {
                const exportUrl = '/export_unsigned_customers';
                window.open(exportUrl, '_blank');
            });
        })
        .catch(error => {
            console.error('获取客户数据错误:', error);
            unsignedList.innerHTML = '<div style="text-align: center; color: #e74c3c; padding: 10px;">获取数据失败，请稍后重试</div>';
        });
    }

    // 获取集成模式提醒
    function getIntegrationModeTip(mode) {
        if (!mode) return '';
        
        if (mode.includes('企微')) {
            return `<span style="color: #1890ff;">${mode} <strong>⚠️ 需在SA后台和企微平台下单</strong></span>`;
        } else if (mode.includes('钉钉')) {
            return `<span style="color: #52c41a;">${mode} <strong>✅ 仅需在钉钉后台下单</strong></span>`;
        }
        return mode;
    }

    function updateStatusFilter(availableStatuses, currentFilter) {
        const filterContainer = document.getElementById('status-filter-container');
        if (!filterContainer) return;
        
        let html = '<div class="status-filters" style="margin-bottom: 10px; text-align: center;">';
        availableStatuses.forEach(status => {
            const activeClass = status.value === currentFilter ? 'active' : '';
            const buttonStyle = status.value === currentFilter ? 
                'background: #007bff; color: white; border: 1px solid #007bff;' : 
                'background: white; color: #007bff; border: 1px solid #007bff;';
            html += `<button class="filter-btn ${activeClass}" data-filter="${status.value}"
                style="${buttonStyle} padding: 4px 8px; margin: 2px; border-radius: 4px; cursor: pointer; font-size: 11px;">
                ${status.label} (${status.count})
            </button>`;
        });
        html += '</div>';
        
        filterContainer.innerHTML = html;
        
        // 添加事件监听器
        const filterButtons = filterContainer.querySelectorAll('.filter-btn');
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const filterValue = this.getAttribute('data-filter');
                fetchUnsignedCustomers(filterValue);
            });
        });
    }
    
    function getFilterLabel(filter) {
    const labels = {
        'all': '全部状态',
        'na': 'NA状态',
        'contract': '合同状态',
        'invoice': '开票状态',
        'advance_invoice': '提前开状态',
        'paid': '回款状态',
        'invalid': '无效',
        'upsell': '增购',
        'lost': '失联'
    };
    return labels[filter] || filter;
}
    
    function getStageClass(stage) {
    if (stage === 'NA') return 'stage-na';
    if (stage.includes('合同')) return 'stage-contract';
    if (stage.includes('开票')) return 'stage-invoice';
    if (stage.includes('提前开')) return 'stage-advance-invoice';
    if (stage.includes('回款') || stage.includes('已付')) return 'stage-paid';
    if (stage.includes('无效')) return 'stage-invalid';
    if (stage.includes('增购')) return 'stage-upsell';
    if (stage.includes('失联')) return 'stage-lost';
    return 'stage-other';
}
    
    // 自动监控功能
    let statusCheckInterval = null;
    let isMonitoring = false;
    
    // 切换监控状态功能已移除（监控自动启动）
    
    // 启动自动监控
    async function startAutoMonitor() {
        if (isMonitoring) return;
        
        try {
            const response = await fetch('/start_auto_monitor', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success) {
                isMonitoring = true;
                // 停止监控按钮已移除
                document.getElementById('monitorStatusText').textContent = '后台监控中';
                
                // 开始定期检查监控状态
                startStatusCheck();
                
                console.log('后台自动监控已启动');
            } else {
                alert('启动监控失败: ' + data.error);
            }
        } catch (error) {
            console.error('启动监控失败:', error);
            alert('启动监控失败: ' + error.message);
        }
    }
    
    // 停止自动监控
    async function stopAutoMonitor() {
        if (!isMonitoring) return;
        
        try {
            const response = await fetch('/stop_auto_monitor', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success) {
                isMonitoring = false;
                // 停止监控按钮已移除
                document.getElementById('monitorStatusText').textContent = '已停止';
                
                // 停止状态检查
                stopStatusCheck();
                
                console.log('后台自动监控已停止');
            } else {
                alert('停止监控失败: ' + data.error);
            }
        } catch (error) {
            console.error('停止监控失败:', error);
            alert('停止监控失败: ' + error.message);
        }
    }
    
    // 开始状态检查
    function startStatusCheck() {
        // 立即检查一次
        checkMonitorStatus();
        
        // 每10秒检查一次状态
        statusCheckInterval = setInterval(() => {
            checkMonitorStatus();
        }, 10000);
    }
    
    // 停止状态检查
    function stopStatusCheck() {
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
            statusCheckInterval = null;
        }
    }
    
    // 检查监控状态
    async function checkMonitorStatus() {
        try {
            const response = await fetch('/get_monitor_status', {
                method: 'GET',
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success) {
                updateMonitorDisplay(data);
            }
        } catch (error) {
            console.error('检查监控状态失败:', error);
        }
    }
    
    // 初始化监控状态
    async function initializeMonitorStatus() {
        try {
            const response = await fetch('/get_monitor_status', {
                method: 'GET',
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success) {
                // 更新监控状态显示
                isMonitoring = data.enabled;
                
                const monitorStatusText = document.getElementById('monitorStatusText');
                
                if (monitorStatusText) {
                    if (data.enabled) {
                        monitorStatusText.textContent = '自动监控中';
                        monitorStatusText.style.color = '#48bb78';
                        
                        // 开始定期检查监控状态
                        startStatusCheck();
                        
                        console.log('检测到监控已自动启动');
                    } else {
                        monitorStatusText.textContent = '已停止';
                        monitorStatusText.style.color = '#666';
                    }
                }
                
                // 更新监控显示
                updateMonitorDisplay(data);
            }
        } catch (error) {
            console.error('初始化监控状态失败:', error);
        }
    }
    
    // 更新监控显示
    function updateMonitorDisplay(data) {
        const resultsElement = document.getElementById('monitorResults');
        const lastCheckElement = document.getElementById('lastCheckTime');
        
        // 更新监控状态
        if (data.enabled !== undefined) {
            isMonitoring = data.enabled;
            const monitorStatusText = document.getElementById('monitorStatusText');
            
            if (monitorStatusText) {
                if (data.enabled) {
                    monitorStatusText.textContent = '自动监控中';
                    monitorStatusText.style.color = '#48bb78';
                } else {
                    monitorStatusText.textContent = '已停止';
                    monitorStatusText.style.color = '#666';
                }
            }
        }
        
        // 更新最后检查时间
        if (data.last_check && lastCheckElement) {
            const checkTime = new Date(data.last_check);
            lastCheckElement.textContent = checkTime.toLocaleTimeString();
        }
        
        // 更新监控结果
        if (data.results && data.results.recent_contracts && resultsElement) {
            let html = '';
            
            if (data.results.recent_contracts.length > 0) {
                html += '<div style="color: #48bb78; font-weight: bold; margin-bottom: 5px;">发现合同文件:</div>';
                
                data.results.recent_contracts.forEach(contract => {
                    const updateInfo = data.results.updated_contracts.find(u => u.filename === contract.filename);
                    let statusText = '';
                    let statusColor = '#666';
                    
                    if (contract.jdy_account) {
                        if (updateInfo) {
                            if (updateInfo.status === 'updated') {
                                statusText = '✅ 已自动推进';
                                statusColor = '#48bb78';
                            } else {
                                statusText = '❌ 推进失败: ' + (updateInfo.error || '未知错误');
                                statusColor = '#f56565';
                            }
                        }
                    } else {
                        statusText = '⚠️ 未识别账号';
                        statusColor = '#ed8936';
                    }
                    
                    html += `
                        <div style="padding: 5px; border-bottom: 1px solid #eee; margin-bottom: 5px;">
                            <div style="font-weight: bold; color: #333;">${contract.filename}</div>
                            ${contract.jdy_account ? `<div style="color: #666;">账号: ${contract.jdy_account}</div>` : ''}
                            <div style="color: ${statusColor};">${statusText}</div>
                        </div>
                    `;
                });
                
                if (data.results.total_updated > 0) {
                    html += `<div style="color: #48bb78; font-weight: bold; margin-top: 5px;">成功推进 ${data.results.total_updated} 个客户到合同阶段</div>`;
                }
            } else {
                html = '<div style="color: #666; padding: 5px;">未发现新的合同文件</div>';
            }
            
            resultsElement.innerHTML = html;
        }
    }
    

    
    function askQuestion() {
        const question = assistAsk.value.trim();
        if (!question) {
            assistAnswer.textContent = '请输入问题';
            return;
        }
        
        assistAnswer.textContent = '正在思考...';
        
        // 简单的本地检索逻辑
        const savedMemos = JSON.parse(localStorage.getItem('assistMemos') || '[]');
        const matchingMemos = savedMemos.filter(memo => 
            memo.content.toLowerCase().includes(question.toLowerCase())
        );
        
        if (matchingMemos.length > 0) {
            const result = `找到${matchingMemos.length}条相关记录:\n` + 
                          matchingMemos.slice(0, 3).map(memo => `• ${memo.content} (${memo.timestamp})`).join('\n');
            assistAnswer.textContent = result;
        } else {
            assistAnswer.textContent = '暂未找到相关记录，功能开发中...';
        }
    }
    
    function clearAssistPanel() {
        assistAsk.value = '';
        assistAnswer.textContent = '提示：生成合同成功后会自动推进到"合同"。';
    }
});



// 合同生成成功后自动推进到合同阶段
function onContractGenerated(jdyId) {
    if (jdyId) {
        fetch('/update_stage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                jdy_id: jdyId,
                stage: '合同'
            })
        })
        .then(response => {
            const contentType = response.headers.get('content-type');
            if (!response.ok || !contentType || !contentType.includes('application/json')) {
                throw new Error('阶段推进服务不可用');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const assistAnswer = document.getElementById('assistAnswer');
                if (assistAnswer) {
                    assistAnswer.textContent = '✅ 合同生成成功，已自动推进到"合同"阶段';
                }
            }
        })
        .catch(error => {
            console.error('自动推进阶段错误:', error);
            const assistAnswer = document.getElementById('assistAnswer');
            if (assistAnswer) {
                assistAnswer.textContent = '⚠️ 合同生成成功，但自动推进功能暂时不可用（静态预览模式）';
            }
        });
    }
}