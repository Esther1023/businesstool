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
        'btn-hetiao': 'https://bi.finereporthelp.com/webroot/decision?#/directory?activeTab=4a3d1d52-2e58-4e0c-bb82-722b1a8bc6bf',  // 业绩进度链接
        'btn-sa': 'https://sa.jiandaoyun.com/',      // SA链接
        'btn-huikuan': 'https://bi.jdydevelop.com/webroot/decision#/?activeTab=6ed7a7e6-70b0-4814-9424-35d784d8e686',  // 回款链接
        'btn-xiadan': 'https://bi.jdydevelop.com/webroot/decision#/?activeTab=6ed7a7e6-70b0-4814-9424-35d784d8e686',   // 接口链接
        'btn-qiwei': 'https://kms.jiandaoyun.com/',                                           // kms链接
        'btn-daike': 'https://bi.finereporthelp.com/webroot/decision?#/directory?activeTab=12d9701c-b4b7-4ae7-b37f-ff3d418f4b8a'    // 客户归属链接
    };
    
    // 内联快捷按钮的链接配置（与顶部快捷按钮使用相同的链接）
    const inlineShortcutLinks = {
        'btn-hetiao-inline': 'https://bi.finereporthelp.com/webroot/decision?#/directory?activeTab=4a3d1d52-2e58-4e0c-bb82-722b1a8bc6bf',  // 业绩进度链接
        'btn-sa-inline': 'https://sa.jiandaoyun.com/',      // SA链接
        'btn-huikuan-inline': 'https://bi.jdydevelop.com/webroot/decision#/?activeTab=6ed7a7e6-70b0-4814-9424-35d784d8e686',  // 回款链接
        'btn-xiadan-inline': 'https://bi.jdydevelop.com/webroot/decision#/?activeTab=6ed7a7e6-70b0-4814-9424-35d784d8e686',   // 接口链接
        'btn-qiwei-inline': 'https://kms.jiandaoyun.com/',      // kms链接
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
    const parseBtn = document.getElementById('parseClipboardBtn');
    const clearBtn = document.getElementById('clearClipboardBtn');
    
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
    
    // 解析按钮事件
    if (parseBtn) {
        parseBtn.addEventListener('click', function() {
            const text = clipboardTextarea.value.trim();
            if (text) {
                parseClipboardText(text);
            } else {
                alert('请先输入要解析的文本内容');
            }
        });
    }
    
    // 清空按钮事件
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            clipboardTextarea.value = '';
            clipboardTextarea.style.display = 'none';
            clipboardContent.style.display = 'flex';
            const clipboardResult = document.getElementById('clipboardResult');
            if (clipboardResult) {
                clipboardResult.style.display = 'none';
            }
        });
    }
    
    // 支持粘贴事件
    clipboardTextarea.addEventListener('paste', function(e) {
        setTimeout(() => {
            if (clipboardTextarea.value.trim()) {
                parseClipboardText(clipboardTextarea.value.trim());
            }
        }, 100);
    });
}

