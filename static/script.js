// 全局变量声明
let isMonitoring = false;

// 安全JSON获取与静态预览检测
function isStaticPreview() {
  try {
    const isTemplates = window.location.pathname.includes('/templates/');
    const isHttpServer = String(window.location.port || '') === '8081';
    return isTemplates || isHttpServer;
  } catch (_) {
    return false;
  }
}

async function safeJsonFetch(url, options = {}, fallbackData = {}) {
  try {
    const response = await fetch(url, options);
    const contentType = response.headers ? (response.headers.get('content-type') || '') : '';
    if (!response.ok || !contentType.includes('application/json')) {
      return { ...fallbackData, _static_preview: true };
    }
    return await response.json();
  } catch (error) {
    return { ...fallbackData, _static_preview: true, error: error && error.message ? error.message : String(error) };
  }
}

// 简单的API错误记录器，便于后续监控与排查
function logApiError(endpoint, error) {
  if (!error) return;
  try {
    window._apiErrors = window._apiErrors || [];
    window._apiErrors.push({
      endpoint,
      error: typeof error === 'string' ? error : (error && error.message) ? error.message : String(error),
      time: new Date().toISOString(),
      page: window.location.pathname
    });
  } catch (_) {}
  console.error('API调用错误:', endpoint, error);

  // 将错误上报到后端日志/监控系统
  try {
    if (!isStaticPreview()) {
      const payload = {
        errors: window._apiErrors.slice(-1),
        ua: navigator.userAgent,
        page: window.location.pathname
      };
      fetch('/log_client_error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(payload)
      }).catch(() => {});
    }
  } catch (_) {}

  // 轻量聚合：延迟批量上报最近错误，避免频繁请求
  try {
    clearTimeout(window._errorFlushTimer);
    window._errorFlushTimer = setTimeout(() => {
      if (isStaticPreview()) return;
      const errs = (window._apiErrors || []).slice(-20);
      if (!errs.length) return;
      fetch('/log_client_error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ errors: errs, ua: navigator.userAgent, page: window.location.pathname })
      }).catch(() => {});
    }, 1000);
  } catch (_) {}
}

// 显示销售代表筛选模态框
function showSalesFilterModal(type) {
    // 移除现有模态框
    const existingModal = document.getElementById('salesFilterModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 创建模态框背景
    const modalBackdrop = document.createElement('div');
    modalBackdrop.id = 'salesFilterModal';
    modalBackdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 10000;
        display: flex;
        justify-content: center;
        align-items: center;
    `;
    
    // 创建模态框内容
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        border-radius: 8px;
        padding: 20px;
        width: 300px;
        max-height: 400px;
        overflow-y: auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    `;
    
    // 模态框标题
    const title = document.createElement('h3');
    title.textContent = '选择销售代表';
    title.style.cssText = `
        margin: 0 0 15px 0;
        color: #333;
        text-align: center;
    `;
    
    // 加载中提示
    const loading = document.createElement('div');
    loading.textContent = '正在加载销售代表列表...';
    loading.style.cssText = `
        text-align: center;
        color: #666;
        padding: 20px;
    `;
    
    modalContent.appendChild(title);
    modalContent.appendChild(loading);
    modalBackdrop.appendChild(modalContent);
    document.body.appendChild(modalBackdrop);
    
    // 点击背景关闭模态框
    modalBackdrop.addEventListener('click', function(e) {
        if (e.target === modalBackdrop) {
            modalBackdrop.remove();
        }
    });
    
    // 获取销售代表列表
    fetch('/get_sales_representatives')
        .then(response => response.json())
        .then(data => {
            loading.remove();
            
            if (data.error) {
                const errorDiv = document.createElement('div');
                errorDiv.textContent = '获取销售代表列表失败: ' + data.error;
                errorDiv.style.color = '#e74c3c';
                errorDiv.style.textAlign = 'center';
                modalContent.appendChild(errorDiv);
                return;
            }
            
            // 创建销售代表选项
            const salesList = data.sales_representatives || [];
            
            // 添加"全部"选项
            const allOption = document.createElement('button');
            allOption.textContent = '全部';
            allOption.style.cssText = `
                width: 100%;
                padding: 10px;
                margin: 5px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: #f8f9fa;
                cursor: pointer;
                font-size: 14px;
            `;
            allOption.addEventListener('click', function() {
                applySalesFilter('all', type);
                modalBackdrop.remove();
            });
            modalContent.appendChild(allOption);
            
            // 添加具体销售代表选项
            salesList.forEach(salesName => {
                if (salesName && salesName.trim()) {
                    const option = document.createElement('button');
                    option.textContent = salesName;
                    option.style.cssText = `
                        width: 100%;
                        padding: 10px;
                        margin: 5px 0;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        background: white;
                        cursor: pointer;
                        font-size: 14px;
                    `;
                    option.addEventListener('mouseenter', function() {
                        this.style.background = '#e9ecef';
                    });
                    option.addEventListener('mouseleave', function() {
                        this.style.background = 'white';
                    });
                    option.addEventListener('click', function() {
                        applySalesFilter(salesName, type);
                        modalBackdrop.remove();
                    });
                    modalContent.appendChild(option);
                }
            });
            
            // 添加关闭按钮
            const closeBtn = document.createElement('button');
            closeBtn.textContent = '取消';
            closeBtn.style.cssText = `
                width: 100%;
                padding: 10px;
                margin: 10px 0 0 0;
                border: 1px solid #6c757d;
                border-radius: 4px;
                background: #6c757d;
                color: white;
                cursor: pointer;
                font-size: 14px;
            `;
            closeBtn.addEventListener('click', function() {
                modalBackdrop.remove();
            });
            modalContent.appendChild(closeBtn);
        })
        .catch(error => {
            loading.remove();
            const errorDiv = document.createElement('div');
            errorDiv.textContent = '网络错误，请稍后重试';
            errorDiv.style.color = '#e74c3c';
            errorDiv.style.textAlign = 'center';
            modalContent.appendChild(errorDiv);
        });
}

// 显示战区多选筛选模态框（用于未来30天客户看板）
function showZonesFilterModal() {
    // 移除现有模态框
    const existingModal = document.getElementById('zonesFilterModal');
    if (existingModal) {
        existingModal.remove();
    }

    // 创建模态框背景
    const modalBackdrop = document.createElement('div');
    modalBackdrop.id = 'zonesFilterModal';
    modalBackdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 10000;
        display: flex;
        justify-content: center;
        align-items: center;
    `;

    // 创建模态框内容
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        border-radius: 8px;
        padding: 16px;
        width: 340px;
        max-height: 420px;
        overflow-y: auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    `;

    // 模态框标题
    const title = document.createElement('h3');
    title.textContent = '选择战区（可多选）';
    title.style.cssText = `
        margin: 0 0 10px 0;
        color: #333;
        text-align: center;
        font-size: 16px;
    `;

    // 加载中提示
    const loading = document.createElement('div');
    loading.textContent = '正在加载战区列表...';
    loading.style.cssText = `
        text-align: center;
        color: #666;
        padding: 20px;
    `;

    modalContent.appendChild(title);
    modalContent.appendChild(loading);
    modalBackdrop.appendChild(modalContent);
    document.body.appendChild(modalBackdrop);

    // 点击背景关闭模态框
    modalBackdrop.addEventListener('click', function(e) {
        if (e.target === modalBackdrop) {
            modalBackdrop.remove();
        }
    });

    // 获取战区列表
    fetch('/get_zones')
        .then(response => response.json())
        .then(data => {
            loading.remove();

            const zones = Array.isArray(data) ? data : (data.zones || []);
            if (!zones || zones.length === 0) {
                const emptyDiv = document.createElement('div');
                emptyDiv.textContent = '未获取到战区列表';
                emptyDiv.style.cssText = 'text-align:center;color:#e74c3c;padding:10px;';
                modalContent.appendChild(emptyDiv);
                return;
            }

            // 选项容器
            const listContainer = document.createElement('div');
            listContainer.style.cssText = 'margin: 8px 0;';

            const current = Array.isArray(window._selectedZones) ? window._selectedZones : [];

            zones.forEach(zone => {
                if (!zone || !String(zone).trim()) return;
                const label = document.createElement('label');
                label.style.cssText = 'display:flex;align-items:center;gap:8px;padding:6px;border:1px solid #eee;border-radius:6px;margin-bottom:6px;background:#fff;';
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = zone;
                checkbox.checked = current.includes(zone);
                const span = document.createElement('span');
                span.textContent = zone;
                label.appendChild(checkbox);
                label.appendChild(span);
                listContainer.appendChild(label);
            });

            modalContent.appendChild(listContainer);

            // 操作按钮区域
            const actions = document.createElement('div');
            actions.style.cssText = 'display:flex;gap:8px;margin-top:8px;';

            const btnSelectAll = document.createElement('button');
            btnSelectAll.textContent = '全选';
            btnSelectAll.style.cssText = 'flex:1;padding:8px;border:1px solid #ddd;border-radius:6px;background:#f8f9fa;cursor:pointer;';
            btnSelectAll.addEventListener('click', function() {
                modalContent.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = true);
            });

            const btnClear = document.createElement('button');
            btnClear.textContent = '清除';
            btnClear.style.cssText = 'flex:1;padding:8px;border:1px solid #ddd;border-radius:6px;background:#fff;cursor:pointer;';
            btnClear.addEventListener('click', function() {
                modalContent.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
            });

            const btnApply = document.createElement('button');
            btnApply.textContent = '应用筛选';
            btnApply.style.cssText = 'flex:1;padding:8px;border:1px solid #007bff;border-radius:6px;background:#007bff;color:#fff;cursor:pointer;';
            btnApply.addEventListener('click', function() {
                const selected = Array.from(modalContent.querySelectorAll('input[type="checkbox"]'))
                    .filter(cb => cb.checked)
                    .map(cb => cb.value);
                applyZoneFilter(selected);
                modalBackdrop.remove();
            });

            const btnCancel = document.createElement('button');
            btnCancel.textContent = '取消';
            btnCancel.style.cssText = 'flex:1;padding:8px;border:1px solid #6c757d;border-radius:6px;background:#6c757d;color:#fff;cursor:pointer;';
            btnCancel.addEventListener('click', function() {
                modalBackdrop.remove();
            });

            actions.appendChild(btnSelectAll);
            actions.appendChild(btnClear);
            actions.appendChild(btnApply);
            actions.appendChild(btnCancel);
            modalContent.appendChild(actions);
        })
        .catch(error => {
            loading.remove();
            const errorDiv = document.createElement('div');
            errorDiv.textContent = '网络错误，请稍后重试';
            errorDiv.style.color = '#e74c3c';
            errorDiv.style.textAlign = 'center';
            modalContent.appendChild(errorDiv);
        });
}

