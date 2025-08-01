// 获取即将过期的客户信息并显示提示框
function fetchExpiringCustomers() {
    fetch('/get_expiring_customers')
        .then(response => response.json())
        .then(data => {
            const todayDate = data.today_date || new Date().toLocaleDateString('zh-CN');
            const reminderType = data.reminder_type || '';
            
            if (data.message) {
                // 如果有消息（比如周末提示或没有到期客户），显示消息
                showExpiringCustomersAlert([], data.message, todayDate, reminderType);
            } else if (data.expiring_customers && data.expiring_customers.length > 0) {
                // 有到期客户，显示列表
                showExpiringCustomersAlert(data.expiring_customers, null, todayDate, reminderType);
            } else if (data.error) {
                // 有错误但不显示技术错误，只显示友好提示
                showExpiringCustomersAlert([], '暂时无法获取客户信息', todayDate, reminderType);
            } else {
                // 默认情况：没有到期客户
                showExpiringCustomersAlert([], '😊 近期没有客户到期', todayDate, reminderType);
            }
        })
        .catch(error => {
            console.error('获取即将过期客户错误:', error);
            // 不显示技术错误，只显示友好提示
            const todayDate = new Date().toLocaleDateString('zh-CN');
            showExpiringCustomersAlert([], '暂时无法获取客户信息', todayDate, '系统错误');
        });
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

function showExpiringCustomersAlert(customers, message = null, todayDate = '', reminderType = '') {
    // 如果已经存在提示框，先移除
    const existingAlert = document.getElementById('expiring-customers-alert');
    if (existingAlert) {
        existingAlert.remove();
    }

    // 创建提示框（使用原来的CSS类名和样式）
    const alertDiv = document.createElement('div');
    alertDiv.id = 'expiring-customers-alert';
    alertDiv.className = 'expiring-customers-alert';

    // 创建头部（保持原来的结构）
    const headerDiv = document.createElement('div');
    headerDiv.className = 'expiring-customers-header';
    headerDiv.style.display = 'flex';
    headerDiv.style.justifyContent = 'space-between';
    headerDiv.style.alignItems = 'center';
    headerDiv.style.padding = '12px 15px';
    headerDiv.style.backgroundColor = 'var(--secondary-color)';
    headerDiv.style.borderRadius = '8px 8px 0 0';
    headerDiv.style.borderBottom = '1px solid var(--border-color)';

    const titleDiv = document.createElement('h4');
    titleDiv.style.margin = '0';
    titleDiv.style.color = 'var(--text-color)';  // 改为黑色，与备忘录标题一致
    titleDiv.style.fontSize = '14px';
    titleDiv.style.fontWeight = '600';
    titleDiv.textContent = `📅 ${todayDate} - 提醒看板`;  // 简化标题内容

    const closeBtn = document.createElement('button');
    closeBtn.className = 'close-btn';
    closeBtn.textContent = '×';
    closeBtn.onclick = function() {
        alertDiv.remove();
    };

    headerDiv.appendChild(titleDiv);
    headerDiv.appendChild(closeBtn);

    // 创建内容区域（保持原来的结构）
    const bodyDiv = document.createElement('div');
    bodyDiv.className = 'expiring-customers-body';

    if (message) {
        // 显示消息（周末提示或没有到期客户）
        const messageDiv = document.createElement('div');
        messageDiv.className = 'expiring-customer-item';
        messageDiv.innerHTML = `
            <div style="display: flex; align-items: center; padding: 8px 0;">
                <span style="margin-right: 8px;">ℹ️</span>
                <span style="color: var(--text-color); font-size: 14px;">${message}</span>
            </div>
        `;
        bodyDiv.appendChild(messageDiv);
    } else if (customers && customers.length > 0) {
        // 显示到期客户列表
        customers.forEach(customer => {
            const customerDiv = document.createElement('div');
            customerDiv.className = 'expiring-customer-item';
            customerDiv.innerHTML = `
                <div class="expiring-customer-date">${customer.expiry_date}</div>
                <div style="font-size: 13px; color: var(--text-color); line-height: 1.4;">
                    <div>公司：${customer.company_name}</div>
                    <div>账号：${customer.jdy_account}</div>
                    <div>销售：${customer.sales_person}</div>
                </div>
            `;
            bodyDiv.appendChild(customerDiv);
        });
    } else {
        // 默认情况：没有到期客户
        const noCustomerDiv = document.createElement('div');
        noCustomerDiv.className = 'expiring-customer-item';
        noCustomerDiv.innerHTML = `
            <div style="display: flex; align-items: center; padding: 8px 0;">
                <span style="margin-right: 8px;">😊</span>
                <span style="color: var(--text-color); font-size: 14px;">近期没有客户到期</span>
            </div>
        `;
        bodyDiv.appendChild(noCustomerDiv);
    }

    // 组装提示框
    alertDiv.appendChild(headerDiv);
    alertDiv.appendChild(bodyDiv);
    document.body.appendChild(alertDiv);

    // 看板一直存在，不自动关闭
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

    const memoTextarea = document.createElement('textarea');
    memoTextarea.className = 'memo-textarea';
    memoTextarea.placeholder = '在这里记录您的备忘事项...\n\n• 待办事项\n• 重要提醒\n• 工作笔记\n• 客户跟进';
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
        fetchExpiringCustomers();
        // 显示备忘录白板（替代原来的25-30天到期客户看板）
        showFutureExpiringCustomersDashboard([], []);
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
    .then(response => response.json())
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
        showAutoFillError('网络请求失败，请检查网络连接');
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
    .then(response => response.json())
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
    });
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
    .then(response => response.json())
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
        document.getElementById('integrationMode').textContent = data.integration_mode || '暂无数据';
        document.getElementById('expiryDate').textContent = data.expiry_date || '暂无数据';
        document.getElementById('uidArr').textContent = data.uid_arr || '0元';
        document.getElementById('customerClassification').textContent = data.customer_classification || '暂无数据';
        document.getElementById('salesPerson').textContent = data.sales || '暂无数据';
        document.getElementById('salesCnEn').textContent = data.sales_cn_en || '暂无数据';
        document.getElementById('jdySales').textContent = data.jdy_sales || '暂无数据';
        
        // 显示结果区域
        document.getElementById('customerInfo').style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('查询失败，请稍后重试');
    });
}