// 解析粘贴板文本
function parseClipboardText(text) {
    // 显示解析进度
    const resultDiv = document.getElementById('clipboardResult');
    const parsedFieldsDiv = document.getElementById('parsedFields');
    
    if (!resultDiv || !parsedFieldsDiv) return;
    
    resultDiv.style.display = 'block';
    parsedFieldsDiv.innerHTML = '<div style="text-align: center; padding: 20px;">正在解析文本...</div>';
    
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
        if (data.success) {
            displayParsedFields(data.fields);
        } else {
            parsedFieldsDiv.innerHTML = `
                <div style="text-align: center; padding: 20px; color: var(--error-color);">
                    解析失败：${data.error || '未知错误'}
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('解析文本错误:', error);
        parsedFieldsDiv.innerHTML = `
            <div style="text-align: center; padding: 20px; color: var(--error-color);">
                解析失败，请检查网络连接
            </div>
        `;
    });
}

// 显示解析结果
function displayParsedFields(fields) {
    const parsedFieldsDiv = document.getElementById('parsedFields');
    
    if (!parsedFieldsDiv) return;
    
    if (Object.keys(fields).length === 0) {
        parsedFieldsDiv.innerHTML = `
            <div style="text-align: center; padding: 20px; color: var(--dark-gray);">
                未识别到相关字段，请检查文本内容
            </div>
        `;
        return;
    }
    
    const fieldLabels = {
        'company_name': '公司名称',
        'tax_number': '税号',
        'reg_address': '注册地址',
        'reg_phone': '注册电话',
        'bank_name': '开户行',
        'bank_account': '账号',
        'contact_name': '联系人',
        'contact_phone': '联系电话',
        'mail_address': '邮寄地址',
        'jdy_account': '简道云账号'
    };
    
    let html = '';
    for (const [fieldName, value] of Object.entries(fields)) {
        const label = fieldLabels[fieldName] || fieldName;
        html += `
            <div class="parsed-field-item">
                <div>
                    <div class="field-label">${label}</div>
                    <div class="field-value">${value}</div>
                </div>
                <button class="field-apply-btn" onclick="applyFieldValue('${fieldName}', '${value.replace(/'/g, "\\'")}')">
                    应用
                </button>
            </div>
        `;
    }
    
    parsedFieldsDiv.innerHTML = html;
}

// 应用字段值到表单
function applyFieldValue(fieldName, value) {
    const input = document.getElementById(fieldName);
    if (input) {
        input.value = value;
        input.classList.add('auto-filled');
        
        // 移除高亮效果
        setTimeout(() => {
            input.classList.remove('auto-filled');
        }, 2000);
        
        // 触发输入事件（用于公司名称搜索等）
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }
}

// 增强OCR功能
function enhanceOCRFeature() {
    const retryBtn = document.getElementById('retryOcrBtn');
    const applyBtn = document.getElementById('applyOcrBtn');
    const editBtn = document.getElementById('editOcrBtn');
    
    // OCR图片上传处理
    const imageUpload = document.getElementById('imageUpload');
    if (imageUpload) {
        imageUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const previewImage = document.getElementById('previewImage');
                    const imagePreview = document.getElementById('imagePreview');
                    
                    // 显示图片预览
                    previewImage.src = e.target.result;
                    imagePreview.style.display = 'block';
                    
                    // 自动开始OCR识别
                    processImageForOCR(e.target.result);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // 拖拽上传功能
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type.startsWith('image/')) {
                    document.getElementById('imageUpload').files = files;
                    document.getElementById('imageUpload').dispatchEvent(new Event('change'));
                } else {
                    alert('请上传图片文件');
                }
            }
        });
    }
    
    // 重新识别按钮
    if (retryBtn) {
        retryBtn.addEventListener('click', function() {
            const previewImage = document.getElementById('previewImage');
            if (previewImage && previewImage.src) {
                // 重新触发OCR识别
                processImageForOCR(previewImage.src);
            }
        });
    }
    
    // 应用识别结果按钮
    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            const ocrText = document.getElementById('ocrText');
            if (ocrText && ocrText.textContent) {
                parseClipboardText(ocrText.textContent);
            }
        });
    }
    
    // 手动编辑按钮
    if (editBtn) {
        editBtn.addEventListener('click', function() {
            const ocrText = document.getElementById('ocrText');
            const clipboardTextarea = document.getElementById('clipboardTextarea');
            const clipboardContent = document.querySelector('.clipboard-content');
            
            if (ocrText && clipboardTextarea && clipboardContent) {
                // 将OCR结果复制到粘贴板区域
                clipboardTextarea.value = ocrText.textContent;
                clipboardTextarea.style.display = 'block';
                clipboardContent.style.display = 'none';
                clipboardTextarea.focus();
            }
        });
    }
}

// 处理图片OCR识别
function processImageForOCR(imageSrc) {
    const ocrProgress = document.getElementById('ocrProgress');
    const ocrResult = document.getElementById('ocrResult');
    const ocrText = document.getElementById('ocrText');
    
    if (!ocrProgress || !ocrResult || !ocrText) return;
    
    // 显示进度
    ocrProgress.style.display = 'block';
    ocrResult.style.display = 'none';
    
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
            ocrText.textContent = data.text || '未识别到文字内容';
            ocrResult.style.display = 'block';
        } else {
            ocrText.textContent = `识别失败：${data.error || '未知错误'}`;
            ocrResult.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('OCR识别错误:', error);
        ocrProgress.style.display = 'none';
        ocrText.textContent = '识别失败，请检查网络连接或尝试其他图片';
        ocrResult.style.display = 'block';
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