// 应用战区筛选
function applyZoneFilter(zones) {
    window._selectedZones = Array.isArray(zones) ? zones : [];
    fetchFutureCustomersWithZones(window._selectedZones);
}

// 获取筛选后的未来30天客户（按战区，多选）
function fetchFutureCustomersWithZones(selectedZones = []) {
    let url = '/get_future_expiring_customers';
    if (Array.isArray(selectedZones) && selectedZones.length > 0) {
        const zonesParam = encodeURIComponent(selectedZones.join(','));
        url += `?zones=${zonesParam}`;
    }

    const fallback = { future_customers: [], _static_preview: true };

    // 显示加载状态
    const unsignedList = document.getElementById('unsignedCustomersList');
    if (unsignedList) {
        unsignedList.innerHTML = '<div class="loading">加载中...</div>';
    }

    safeJsonFetch(url, { credentials: 'same-origin' }, fallback)
        .then(data => {
            const errorMsg = data && data.error ? data.error : (data && data._static_preview ? '静态预览：后端未连接' : '');
            if (errorMsg) {
                logApiError(url, errorMsg);
            }
            const customers = (data && Array.isArray(data.future_customers)) ? data.future_customers : [];
            updateFutureCustomersDisplayWithZones(customers, selectedZones);
        });
}

// 更新未来30天客户看板显示（按战区）
// 辅助：格式化到期日期标签（为未来30天看板补充“多少天后到期”）
function formatExpiryLabel(dateStr) {
    try {
        if (!dateStr) return '';
        // 如果后端已经提供了“多少天后到期”标签，则直接返回
        if (dateStr.includes('天后到期') || dateStr.includes('今天到期') || dateStr.includes('明天到期')) {
            return dateStr;
        }
        const m = dateStr.match(/(\d{4})年(\d{1,2})月(\d{1,2})日/);
        if (!m) return dateStr;
        const year = parseInt(m[1], 10);
        const month = parseInt(m[2], 10) - 1;
        const day = parseInt(m[3], 10);
        const d = new Date(year, month, day);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        d.setHours(0, 0, 0, 0);
        const diffMs = d - today;
        const days = Math.round(diffMs / 86400000);
        let label = '';
        if (days === 0) label = '今天到期';
        else if (days === 1) label = '明天到期';
        else label = `${days}天后到期`;
        return `${label} (${dateStr})`;
    } catch (e) {
        return dateStr;
    }
}
function updateFutureCustomersDisplayWithZones(customers, selectedZones = []) {
    const unsignedList = document.getElementById('unsignedCustomersList');
    if (!unsignedList) return;

    const hasSelection = Array.isArray(selectedZones) && selectedZones.length > 0;
    const filterLabel = hasSelection ? selectedZones.join('，') : '全部战区';

    if (customers.length === 0) {
        unsignedList.innerHTML = `<div style="text-align: center; color: var(--text-color); padding: 10px;">😊 ${filterLabel}内没有未来8-33天内到期的客户</div>`;
        return;
    }

    let html = '';

    

    customers.forEach(customer => {
        const expiryLabel = formatExpiryLabel(customer.expiry_date);
        html += `
            <div style="border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px; margin-bottom: 6px; background: #f9f9f9;">
                <div style="font-size: 12px; color: #e74c3c; font-weight: bold; margin-bottom: 4px;">${expiryLabel}</div>
                <div style="font-size: 11px; color: #333; line-height: 1.3;">
                    <div style="margin-bottom: 2px;"><strong>公司:</strong> ${customer.company_name}</div>
                    <div style="margin-bottom: 2px;"><strong>账号:</strong> ${customer.jdy_account}</div>
                    ${customer.zone ? `<div style=\"margin-bottom: 2px;\"><strong>战区:</strong> ${customer.zone}</div>` : ''}
                    <div style="margin-bottom: 2px;"><strong>金额:</strong> ${customer.amount || customer.uid_arr || customer.contract_amount || ''}</div>
                </div>
            </div>
        `;
    });

    unsignedList.innerHTML = html;
}

// 应用销售代表筛选
function applySalesFilter(salesName, type) {
    if (type === 'expiring') {
        // 为到期客户提醒看板应用筛选
        fetchExpiringCustomersWithFilter(salesName);
    } else if (type === 'future') {
        // 为未来30天客户看板应用筛选
        fetchFutureCustomersWithFilter(salesName);
    }
}

// 获取筛选后的到期客户（静态预览友好）
function fetchExpiringCustomersWithFilter(salesFilter) {
    const url = `/get_expiring_customers?sales_filter=${encodeURIComponent(salesFilter)}`;
    const fallback = {
        expiring_customers: [],
        reminder_type: 'daily',
        today_date: new Date().toISOString().slice(0,10),
        message: `静态预览模式：后端未启动，${salesFilter==='all'?'暂无到期客户数据':`${salesFilter}负责的客户暂无到期客户`}`
    };

    // 预加载指示：如有现存看板，先显示统一的加载状态
    const sc = document.getElementById('smart-calculator');
    if (sc) {
        const contentEl = sc.querySelector('.calculator-display');
        if (contentEl) contentEl.innerHTML = '<div class="loading">加载中...</div>';
    }

    safeJsonFetch(url, { credentials: 'same-origin' }, fallback)
        .then(data => {
            if (!data) return;
            if (data.error) {
                logApiError(url, data.error);
                showExpiringCustomersAlert([], fallback.reminder_type, fallback.today_date, '暂时无法获取到期客户数据');
                return;
            }
            const customers = data.expiring_customers || [];
            const message = customers.length === 0 ? 
                (data.message || `😊 ${salesFilter === 'all' ? '今天' : salesFilter + '负责的客户中'}没有即将到期的客户`) : '';
            // 静态预览也记录一次日志，便于确认前端行为
            if (data._static_preview) {
                logApiError(url, '静态预览：后端未连接');
            }
            showExpiringCustomersAlert(customers, data.reminder_type || fallback.reminder_type, data.today_date || fallback.today_date, message);
        });
}

// 获取筛选后的未来30天客户（静态预览友好）
function fetchFutureCustomersWithFilter(salesFilter) {
    const url = `/get_future_expiring_customers?sales_filter=${encodeURIComponent(salesFilter)}`;
    const fallback = { future_customers: [], _static_preview: true };

    // 显示加载状态
    const unsignedList = document.getElementById('unsignedCustomersList');
    if (unsignedList) {
        unsignedList.innerHTML = '<div class="loading">加载中...</div>';
    }

    safeJsonFetch(url, { credentials: 'same-origin' }, fallback)
        .then(data => {
            const errorMsg = data && data.error ? data.error : (data && data._static_preview ? '静态预览：后端未连接' : '');
            if (errorMsg) {
                logApiError(url, errorMsg);
            }
            // 更新未来30天客户看板显示（出错或静态预览时显示空列表提示）
            updateFutureCustomersDisplay((data && Array.isArray(data.future_customers)) ? data.future_customers : [], salesFilter);
        });
}

// 更新未来30天客户看板显示
function updateFutureCustomersDisplay(customers, salesFilter) {
    const unsignedList = document.getElementById('unsignedCustomersList');
    if (!unsignedList) return;
    
    if (customers.length === 0) {
        const filterLabel = salesFilter === 'all' ? '全部' : salesFilter;
        unsignedList.innerHTML = `<div style="text-align: center; color: var(--text-color); padding: 10px;">😊 ${filterLabel}负责的客户中没有未来8-33天内到期的客户</div>`;
        return;
    }
    
    let html = '';
    
    // 添加筛选提示
    if (salesFilter !== 'all') {
        html += `<div style="background: #e3f2fd; padding: 8px; margin-bottom: 10px; border-radius: 4px; text-align: center; font-size: 12px; color: #1976d2;">
            当前筛选：${salesFilter} (${customers.length}个客户)
        </div>`;
    }
    
    customers.forEach(customer => {
        const expiryLabel = formatExpiryLabel(customer.expiry_date);
        html += `
            <div style="border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px; margin-bottom: 6px; background: #f9f9f9;">
                <div style="font-size: 12px; color: #e74c3c; font-weight: bold; margin-bottom: 4px;">${expiryLabel}</div>
                <div style="font-size: 11px; color: #333; line-height: 1.3;">
                    <div style="margin-bottom: 2px;"><strong>公司:</strong> ${customer.company_name}</div>
                    <div style="margin-bottom: 2px;"><strong>账号:</strong> ${customer.jdy_account}</div>
                    ${customer.zone ? `<div style=\"margin-bottom: 2px;\"><strong>战区:</strong> ${customer.zone}</div>` : ''}
                    <div style="margin-bottom: 2px;"><strong>金额:</strong> ${customer.amount || customer.uid_arr || customer.contract_amount || ''}</div>
                    ${customer.customer_stage && customer.customer_stage !== 'NA' ? `<div style=\"margin-bottom: 2px;\"><strong>状态:</strong> ${customer.customer_stage}</div>` : ''}
                </div>
            </div>
        `;
    });
    
    unsignedList.innerHTML = html;
}

// 获取即将到期的客户并显示提醒看板（静态预览友好）
function fetchExpiringCustomers() {
    safeJsonFetch('/get_expiring_customers', { credentials: 'same-origin' }, {
        expiring_customers: [],
        reminder_type: 'daily',
        today_date: new Date().toISOString().slice(0,10),
        message: '静态预览模式：API未启动，暂无到期客户数据'
    })
    .then(data => {
        if (!data) return;
        if (data.error) {
            // 在UI上提示，不抛错，同时记录错误
            logApiError('/get_expiring_customers', data.error);
            showExpiringCustomersAlert([], data.reminder_type, data.today_date, '暂时无法获取到期客户数据');
            return;
        }
        if (data._static_preview) {
            logApiError('/get_expiring_customers', '静态预览：后端未连接');
        }
        if (data.expiring_customers && data.expiring_customers.length > 0) {
            showExpiringCustomersAlert(data.expiring_customers, data.reminder_type, data.today_date);
        } else {
            const msg = data.message || '今天没有即将到期的客户';
            showExpiringCustomersAlert([], data.reminder_type, data.today_date, msg);
        }
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
    
    // 检查用户是否已登录（通过检查页面上的元素判断）
    if (document.getElementById('contractForm')) {
        console.log('页面已加载，开始初始化...');
        
        // Giko 销售页不显示到期客户看板；其他页面保留
        if (!document.body.classList.contains('theme-giko-dark')) {
            createExpiringCustomersReminder();
        }
        
        // 延迟显示备忘录白板
        setTimeout(() => {
            if (typeof showFutureExpiringCustomersDashboard === 'function') {
                showFutureExpiringCustomersDashboard([], []);
            }
        }, 500);
    }
});

// 显示即将到期客户提醒看板（替代计算器）
function showExpiringCustomersAlert(customers, reminderType, todayDate, message, selectedZones = []) {
    customers = customers || [];
    reminderType = reminderType || '';
    todayDate = todayDate || '';
    message = message || '';
    selectedZones = Array.isArray(selectedZones) ? selectedZones : [];
    
    // 检查是否已存在提醒看板，如果存在则移除
    const existingAlert = document.getElementById('smart-calculator');
    if (existingAlert) {
        existingAlert.remove();
    }

    // 创建提醒看板容器（使用计算器的ID和样式）
    const alertContainer = document.createElement('div');
    alertContainer.id = 'smart-calculator';
    alertContainer.className = 'smart-calculator';

    // 创建标题栏
    const alertHeader = document.createElement('div');
    alertHeader.className = 'calculator-header';
    
    const titleSpan = document.createElement('span');
    titleSpan.textContent = '📅 到期客户提醒';
    
    // 添加筛选按钮（使用高对比度样式类）
    const filterBtn = document.createElement('button');
    filterBtn.textContent = '🔍 筛选（战区）';
    filterBtn.className = 'calculator-filter-btn';
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'close-btn';
    closeBtn.textContent = '×';
    closeBtn.style.background = 'none';
    closeBtn.style.border = 'none';
    closeBtn.style.color = '#fff';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.fontSize = '18px';
    
    // 网格布局：左侧筛选，中间标题，右侧关闭
    alertHeader.style.display = 'grid';
    alertHeader.style.gridTemplateColumns = 'auto 1fr auto';
    alertHeader.style.alignItems = 'center';

    alertHeader.appendChild(filterBtn);
    alertHeader.appendChild(titleSpan);
    alertHeader.appendChild(closeBtn);

    // 标题在网格中居中，不受左右按钮宽度影响
    titleSpan.style.justifySelf = 'center';
    titleSpan.style.color = '#1f2a37';

    // 关闭按钮颜色与标题一致，避免过白
    closeBtn.style.color = '#1f2a37';

    // 创建内容区域
    const alertContent = document.createElement('div');
    alertContent.className = 'calculator-display';
    alertContent.style.padding = '15px';
    alertContent.style.maxHeight = '400px';
    alertContent.style.overflowY = 'auto';

    // 移除日期和类型信息显示

    // 显示当前筛选战区（如有）
    if (selectedZones.length > 0) {
        const zoneInfo = document.createElement('div');
        zoneInfo.style.marginBottom = '8px';
        zoneInfo.style.color = '#1f2a37';
        zoneInfo.style.fontSize = '13px';
        zoneInfo.textContent = '当前筛选战区：' + selectedZones.join('，');
        alertContent.appendChild(zoneInfo);
    }

    if (customers.length > 0) {
        // 显示到期客户列表
        const customersList = document.createElement('div');
        customersList.style.fontSize = '13px';
        
        customers.forEach(function(customer) {
            const customerItem = document.createElement('div');
            customerItem.style.padding = '8px 0';
            customerItem.style.borderBottom = '1px solid #f0f0f0';
            
            const dateDiv = document.createElement('div');
            dateDiv.style.fontWeight = 'bold';
            dateDiv.style.color = '#f5222d';
            dateDiv.style.marginBottom = '3px';
            dateDiv.textContent = customer.expiry_date || '';
            
            const companyDiv = document.createElement('div');
            companyDiv.style.color = '#333';
            companyDiv.style.marginBottom = '2px';
            companyDiv.textContent = '公司：' + (customer.company_name || '');

            const accountDiv = document.createElement('div');
            accountDiv.style.color = '#666';
            accountDiv.style.marginBottom = '2px';
            accountDiv.textContent = '账号：' + (customer.jdy_account || '');
            
            const zoneDiv = document.createElement('div');
            zoneDiv.style.color = '#333';
            zoneDiv.style.fontSize = '12px';
            zoneDiv.textContent = '战区：' + (customer.zone || '');

            const amountDiv = document.createElement('div');
            amountDiv.style.color = '#333';
            amountDiv.style.fontSize = '12px';
            amountDiv.textContent = '金额：' + (customer.amount || customer.uid_arr || customer.contract_amount || '');
            
            customerItem.appendChild(dateDiv);
            customerItem.appendChild(companyDiv);
            customerItem.appendChild(accountDiv);
            customerItem.appendChild(zoneDiv);
            customerItem.appendChild(amountDiv);
            
            customersList.appendChild(customerItem);
        });
        
        alertContent.appendChild(customersList);
    } else if (message) {
        // 显示无到期客户的消息
        const messageDiv = document.createElement('div');
        messageDiv.className = 'loading';
        messageDiv.style.textAlign = 'center';
        messageDiv.style.padding = '20px';
        messageDiv.style.color = 'var(--text-color)';
        messageDiv.style.fontSize = '16px';
        messageDiv.textContent = message;
        alertContent.appendChild(messageDiv);
    }

    // 组装提醒看板
    alertContainer.appendChild(alertHeader);
    alertContainer.appendChild(alertContent);
    // 优先挂载到侧栏容器（仅布局，不改 UI）
    const sidebarMount = document.getElementById('sidebarExpiringMount');
    if (sidebarMount) {
        // 清理旧内容后插入
        sidebarMount.innerHTML = '';
        sidebarMount.appendChild(alertContainer);
    } else {
        document.body.appendChild(alertContainer);
    }

    // 添加关闭按钮事件
    closeBtn.addEventListener('click', function() {
        // 如果挂载在侧栏，则清理侧栏内容；否则移除容器
        const mount = alertContainer.parentElement;
        if (mount && mount.id === 'sidebarExpiringMount') {
            mount.innerHTML = '';
        } else {
            alertContainer.remove();
        }
    });
    
    // 添加筛选按钮事件
    filterBtn.addEventListener('click', function() {
        showExpiringZonesFilterModal();
    });
}

// 到期提醒：战区筛选弹窗
function showExpiringZonesFilterModal() {
    // 创建遮罩层
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'modal-overlay';
    modalOverlay.style.position = 'fixed';
    modalOverlay.style.top = '0';
    modalOverlay.style.left = '0';
    modalOverlay.style.width = '100%';
    modalOverlay.style.height = '100%';
    modalOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.4)';
    modalOverlay.style.display = 'flex';
    modalOverlay.style.alignItems = 'center';
    modalOverlay.style.justifyContent = 'center';

    // 创建弹窗容器
    const modalContainer = document.createElement('div');
    modalContainer.className = 'modal-container';
    modalContainer.style.backgroundColor = '#fff';
    modalContainer.style.borderRadius = '8px';
    modalContainer.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)';
    modalContainer.style.maxWidth = '520px';
    modalContainer.style.width = '90%';
    modalContainer.style.padding = '16px';
    modalContainer.style.color = 'var(--text-color)';

    // 标题
    const modalTitle = document.createElement('h3');
    modalTitle.textContent = '选择战区（到期提醒）';
    modalTitle.style.marginTop = '0';
    modalTitle.style.marginBottom = '12px';
    modalTitle.style.fontSize = '16px';
    modalTitle.style.color = '#1f2a37';
    modalContainer.appendChild(modalTitle);

    // 描述
    const modalDesc = document.createElement('p');
    modalDesc.textContent = '可多选战区，系统将显示今天起未来7天内到期的客户。';
    modalDesc.style.margin = '0 0 12px 0';
    modalDesc.style.fontSize = '13px';
    modalDesc.style.color = '#4b5563';
    modalContainer.appendChild(modalDesc);

    // 复选框容器
    const checkboxContainer = document.createElement('div');
    checkboxContainer.style.display = 'grid';
    checkboxContainer.style.gridTemplateColumns = 'repeat(2, 1fr)';
    checkboxContainer.style.gap = '8px';
    checkboxContainer.style.maxHeight = '240px';
    checkboxContainer.style.overflowY = 'auto';
    modalContainer.appendChild(checkboxContainer);

    // 底部按钮
    const modalActions = document.createElement('div');
    modalActions.style.display = 'flex';
    modalActions.style.justifyContent = 'flex-end';
    modalActions.style.gap = '8px';
    modalActions.style.marginTop = '12px';

    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = '取消';
    cancelBtn.className = 'btn';
    cancelBtn.style.backgroundColor = '#e5e7eb';
    cancelBtn.style.color = '#111827';
    cancelBtn.style.border = 'none';
    cancelBtn.style.padding = '8px 12px';
    cancelBtn.style.borderRadius = '6px';
    cancelBtn.style.cursor = 'pointer';

    const confirmBtn = document.createElement('button');
    confirmBtn.textContent = '确定';
    confirmBtn.className = 'btn btn-primary';
    confirmBtn.style.padding = '8px 12px';
    confirmBtn.style.borderRadius = '6px';
    confirmBtn.style.cursor = 'pointer';

    modalActions.appendChild(cancelBtn);
    modalActions.appendChild(confirmBtn);
    modalContainer.appendChild(modalActions);

    modalOverlay.appendChild(modalContainer);
    document.body.appendChild(modalOverlay);

    // 加载战区列表
    safeJsonFetch('/get_zones')
        .then(function(data) {
            const zones = data.zones || [];
            zones.forEach(function(zone) {
                const label = document.createElement('label');
                label.style.display = 'flex';
                label.style.alignItems = 'center';
                label.style.gap = '8px';
                label.style.padding = '6px 8px';
                label.style.border = '1px solid #e5e7eb';
                label.style.borderRadius = '6px';
                label.style.cursor = 'pointer';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = zone;

                const span = document.createElement('span');
                span.textContent = zone;
                span.style.color = '#1f2a37';

                label.appendChild(checkbox);
                label.appendChild(span);
                checkboxContainer.appendChild(label);
            });
        })
        .catch(function(error){
            console.error('获取战区列表失败:', error);
            const errDiv = document.createElement('div');
            errDiv.textContent = '获取战区列表失败';
            errDiv.style.color = '#ef4444';
            checkboxContainer.appendChild(errDiv);
        });

    // 事件绑定
    cancelBtn.addEventListener('click', function(){
        modalOverlay.remove();
    });
    confirmBtn.addEventListener('click', function(){
        const selectedZones = [];
        checkboxContainer.querySelectorAll('input[type="checkbox"]:checked').forEach(function(cb){
            selectedZones.push(cb.value);
        });
        modalOverlay.remove();
        fetchExpiringCustomersWithZones(selectedZones);
    });
}

// 到期提醒：按战区获取数据
function fetchExpiringCustomersWithZones(selectedZones = []) {
    const zonesParam = selectedZones && selectedZones.length > 0 ? encodeURIComponent(selectedZones.join(',')) : '';
    const url = zonesParam ? `/get_expiring_customers?zones=${zonesParam}` : '/get_expiring_customers';
    safeJsonFetch(url)
        .then(function(data) {
            const customers = data.expiring_customers || [];
            const message = data.message || '';
            showExpiringCustomersAlert(customers, data.reminder_type, data.today_date, message, selectedZones);
        })
        .catch(function(error) {
            console.error('获取到期客户失败（战区筛选）:', error);
            showExpiringCustomersAlert([], '', '', '获取数据失败，请稍后重试');
        });
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
    // 文本换行设置，避免横向滚动
    memoTextarea.setAttribute('wrap', 'soft');

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

    // 优先挂载到侧栏容器（仅布局，不改 UI）
    const memoMount = document.getElementById('sidebarMemoMount');
    if (memoMount) {
        memoMount.innerHTML = '';
        memoMount.appendChild(dashboardContainer);
    } else {
        // 添加到页面（回退）
        document.body.appendChild(dashboardContainer);
    }
}





// 页面加载完成后获取即将过期的客户并显示备忘录
document.addEventListener('DOMContentLoaded', function() {
    // 检查用户是否已登录（通过检查页面上的元素判断）
    if (document.getElementById('contractForm')) {
        console.log('页面已加载，开始初始化...');
        
        // Giko 销售页不显示到期客户看板；其他页面保留
        if (!document.body.classList.contains('theme-giko-dark')) {
            createExpiringCustomersReminder();
        }
        
        // 延迟显示备忘录白板
        setTimeout(() => {
            showFutureExpiringCustomersDashboard([], []);
        }, 500);
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
    } else if (modeText.includes('钉钉') && !modeText.includes('内置')) {
        tipElement.innerHTML = `
            <div class="tip-content">
                <strong>⚠️</strong>
                <p class="integration-tip-text">直接在钉钉后台下单</p>
            </div>
        `;
        tipElement.style.display = 'block';
    } else if (modeText.includes('内置')) {
        tipElement.innerHTML = `
            <div class="tip-content">
                <strong>💡</strong>
                <p class="integration-tip-text">简道眼下单</p>
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
        
        // 检查是否有查询结果
        if (!data.results || data.results.length === 0) {
            alert('未找到客户信息');
            return;
        }
        
        // 取第一条结果（通常只有一条）
        const customerData = data.results[0];
        
        // 更新表单字段
        if (customerData.company_name && customerData.company_name !== 'nan') {
            document.querySelector('[name="company_name"]').value = customerData.company_name;
        }
        if (customerData.tax_number && customerData.tax_number !== 'nan') {
            document.querySelector('[name="tax_number"]').value = customerData.tax_number;
        }
        
        // 更新显示内容 - 添加null检查
        const accountEnterpriseNameElement = document.getElementById('accountEnterpriseName');
        if (accountEnterpriseNameElement) {
            accountEnterpriseNameElement.textContent = customerData.account_enterprise_name || '暂无数据';
        }
        
        const versionElement = document.getElementById('version');
        if (versionElement) {
            versionElement.textContent = customerData.version || '暂无数据';
        }
        
        const expiryDateElement = document.getElementById('expiryDate');
        if (expiryDateElement) {
            expiryDateElement.textContent = customerData.expiry_date || '暂无数据';
        }
        
        const uidArrElement = document.getElementById('uidArr');
        if (uidArrElement) {
            uidArrElement.textContent = customerData.uid_arr || '0元';
        }

        const contractAmountElement = document.getElementById('contractAmount');
        if (contractAmountElement) {
            contractAmountElement.textContent = customerData.contract_amount || '0元';
        }
        
        
        
        const amountEl = document.getElementById('amountDisplay');
        if (amountEl) {
            amountEl.textContent = customerData.amount || customerData.uid_arr || customerData.contract_amount || '0元';
        }
        
        // 安全设置可选元素的内容
        const salesCnEnElement = document.getElementById('salesCnEn');
        if (salesCnEnElement) {
            salesCnEnElement.textContent = customerData.sales_cn_en || '暂无数据';
        }
        
        const jdySalesElement = document.getElementById('jdySales');
        if (jdySalesElement) {
            jdySalesElement.textContent = customerData.jdy_sales || '暂无数据';
        }
        
        // 显示结果区域
        document.getElementById('customerInfo').style.display = 'block';
        
        
    })
    .catch(error => {
        console.error('Error:', error);
        alert('客户查询服务暂时不可用，当前为静态预览模式');
    });
}

// 第一个函数已删除，使用文件末尾的完整版本

// 加载节假日到期客户数据
function loadHolidayExpiringCustomers(contentContainer) {
    // 显示加载状态
    contentContainer.innerHTML = `
        <div style="text-align: center; color: #666; padding: 20px;">
            📅 正在加载到期提醒...
        </div>
    `;

    // 调用后端API获取到期客户数据
    fetch('/get_expiring_customers')
        .then(response => {
            if (!response.ok) {
                throw new Error('网络请求失败');
            }
            return response.json();
        })
        .then(data => {
            displayHolidayReminder(contentContainer, data);
        })
        .catch(error => {
            console.error('获取到期客户数据失败:', error);
            contentContainer.innerHTML = `
                <div style="text-align: center; color: #f5222d; padding: 20px;">
                    ❌ 加载失败<br>
                    <small style="color: #666;">点击标题重试</small>
                </div>
            `;
        });
}

// 显示节假日提醒内容
function displayHolidayReminder(container, data) {
    let html = '';

    if (data.error) {
        html = `
            <div style="text-align: center; color: #f5222d; padding: 20px;">
                ❌ ${data.error}<br>
                <small style="color: #666;">点击标题重试</small>
            </div>
        `;
    } else if (data.message) {
        // 没有到期客户的情况
        html = `
            <div style="text-align: center; color: #52c41a; padding: 20px; line-height: 1.6;">
                ${data.message}<br>
                <small style="color: #666; margin-top: 10px; display: block;">
                    ${data.today_date || ''}<br>
                    ${data.reminder_type || ''}
                </small>
            </div>
        `;
    } else if (data.expiring_customers && data.expiring_customers.length > 0) {
        // 有到期客户的情况 - 移除信息区域，直接显示客户列表
        html = '';

        data.expiring_customers.forEach((customer, index) => {
            // 判断销售人员类型并设置颜色
            let salesColor = '#666';
            let salesName = customer.sales_person || '未分配';
            
            // 精确匹配销售人员
            const salesNameLower = salesName.toLowerCase();
            if (salesNameLower.includes('esther')) {
                salesColor = '#ff6b81'; // 粉红色表示Esther负责
            } else if (salesNameLower.includes('mia')) {
                salesColor = '#1890ff'; // 蓝色表示Mia负责
            }
            
            console.log('销售人员:', salesName, '小写:', salesNameLower, '颜色:', salesColor); // 调试信息

            // 判断客户类型
            let customerType = '';
            let customerTypeColor = '#666';
            
            // 根据客户分类或其他字段判断是否为name客户
            if (customer.customer_classification) {
                const classification = customer.customer_classification.toLowerCase();
                if (classification.includes('name') || classification.includes('战区')) {
                    customerType = 'Name';
                    customerTypeColor = '#52c41a';
                } else if (classification.includes('融合')) {
                    customerType = '融合';
                    customerTypeColor = '#fa8c16';
                } else {
                    customerType = '非Name';
                    customerTypeColor = '#8c8c8c';
                }
            } else {
                // 如果没有分类信息，根据其他规则判断
                customerType = '待分类';
                customerTypeColor = '#d9d9d9';
            }

            html += `
                <div style="padding: 8px 12px; border-bottom: 1px solid #f0f0f0; ${index === data.expiring_customers.length - 1 ? 'border-bottom: none;' : ''}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
                        <div style="font-weight: bold; color: #f5222d; font-size: 14px;">
                            ${customer.expiry_date}
                        </div>
                        <div style="background: ${customerTypeColor}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: 500;">
                            ${customerType}
                        </div>
                    </div>
                    <div style="color: #666; font-size: 12px; margin-bottom: 2px; word-break: break-all;">
                        ${customer.jdy_account}
                    </div>
                    <div style="color: #333; font-size: 12px; margin-bottom: 2px; word-break: break-all; line-height: 1.3;">
                        ${customer.company_name}
                    </div>
                    <div style="font-size: 12px; font-weight: 500;">
                        销售: <span style="color: ${salesColor}; font-weight: bold;">${salesName}</span>
                    </div>
                </div>
            `;
        });
    } else {
        // 数据为空的情况
        html = `
            <div style="text-align: center; color: #666; padding: 20px;">
                📅 暂无到期提醒<br>
                <small style="color: #999;">点击标题刷新</small>
            </div>
        `;
    }

    container.innerHTML = html;
}

// 计算器代码已移除，替换为到期客户提醒功能

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
                console.error('计算错误:', error);
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
    const assistAnswer = document.getElementById('assistAnswer');
    
    // 悬浮球点击事件
    if (assistBall) {
        assistBall.addEventListener('click', function() {
            toggleAssistPanel();
        });
    }
    
    // 关闭按钮点击事件
    if (assistClose) {
        assistClose.addEventListener('click', function() {
            closeAssistPanel();
        });
    }
    
    // 键盘快捷键 Ctrl/⌘ + Shift + K
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'K') {
            if (!assistPanel || !assistBall) return; // 元素不存在时忽略
            e.preventDefault();
            toggleAssistPanel();
        }
    });
    
    // 点击面板外部关闭
    document.addEventListener('click', function(e) {
        if (!assistPanel || !assistBall) return; // 元素不存在时忽略
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
    
    const getLocalStageOps = () => { try { return JSON.parse(localStorage.getItem('stage-ops') || '{}'); } catch (e) { return {}; } };
    const setLocalStageOps = (ops) => { localStorage.setItem('stage-ops', JSON.stringify(ops)); };
    const recordLocalStageOp = (jdyId, stage) => {
        if (!jdyId) return;
        const ops = getLocalStageOps();
        ops[jdyId] = { stage, ts: Date.now(), status: 'pending' };
        setLocalStageOps(ops);
    };
    const markStageOpSynced = (jdyId) => {
        const ops = getLocalStageOps();
        if (ops[jdyId]) { ops[jdyId].status = 'synced'; setLocalStageOps(ops); }
    };
    const getUnsyncedCount = () => {
        const ops = getLocalStageOps();
        return Object.values(ops).filter(v => v && v.status === 'pending').length;
    };
    const renderUnsyncedBanner = () => {
        const container = document.getElementById('status-filter-container');
        if (!container) return;
        let banner = document.getElementById('unsyncedBanner');
        const count = getUnsyncedCount();
        if (count > 0) {
            const html = `<div id="unsyncedBanner" style="margin:6px 0;padding:6px;border:1px solid #faad14;background:#fffbe6;color:#ad6800;border-radius:4px;font-size:12px;">检测到 ${count} 条本地未同步状态，已优先显示本地修改</div>`;
            if (banner) { banner.outerHTML = html; } else { container.insertAdjacentHTML('beforebegin', html); }
        } else if (banner) {
            banner.remove();
        }
    };
    const bindStageBtn = (id, stage) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('click', function() {
            const jdyId = (assistId && assistId.value ? assistId.value.trim() : '');
            if (jdyId) recordLocalStageOp(jdyId, stage);
            updateStage(stage, jdyId);
            renderUnsyncedBanner();
        });
    };
    bindStageBtn('btnStageContract', '合同');
    bindStageBtn('btnStageInvoice', '开票');
    bindStageBtn('btnStageAdvanceInvoice', '提前开');
    bindStageBtn('btnStageInvalid', '无效');
    bindStageBtn('btnStageUpsell', '增购');
    bindStageBtn('btnStageLost', '失联');
    bindStageBtn('btnStagePaid', '回款');
    
    // 未签订合同客户功能（首页专用；销售页可能没有该按钮）
    const refreshUnsignedBtn = document.getElementById('btnRefreshUnsigned');
    if (refreshUnsignedBtn) {
        refreshUnsignedBtn.addEventListener('click', function() {
            const zones = (window._selectedZones && window._selectedZones.length > 0) ? window._selectedZones : [];
            fetchFutureCustomersWithZones(zones);
        });
    }
    
    // 未来30天客户筛选功能
    const btnFilterUnsigned = document.getElementById('btnFilterUnsigned');
    if (btnFilterUnsigned) {
        btnFilterUnsigned.addEventListener('click', function() {
            showZonesFilterModal();
        });
    }
    
    // 绑定自动监控按钮事件
    // 停止监控按钮已移除
    
    const btnCheckNow = document.getElementById('btnCheckNow');
    if (btnCheckNow) {
        btnCheckNow.addEventListener('click', function() {
            // 立即检查监控状态
            updateMonitorStatus();
        });
    }
    

    const savedFilter = localStorage.getItem('status-filter') || 'na';
    fetchUnsignedCustomers(savedFilter);
    const unsyncedList = document.getElementById('unsyncedOpsList');
    function renderUnsyncedOpsList() {
        if (!unsyncedList) return;
        const container = unsyncedList.closest('.assist-unsigned');
        const ops = getLocalStageOps();
        const entries = Object.entries(ops).filter(([k, v]) => v && v.status === 'pending');
        if (entries.length === 0) {
            if (container) container.style.display = 'none';
            unsyncedList.innerHTML = '';
            return;
        }
        if (container) container.style.display = '';
        let html = '';
        entries.forEach(([id, v]) => {
            const time = new Date(v.ts).toLocaleString('zh-CN');
            html += `
                <div style="border:1px solid #e0e0e0;border-radius:6px;padding:8px;margin-bottom:6px;background:#fff;display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-size:12px;color:#333;line-height:1.4;">
                        <div><strong>账号:</strong> ${id}</div>
                        <div><strong>阶段:</strong> ${v.stage}</div>
                        <div><strong>时间:</strong> ${time}</div>
                    </div>
                    <div>
                        <button class="btn btn-secondary" data-sync-id="${id}" style="font-size:12px;padding:4px 8px;">同步</button>
                    </div>
                </div>
            `;
        });
        unsyncedList.innerHTML = html;
        unsyncedList.querySelectorAll('button[data-sync-id]').forEach(btn => {
            btn.addEventListener('click', function() {
                const jdyId = this.getAttribute('data-sync-id');
                const op = getLocalStageOps()[jdyId];
                if (op) updateStage(op.stage, jdyId);
            });
        });
    }
    renderUnsyncedOpsList();
    const btnSyncLocalOps = document.getElementById('btnSyncLocalOps');
    if (btnSyncLocalOps) {
        btnSyncLocalOps.addEventListener('click', function() {
            const ops = getLocalStageOps();
            const entries = Object.entries(ops).filter(([k, v]) => v && v.status === 'pending');
            entries.forEach(([id, v]) => {
                updateStage(v.stage, id);
            });
        });
    }
    const btnExportAll = document.getElementById('btnExportAllCustomers');
    if (btnExportAll) {
        btnExportAll.addEventListener('click', function() {
            const exportUrl = '/export_unsigned_customers';
            window.open(exportUrl, '_blank');
        });
    }
    
    // 页面初次加载主动获取未来30天客户（仅在已选择战区时触发）
    // 避免与状态筛选看板的渲染冲突
    const initialZones = (window._selectedZones && window._selectedZones.length > 0) ? window._selectedZones : [];
    // 初始化时无论是否选择战区，都拉取未来看板数据（空数组表示全部战区）
    fetchFutureCustomersWithZones(initialZones);
    
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

                // 状态修改成功后，刷新未来30天客户看板（保持当前筛选）
                try {
                    const activeBtn = document.querySelector('#status-filter-container .filter-btn.active');
                    const currentFilter = activeBtn ? activeBtn.getAttribute('data-filter') : 'na';
                    fetchUnsignedCustomers(currentFilter);
                } catch (e) {
                    // 回退为默认NA筛选
                    fetchUnsignedCustomers('na');
                }

                // 同步刷新战区视图（空数组表示全部战区）
                const zones = Array.isArray(window._selectedZones) ? window._selectedZones : [];
                fetchFutureCustomersWithZones(zones);
                markStageOpSynced(jdyId);
                renderUnsyncedBanner();
                renderUnsyncedOpsList();
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
    
    // 获取未签订合同客户（静态预览友好）
    async function fetchUnsignedCustomers(statusFilter = 'all') {
        const unsignedList = document.getElementById('unsignedCustomersList');
        if (!unsignedList) return;
        
        unsignedList.innerHTML = '<div class="loading" style="text-align: center; color: #666; padding: 10px;">加载中...</div>';
        
        const url = `/get_unsigned_customers?status=${statusFilter}`;
        const fallback = {
            available_statuses: [
                { value: 'all', count: 0 },
                { value: 'na', count: 0 },
                { value: 'contract', count: 0 },
                { value: 'invoice', count: 0 },
                { value: 'advance_invoice', count: 0 },
                { value: 'paid', count: 0 },
                { value: 'invalid', count: 0 },
                { value: 'upsell', count: 0 },
                { value: 'lost', count: 0 }
            ],
            current_filter: statusFilter,
            customers: []
        };
        
        const data = await safeJsonFetch(url, { credentials: 'same-origin' }, fallback);
        
        if (!data) return;
        
        if (data._static_preview && !data.customers?.length) {
            const filterLabel = getFilterLabel(statusFilter);
            unsignedList.innerHTML = `<div style="text-align: center; color: var(--text-color); padding: 10px;">🌐 静态预览模式：后端未启动，暂无法获取"${filterLabel}"客户</div>`;
            updateStatusFilter(data.available_statuses, data.current_filter);
            return;
        }
        
        if (data.error) {
            unsignedList.innerHTML = `<div style="text-align: center; color: #e74c3c; padding: 10px;">${data.error}</div>`;
            return;
        }
        
        // 更新状态筛选器
        updateStatusFilter(data.available_statuses, data.current_filter);
        
        if (!data.customers || data.customers.length === 0) {
            const filterLabel = getFilterLabel(statusFilter);
            unsignedList.innerHTML = `<div style="text-align: center; color: #666; padding: 10px;">😊 未来8-33天内没有符合"${filterLabel}"条件的客户</div>`;
            return;
        }
        
        // 显示客户列表 - 不显示数量统计信息
        let html = '';
        
        const localOps = getLocalStageOps();
        data.customers.forEach(customer => {
            let stageText = (customer.customer_stage && customer.customer_stage.trim()) ? customer.customer_stage : 'NA';
            const op = localOps[customer.jdy_account];
            const overridden = op && op.status === 'pending' && op.stage;
            if (overridden) stageText = op.stage;
            const stageClass = getStageClass(stageText);
            html += `
                <div style="border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px; margin-bottom: 6px; background: #f9f9f9;">
                    <div style="font-size: 12px; color: #e74c3c; font-weight: bold; margin-bottom: 4px;">${customer.expiry_date}</div>
                    <div style="font-size: 11px; color: #333; line-height: 1.3;">
                        <div style="margin-bottom: 2px;"><strong>公司:</strong> ${customer.company_name}</div>
                        <div style="margin-bottom: 2px;"><strong>账号:</strong> ${customer.jdy_account}</div>
                        <div style="margin-bottom: 2px;"><strong>销售:</strong> ${customer.sales_person}</div>
                        <div style="margin-bottom: 2px;"><strong>状态:</strong> <span class="${stageClass}">${stageText}</span>${overridden ? '<span style="margin-left:6px;color:#fa8c16;font-size:11px;">(本地未同步)</span>' : ''}</div>
                        ${customer.integration_mode ? `<div style="margin-bottom: 2px;"><strong>集成模式:</strong> ${getIntegrationModeTip(customer.integration_mode)}</div>` : ''}
                    </div>
                </div>
            `;
        });
        
        unsignedList.innerHTML = html;
        renderUnsyncedOpsList();
        
        // 导出按钮事件由筛选器区域的固定按钮负责
    }

    // 获取集成模式提醒
    function getIntegrationModeTip(mode) {
        if (!mode) return '';
        
        if (mode.includes('企微')) {
            return `<span style="color: #1890ff;">${mode} <strong>⚠️ 需在SA后台和企微平台下单</strong></span>`;
        } else if (mode.includes('钉钉') && !mode.includes('内置')) {
            return `<span style="color: #52c41a;">${mode} <strong>✅ 仅需在钉钉后台下单</strong></span>`;
        } else if (mode.includes('内置')) {
            return `<span style="color: #fa8c16;">${mode} <strong>💡 简道眼下单</strong></span>`;
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
            // 使用getFilterLabel函数获取处理后的标签文本
            const filteredLabel = getFilterLabel(status.value);
            html += `<button class="filter-btn ${activeClass}" data-filter="${status.value}"
                style="${buttonStyle} padding: 4px 8px; margin: 2px; border-radius: 4px; cursor: pointer; font-size: 11px;">
                ${filteredLabel} (${status.count})
            </button>`;
        });
        html += '</div>';
        
        filterContainer.innerHTML = html;
        // 将导出按钮移动到看板标题右侧，减少占用空间
        const boardRoot = filterContainer.closest('.assist-unsigned');
        const headerControls = boardRoot ? boardRoot.querySelector('.unsigned-header .monitor-controls') : null;
        if (headerControls && !document.getElementById('btnExportBackendAllHeader')) {
            const btn = document.createElement('button');
            btn.id = 'btnExportBackendAllHeader';
            btn.className = 'btn btn-secondary';
            btn.textContent = '📁 导出所有';
            btn.style.marginLeft = '6px';
            btn.style.minWidth = 'auto';
            headerControls.appendChild(btn);
            btn.addEventListener('click', function() {
                const exportUrl = '/export_unsigned_customers';
                window.open(exportUrl, '_blank');
            });
        }
        
        // 添加事件监听器
        const filterButtons = filterContainer.querySelectorAll('.filter-btn');
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const filterValue = this.getAttribute('data-filter');
                localStorage.setItem('status-filter', filterValue);
                fetchUnsignedCustomers(filterValue);
                renderUnsyncedBanner();
                renderUnsyncedOpsList();
            });
        });
        renderUnsyncedBanner();
        renderUnsyncedOpsList();
    }
    
    function getFilterLabel(filter) {
    const labels = {
        'all': '全部',
        'na': 'NA',
        'contract': '合同',
        'invoice': '开票',
        'advance_invoice': '提前开',
        'paid': '回款',
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
                const monitorStatusElement = document.getElementById('monitorStatusText');
                if (monitorStatusElement) {
                    monitorStatusElement.textContent = '后台监控中';
                }
                
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
                const monitorStatusElement = document.getElementById('monitorStatusText');
                if (monitorStatusElement) {
                    monitorStatusElement.textContent = '已停止';
                }
                
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
    
    // 检查监控状态（静态预览友好）
    async function checkMonitorStatus() {
        const data = await safeJsonFetch('/get_monitor_status', { method: 'GET', credentials: 'same-origin' }, {
            success: true,
            enabled: false,
            last_check: new Date().toISOString(),
            results: { recent_contracts: [], updated_contracts: [], total_updated: 0 }
        });
        if (data && data.success) {
            updateMonitorDisplay(data);
        }
    }
    
    // 初始化监控状态（静态预览友好）
    async function initializeMonitorStatus() {
        const data = await safeJsonFetch('/get_monitor_status', { method: 'GET', credentials: 'same-origin' }, {
            success: true,
            enabled: false,
            last_check: new Date().toISOString(),
            results: { recent_contracts: [], updated_contracts: [], total_updated: 0 }
        });

        if (data && data.success) {
            // 更新监控状态显示
            isMonitoring = !!data.enabled;

            const monitorStatusText = document.getElementById('monitorStatusText');

            if (monitorStatusText) {
                if (isMonitoring) {
                    monitorStatusText.textContent = '自动监控中';
                    monitorStatusText.style.color = '#48bb78';

                    // 开始定期检查监控状态
                    startStatusCheck();

                    console.log('检测到监控已自动启动');
                } else {
                    monitorStatusText.textContent = isStaticPreview() ? '预览模式（未连接后台）' : '已停止';
                    monitorStatusText.style.color = '#666';
                }
            }

            // 更新监控显示
            updateMonitorDisplay(data);
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
// 创建到期客户提醒看板（替代智能计算器）
function createExpiringCustomersReminder() {
    console.log('开始创建到期客户提醒看板');
    
    // 移除现有看板
    const existing = document.getElementById('smart-calculator');
    if (existing) existing.remove();

    // 创建新看板（统一使用样式类）
    const container = document.createElement('div');
    container.id = 'smart-calculator';
    container.className = 'smart-calculator';

    // 标题栏使用统一样式类
    const header = document.createElement('div');
    header.className = 'calculator-header';
    header.textContent = '📅 到期客户提醒';

    // 内容区域使用统一样式类
    const content = document.createElement('div');
    content.className = 'calculator-display';
    content.innerHTML = '<div class="loading">加载中...</div>';

    container.appendChild(header);
    container.appendChild(content);
    document.body.appendChild(container);
    
    console.log('看板已创建，开始获取数据');
    fetchExpiringCustomers();
}

// 日历时间显示功能
function initCalendarDisplay() {
    function updateDateTime() {
        const now = new Date();
        
        // 更新日期
        const year = now.getFullYear();
        const month = now.getMonth() + 1;
        const day = now.getDate();
        const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
        const weekday = weekdays[now.getDay()];

        // 计算本月第几周（以周一为一周开始）
        const firstOfMonth = new Date(year, month - 1, 1);
        const firstDayMondayIndex = (firstOfMonth.getDay() + 6) % 7; // 周一=0
        const weekOfMonth = Math.floor((day + firstDayMondayIndex - 1) / 7) + 1;
        
        const dateElement = document.getElementById('calendarDate');
        if (dateElement) {
            dateElement.textContent = `${year}年${month.toString().padStart(2, '0')}月${day.toString().padStart(2, '0')}日（第${weekOfMonth}周） ${weekday}`;
        }
        
        // 更新时间
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        
        const timeElement = document.getElementById('calendarTime');
        if (timeElement) {
            timeElement.textContent = `${hours}:${minutes}`;
        }
    }
    
    // 立即更新一次
    updateDateTime();
    
    // 每秒更新时间
    setInterval(updateDateTime, 1000);
    
    // 获取本月收款金额
    fetchMonthlyRevenue();
}

// 获取本月收款总金额
function fetchMonthlyRevenue() {
    fetch('/get_monthly_revenue', {
        credentials: 'same-origin'
    })
        .then(response => {
            if (response.status === 302 || response.url.includes('/login')) {
                console.log('需要登录才能获取收款数据');
                const revenueElement = document.getElementById('monthlyRevenue');
                if (revenueElement) {
                    revenueElement.textContent = '需要登录';
                }
                return null;
            }
            if (response.status === 404) {
                console.log('收款数据API不可用');
                const revenueElement = document.getElementById('monthlyRevenue');
                if (revenueElement) {
                    revenueElement.textContent = '暂无数据';
                }
                return null;
            }
            const contentType = response.headers.get('content-type');
            if (!response.ok || !contentType || !contentType.includes('application/json')) {
                throw new Error('获取收款数据失败');
            }
            return response.json();
        })
        .then(data => {
            if (!data) return;
            
            const revenueElement = document.getElementById('monthlyRevenue');
            if (revenueElement) {
                if (data.error) {
                    console.error('获取收款数据失败:', data.error);
                    revenueElement.textContent = '数据错误';
                } else if (data.revenue !== undefined) {
                    // 格式化金额显示
                    const formattedRevenue = new Intl.NumberFormat('zh-CN').format(data.revenue);
                    revenueElement.textContent = formattedRevenue;
                } else {
                    revenueElement.textContent = '--';
                }
            }
        })
        .catch(error => {
            console.error('获取收款数据失败:', error);
            const revenueElement = document.getElementById('monthlyRevenue');
            if (revenueElement) {
                revenueElement.textContent = '--';
            }
        });
}

// 在页面加载时初始化日历显示
document.addEventListener('DOMContentLoaded', function() {
    // 延迟初始化，确保元素已加载
    setTimeout(initCalendarDisplay, 500);
});

// -------- 报价单必填校验与错误显示工具函数 --------
function setFieldError(fieldName, message) {
    const input = document.getElementById(fieldName) || document.querySelector(`[name="${fieldName}"]`);
    if (input) {
        input.classList.add('input-error');
    }
    const errEl = document.getElementById(`error_${fieldName}`) || document.getElementById(`${fieldName}-error`);
    if (errEl) {
        errEl.textContent = message || '该字段为必填项';
        errEl.style.display = 'block';
    }
}

function clearFieldError(fieldName) {
    const input = document.getElementById(fieldName) || document.querySelector(`[name="${fieldName}"]`);
    if (input) {
        input.classList.remove('input-error');
    }
    const errEl = document.getElementById(`error_${fieldName}`) || document.getElementById(`${fieldName}-error`);
    if (errEl) {
        errEl.textContent = '';
        errEl.style.display = 'none';
    }
}

function clearAllFieldErrors(fields) {
    (fields || []).forEach(f => clearFieldError(f));
}

// 初始化监听：输入变更时清除错误
document.addEventListener('DOMContentLoaded', function() {
    const fields = ['company_name', 'tax_number', 'jdy_account', 'total_amount', 'user_count'];
    fields.forEach(name => {
        const el = document.getElementById(name) || document.querySelector(`[name="${name}"]`);
        if (el) {
            ['input', 'change', 'blur'].forEach(evt => {
                el.addEventListener(evt, () => clearFieldError(name));
            });
        }
    });
});

// 生成报价单功能
function generateQuote() {
    // 获取表单数据
    const formData = new FormData(document.getElementById('contractForm'));
    
    // 验证必填字段
    const requiredFields = ['company_name', 'tax_number', 'jdy_account', 'total_amount', 'user_count'];
    clearAllFieldErrors(requiredFields);
    const labels = {
        'company_name': '公司名称',
        'tax_number': '税号',
        'jdy_account': '简道云账号',
        'total_amount': '服务费用金额',
        'user_count': '使用人数'
    };
    const missing = [];
    requiredFields.forEach(field => {
        const val = (formData.get(field) || '').toString().trim();
        if (!val) {
            missing.push(field);
            setFieldError(field, `请填写${labels[field]}`);
        }
    });
    if (missing.length) {
        const first = missing[0];
        const el = document.getElementById(first) || document.querySelector(`[name="${first}"]`);
        if (el && typeof el.scrollIntoView === 'function') {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            el.focus();
        }
        return; // 阻止提交
    }
    
    // 显示加载状态
    const button = event && event.target ? event.target : document.querySelector('.btn-quote');
    const originalText = button.textContent;
    button.textContent = '生成中...';
    button.disabled = true;
    
    // 发送请求到后端
    fetch('/generate_quote', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            // 结构化错误返回
            return response.json().then(data => {
                if (data && data.errors) {
                    Object.keys(data.errors).forEach(field => {
                        setFieldError(field, data.errors[field]);
                    });
                }
                const msg = (data && (data.error || data.message)) || '生成报价单失败';
                throw new Error(msg);
            });
        }
        if (!response.ok) {
            throw new Error('生成报价单失败');
        }
        return response.blob();
    })
    .then(blob => {
        // 下载生成的报价单
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `${formData.get('company_name')}_报价单.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        alert('报价单生成成功！');
    })
    .catch(error => {
        console.error('生成报价单错误:', error);
        // 保留一次提示，但以结构化错误为主
        if (!String(error.message || '').includes('请填写')) {
            alert(error.message || '生成报价单失败，请检查填写的信息');
        }
    })
    .finally(() => {
        // 恢复按钮状态
        button.textContent = originalText;
        button.disabled = false;
    });
}

// 获取字段标签
function getFieldLabel(fieldName) {
    const labels = {
        'company_name': '公司名称',
        'tax_number': '税号',
        'jdy_account': '简道云账号',
        'total_amount': '服务费用金额',
        'user_count': '使用人数'
    };
    return labels[fieldName] || fieldName;
}

// 创建智能计算器
function createSmartCalculator() {
    // 检查是否已存在计算器
    const existingCalculator = document.getElementById('smart-calculator');
    if (existingCalculator) {
        return; // 如果已存在，直接返回
    }

    // 创建计算器容器
    const calculator = document.createElement('div');
    calculator.id = 'smart-calculator';
    calculator.className = 'smart-calculator';
    calculator.style.position = 'fixed';
    calculator.style.top = '20px';
    calculator.style.right = '20px';
    calculator.style.zIndex = '1000';
    calculator.style.display = 'none'; // 默认隐藏

    // 创建计算器标题栏
    const header = document.createElement('div');
    header.className = 'calculator-header';
    
    const title = document.createElement('span');
    title.textContent = '🧮 智能计算器';
    
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '×';
    closeBtn.style.background = 'none';
    closeBtn.style.border = 'none';
    closeBtn.style.color = '#fff';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.fontSize = '18px';
    closeBtn.style.marginLeft = 'auto';
    closeBtn.onclick = () => calculator.style.display = 'none';
    
    header.appendChild(title);
    header.appendChild(closeBtn);
    header.style.display = 'flex';
    header.style.justifyContent = 'space-between';
    header.style.alignItems = 'center';

    // 创建显示屏
    const display = document.createElement('input');
    display.className = 'calculator-input';
    display.type = 'text';
    display.value = '0';
    display.readOnly = true;

    // 创建按钮区域
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'calculator-buttons';

    // 定义按钮布局
    const buttonLayout = [
        ['AC', 'C', '÷'],
        ['7', '8', '9', '×'],
        ['4', '5', '6', '-'],
        ['1', '2', '3', '+'],
        ['0', '.', '=']
    ];

    // 计算器状态变量
    let firstOperand = '';
    let operator = '';
    let waitingForSecondOperand = false;

    // 创建按钮
    buttonLayout.forEach(row => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'calculator-row';
        
        row.forEach(buttonText => {
            const button = document.createElement('button');
            button.className = 'calculator-button';
            button.textContent = buttonText;
            button.type = 'button';
            
            // 特殊按钮样式
            if (buttonText === '0') {
                button.style.gridColumn = 'span 2';
            }
            if (['+', '-', '×', '÷', '='].includes(buttonText)) {
                button.style.backgroundColor = '#ff9500';
            }
            if (['AC', 'C'].includes(buttonText)) {
                button.style.backgroundColor = '#a6a6a6';
            }
            
            button.onclick = () => handleButtonClick(buttonText);
            rowDiv.appendChild(button);
        });
        
        buttonsContainer.appendChild(rowDiv);
    });

    // 按钮点击处理函数
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
            // 清空输入
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
                    if (num2 === 0) {
                        display.value = '错误：除数不能为零';
                        return;
                    }
                    result = num1 / num2;
                }
                
                // 格式化结果
                let formattedResult;
                if (Number.isInteger(result) || (Math.abs(result) >= 1e15 || Math.abs(result) < 1e-10)) {
                    formattedResult = result.toString();
                } else {
                    formattedResult = result.toFixed(12).replace(/\.?0+$/, '');
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
                console.error('计算错误:', error);
                display.value = '计算错误';
            }
        }
    }

    // 组装计算器
    calculator.appendChild(header);
    calculator.appendChild(display);
    calculator.appendChild(buttonsContainer);

    // 添加到页面
    document.body.appendChild(calculator);

    // 添加快捷键支持（可选）
    document.addEventListener('keydown', function(event) {
        if (calculator.style.display === 'none') return;
        
        const key = event.key;
        if (/\d/.test(key) || ['+', '-', '*', '/', '=', 'Enter', '.', 'Escape', 'c', 'C'].includes(key)) {
            event.preventDefault();
            
            if (key === 'Enter' || key === '=') {
                handleButtonClick('=');
            } else if (key === 'Escape') {
                calculator.style.display = 'none';
            } else if (key === 'c' || key === 'C') {
                handleButtonClick('C');
            } else if (key === '*') {
                handleButtonClick('×');
            } else if (key === '/') {
                handleButtonClick('÷');
            } else {
                handleButtonClick(key);
            }
        }
    });

    console.log('智能计算器已创建');
}
