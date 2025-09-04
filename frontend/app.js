/**
 * Task Manager Frontend Application
 * Pure JavaScript SPA for task management
 */

// === 設定 ===
const CONFIG = {
    API_BASE_URL: 'http://localhost:5001/api',
    TOKEN_KEY: 'task_manager_token',
    REFRESH_TOKEN_KEY: 'task_manager_refresh_token',
    USER_KEY: 'task_manager_user'
};

// === 状態管理 ===
const AppState = {
    currentUser: null,
    currentView: 'dashboard',
    tasks: [],
    categories: [],
    stats: {},
    editingTask: null,
    editingCategory: null,
    
    setCurrentUser(user) {
        this.currentUser = user;
        localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
    },
    
    clearCurrentUser() {
        this.currentUser = null;
        localStorage.removeItem(CONFIG.USER_KEY);
        localStorage.removeItem(CONFIG.TOKEN_KEY);
        localStorage.removeItem(CONFIG.REFRESH_TOKEN_KEY);
    }
};

// === ユーティリティ関数 ===
const Utils = {
    formatDate(dateString) {
        if (!dateString) return 'なし';
        const date = new Date(dateString);
        return date.toLocaleDateString('ja-JP', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    formatDateForInput(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    },
    
    getPriorityText(priority) {
        const map = {
            low: '低',
            medium: '中',
            high: '高',
            urgent: '緊急'
        };
        return map[priority] || priority;
    },
    
    getStatusText(status) {
        const map = {
            pending: '未完了',
            in_progress: '進行中',
            completed: '完了済み',
            cancelled: 'キャンセル'
        };
        return map[status] || status;
    },
    
    showLoading() {
        document.getElementById('loading').classList.add('active');
    },
    
    hideLoading() {
        document.getElementById('loading').classList.remove('active');
    },
    
    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-triangle' : 
                    'info-circle';
        
        // メッセージに改行が含まれている場合は分割して表示
        const messageLines = message.split('\n').filter(line => line.trim());
        const mainMessage = messageLines[0];
        const detailMessage = messageLines.slice(1).join('\n');
        
        toast.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <div class="toast-content">
                <div class="toast-main">${mainMessage}</div>
                ${detailMessage ? `<div class="toast-details">${detailMessage}</div>` : ''}
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(toast);
        
        // エラーメッセージは8秒、その他は5秒で削除
        const timeout = type === 'error' ? 8000 : 5000;
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, timeout);
    }
};

// === API通信 ===
class APIClient {
    static async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                // ログインAPIの場合は、セッション期限切れの処理をスキップ
                const isLoginAPI = endpoint.includes('/auth/login');
                
                // トークンエラーの場合、ログアウト（ログインAPI以外）
                if ((response.status === 401 || response.status === 422) && !isLoginAPI) {
                    AppState.clearCurrentUser();
                    Auth.showAuthScreen();
                    Utils.showToast('セッションが期限切れです。再度ログインしてください。', 'error');
                    return null;
                }
                
                // 詳細なエラーメッセージがある場合は、それも含めてエラーを投げる
                const errorMessage = data.error || `HTTP ${response.status}`;
                const errorDetails = data.details ? `\n${data.details}` : '';
                throw new Error(errorMessage + errorDetails);
            }
            
            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }
    
    static async get(endpoint) {
        return this.request(endpoint);
    }
    
    static async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    static async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    static async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
}

// === 認証管理 ===
const Auth = {
    async login(username, password) {
        try {
            Utils.showLoading();
            const data = await APIClient.post('/auth/login', { username, password });
            
            if (data) {
                localStorage.setItem(CONFIG.TOKEN_KEY, data.access_token);
                localStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, data.refresh_token);
                AppState.setCurrentUser(data.user);
                
                this.showMainScreen();
                Utils.showToast(data.message);
                await Dashboard.init();
            }
        } catch (error) {
            Utils.showToast(error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    async register(username, email, password) {
        try {
            Utils.showLoading();
            const data = await APIClient.post('/auth/register', { username, email, password });
            
            if (data) {
                Utils.showToast(data.message);
                showLogin(); // 登録後はログイン画面に切り替え
            }
        } catch (error) {
            Utils.showToast(error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    logout() {
        AppState.clearCurrentUser();
        this.showAuthScreen();
        Utils.showToast('ログアウトしました');
    },
    
    showAuthScreen() {
        document.getElementById('auth-screen').classList.add('active');
        document.getElementById('main-screen').classList.remove('active');
    },
    
    showMainScreen() {
        document.getElementById('auth-screen').classList.remove('active');
        document.getElementById('main-screen').classList.add('active');
        
        // ユーザー名表示
        if (AppState.currentUser) {
            document.getElementById('user-name').textContent = AppState.currentUser.username;
        }
    },
    
    checkAuthentication() {
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        const userStr = localStorage.getItem(CONFIG.USER_KEY);
        
        if (token && userStr) {
            try {
                AppState.currentUser = JSON.parse(userStr);
                this.showMainScreen();
                Dashboard.init();
                return true;
            } catch (error) {
                this.logout();
                return false;
            }
        }
        
        this.showAuthScreen();
        return false;
    }
};

// === ダッシュボード ===
const Dashboard = {
    async init() {
        await this.loadStats();
        await this.loadRecentTasks();
    },
    
    async loadStats() {
        try {
            const data = await APIClient.get('/tasks/stats');
            if (data) {
                AppState.stats = data.stats;
                this.renderStats();
            }
        } catch (error) {
            console.error('統計データの読み込みエラー:', error);
        }
    },
    
    async loadRecentTasks() {
        try {
            const data = await APIClient.get('/tasks/?limit=5');
            if (data) {
                this.renderRecentTasks(data.tasks.slice(0, 5));
            }
        } catch (error) {
            console.error('最近のタスクの読み込みエラー:', error);
        }
    },
    
    renderStats() {
        const stats = AppState.stats;
        document.getElementById('total-tasks').textContent = stats.total_tasks || 0;
        document.getElementById('pending-tasks').textContent = stats.pending_tasks || 0;
        document.getElementById('completed-tasks').textContent = stats.completed_tasks || 0;
        document.getElementById('completion-rate').textContent = `${stats.completion_rate || 0}%`;
    },
    
    renderRecentTasks(tasks) {
        const container = document.getElementById('recent-tasks-list');
        
        if (tasks.length === 0) {
            container.innerHTML = '<p class="text-muted">まだタスクがありません。</p>';
            return;
        }
        
        container.innerHTML = tasks.map(task => `
            <div class="task-card">
                <div class="task-header">
                    <div class="task-title">${task.title}</div>
                    <div class="task-actions">
                        <button class="btn btn-outline" onclick="Tasks.editTask(${task.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </div>
                ${task.description ? `<div class="task-description">${task.description}</div>` : ''}
                <div class="task-meta">
                    <span class="task-badge priority-${task.priority}">
                        ${Utils.getPriorityText(task.priority)}
                    </span>
                    <span class="task-badge status-${task.status}">
                        ${Utils.getStatusText(task.status)}
                    </span>
                    ${task.category_name ? `<span class="task-badge">${task.category_name}</span>` : ''}
                </div>
                ${task.due_date ? `<div class="text-small text-muted">期限: ${Utils.formatDate(task.due_date)}</div>` : ''}
            </div>
        `).join('');
    }
};

// === タスク管理 ===
const Tasks = {
    async loadTasks(filters = {}) {
        try {
            Utils.showLoading();
            let queryParams = new URLSearchParams();
            
            if (filters.status) queryParams.append('status', filters.status);
            if (filters.priority) queryParams.append('priority', filters.priority);
            if (filters.category_id) queryParams.append('category_id', filters.category_id);
            
            const queryString = queryParams.toString();
            const url = queryString ? `/tasks/?${queryString}` : '/tasks/';
            
            const data = await APIClient.get(url);
            if (data) {
                AppState.tasks = data.tasks;
                this.renderTasks();
            }
        } catch (error) {
            Utils.showToast('タスクの読み込みに失敗しました', 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    renderTasks() {
        const container = document.getElementById('tasks-list');
        
        if (AppState.tasks.length === 0) {
            container.innerHTML = '<p class="text-muted">条件に合うタスクがありません。</p>';
            return;
        }
        
        container.innerHTML = AppState.tasks.map(task => `
            <div class="task-card">
                <div class="task-header">
                    <div class="task-title">${task.title}</div>
                    <div class="task-actions">
                        <button class="btn btn-outline" onclick="Tasks.editTask(${task.id})" title="編集">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-danger" onclick="Tasks.deleteTask(${task.id})" title="削除">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                ${task.description ? `<div class="task-description">${task.description}</div>` : ''}
                <div class="task-meta">
                    <span class="task-badge priority-${task.priority}">
                        ${Utils.getPriorityText(task.priority)}
                    </span>
                    <span class="task-badge status-${task.status}">
                        ${Utils.getStatusText(task.status)}
                    </span>
                    ${task.category_name ? `<span class="task-badge" style="background-color: ${task.category_color || '#007bff'}20; color: ${task.category_color || '#007bff'}">${task.category_name}</span>` : ''}
                </div>
                ${task.due_date ? `<div class="text-small text-muted">期限: ${Utils.formatDate(task.due_date)}</div>` : ''}
                <div class="text-xs text-muted mt-1">
                    作成: ${Utils.formatDate(task.created_at)}
                    ${task.updated_at !== task.created_at ? ` | 更新: ${Utils.formatDate(task.updated_at)}` : ''}
                </div>
            </div>
        `).join('');
    },
    
    async createTask(taskData) {
        try {
            Utils.showLoading();
            const data = await APIClient.post('/tasks/', taskData);
            
            if (data) {
                Utils.showToast(data.message);
                closeTaskModal();
                await this.loadTasks();
                await Dashboard.loadStats();
                await Dashboard.loadRecentTasks();
            }
        } catch (error) {
            Utils.showToast(error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    async updateTask(taskId, taskData) {
        try {
            Utils.showLoading();
            const data = await APIClient.put(`/tasks/${taskId}`, taskData);
            
            if (data) {
                Utils.showToast(data.message);
                closeTaskModal();
                await this.loadTasks();
                await Dashboard.loadStats();
                await Dashboard.loadRecentTasks();
            }
        } catch (error) {
            Utils.showToast(error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    async deleteTask(taskId) {
        if (!confirm('このタスクを削除してもよろしいですか？')) {
            return;
        }
        
        try {
            Utils.showLoading();
            const data = await APIClient.delete(`/tasks/${taskId}`);
            
            if (data) {
                Utils.showToast(data.message);
                await this.loadTasks();
                await Dashboard.loadStats();
                await Dashboard.loadRecentTasks();
            }
        } catch (error) {
            Utils.showToast(error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    async editTask(taskId) {
        try {
            Utils.showLoading();
            const data = await APIClient.get(`/tasks/${taskId}`);
            
            if (data) {
                AppState.editingTask = data.task;
                showEditTaskModal();
            }
        } catch (error) {
            Utils.showToast(error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    }
};

// === カテゴリ管理 ===
const Categories = {
    async loadCategories() {
        try {
            const data = await APIClient.get('/categories/');
            if (data) {
                AppState.categories = data.categories;
                this.renderCategories();
                this.updateCategorySelects();
            }
        } catch (error) {
            Utils.showToast('カテゴリの読み込みに失敗しました', 'error');
        }
    },
    
    renderCategories() {
        const container = document.getElementById('categories-list');
        
        if (AppState.categories.length === 0) {
            container.innerHTML = '<p class="text-muted">まだカテゴリがありません。</p>';
            return;
        }
        
        container.innerHTML = AppState.categories.map(category => `
            <div class="category-card">
                <div class="category-actions">
                    <button class="btn btn-outline" onclick="Categories.editCategory(${category.id})" title="編集">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-danger" onclick="Categories.deleteCategory(${category.id})" title="削除">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <div class="category-header">
                    <div class="category-color" style="background-color: ${category.color}"></div>
                    <div class="category-name">${category.name}</div>
                </div>
                ${category.description ? `<div class="category-description">${category.description}</div>` : ''}
                <div class="category-stats">
                    <span>${category.task_count || 0} タスク</span>
                    <span class="text-xs">${Utils.formatDate(category.created_at)}</span>
                </div>
            </div>
        `).join('');
    },
    
    updateCategorySelects() {
        const taskCategorySelect = document.getElementById('task-category');
        const categoryFilterSelect = document.getElementById('category-filter');
        
        const categoryOptions = AppState.categories.map(category => 
            `<option value="${category.id}">${category.name}</option>`
        ).join('');
        
        taskCategorySelect.innerHTML = '<option value="">カテゴリなし</option>' + categoryOptions;
        categoryFilterSelect.innerHTML = '<option value="">すべてのカテゴリ</option>' + categoryOptions;
    },
    
    async createCategory(categoryData) {
        try {
            Utils.showLoading();
            const data = await APIClient.post('/categories/', categoryData);
            
            if (data) {
                Utils.showToast(data.message);
                closeCategoryModal();
                await this.loadCategories();
            }
        } catch (error) {
            Utils.showToast(error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    async updateCategory(categoryId, categoryData) {
        try {
            Utils.showLoading();
            const data = await APIClient.put(`/categories/${categoryId}`, categoryData);
            
            if (data) {
                Utils.showToast(data.message);
                closeCategoryModal();
                await this.loadCategories();
            }
        } catch (error) {
            Utils.showToast(error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    async deleteCategory(categoryId) {
        if (!confirm('このカテゴリを削除してもよろしいですか？')) {
            return;
        }
        
        try {
            Utils.showLoading();
            const data = await APIClient.delete(`/categories/${categoryId}`);
            
            if (data) {
                Utils.showToast(data.message);
                await this.loadCategories();
            }
        } catch (error) {
            Utils.showToast(error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    editCategory(categoryId) {
        const category = AppState.categories.find(c => c.id === categoryId);
        if (category) {
            AppState.editingCategory = category;
            showEditCategoryModal();
        }
    }
};

// === イベントハンドラー ===
async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    await Auth.login(username, password);
}

async function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    await Auth.register(username, email, password);
}

async function handleTaskSubmit(event) {
    event.preventDefault();
    
    const taskData = {
        title: document.getElementById('task-title').value,
        description: document.getElementById('task-description').value,
        priority: document.getElementById('task-priority').value,
        status: document.getElementById('task-status').value,
        category_id: document.getElementById('task-category').value || null,
        due_date: document.getElementById('task-due-date').value || null
    };
    
    if (AppState.editingTask) {
        await Tasks.updateTask(AppState.editingTask.id, taskData);
    } else {
        await Tasks.createTask(taskData);
    }
}

async function handleCategorySubmit(event) {
    event.preventDefault();
    
    const categoryData = {
        name: document.getElementById('category-name').value,
        description: document.getElementById('category-description').value,
        color: document.getElementById('category-color').value
    };
    
    if (AppState.editingCategory) {
        await Categories.updateCategory(AppState.editingCategory.id, categoryData);
    } else {
        await Categories.createCategory(categoryData);
    }
}

// === ビュー切り替え ===
function switchView(viewName) {
    // ナビゲーション更新
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.view === viewName) {
            item.classList.add('active');
        }
    });
    
    // ビュー切り替え
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });
    document.getElementById(`${viewName}-view`).classList.add('active');
    
    AppState.currentView = viewName;
    
    // データ読み込み
    if (viewName === 'dashboard') {
        Dashboard.init();
    } else if (viewName === 'tasks') {
        Tasks.loadTasks();
        Categories.loadCategories();
        // フィルター初期化
        updateClearButtonVisibility();
        updateActiveFilters({
            status: document.getElementById('status-filter').value,
            priority: document.getElementById('priority-filter').value,
            category_id: document.getElementById('category-filter').value
        });
    } else if (viewName === 'categories') {
        Categories.loadCategories();
    }
}

// === フィルタリング ===
function filterTasks() {
    const filters = {
        status: document.getElementById('status-filter').value,
        priority: document.getElementById('priority-filter').value,
        category_id: document.getElementById('category-filter').value
    };
    
    Tasks.loadTasks(filters);
    updateActiveFilters(filters);
    updateClearButtonVisibility();
}

function updateActiveFilters(filters) {
    const container = document.getElementById('active-filters');
    const activeFilters = [];
    
    // ステータスフィルター
    if (filters.status) {
        const statusText = Utils.getStatusText(filters.status);
        activeFilters.push({
            type: 'status',
            value: filters.status,
            label: `ステータス: ${statusText}`,
            icon: 'fas fa-circle-check'
        });
    }
    
    // 優先度フィルター
    if (filters.priority) {
        const priorityText = Utils.getPriorityText(filters.priority);
        activeFilters.push({
            type: 'priority',
            value: filters.priority,
            label: `優先度: ${priorityText}`,
            icon: 'fas fa-exclamation'
        });
    }
    
    // カテゴリフィルター
    if (filters.category_id) {
        const category = AppState.categories.find(c => c.id == filters.category_id);
        const categoryName = category ? category.name : 'カテゴリ';
        activeFilters.push({
            type: 'category',
            value: filters.category_id,
            label: `カテゴリ: ${categoryName}`,
            icon: 'fas fa-tag'
        });
    }
    
    if (activeFilters.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'flex';
    container.innerHTML = activeFilters.map(filter => `
        <div class="active-filter-tag">
            <i class="${filter.icon}"></i>
            <span>${filter.label}</span>
            <button class="remove-filter" onclick="removeFilter('${filter.type}')" title="フィルターを削除">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
}

function removeFilter(filterType) {
    const filterElementMap = {
        status: 'status-filter',
        priority: 'priority-filter',
        category: 'category-filter'
    };
    
    const elementId = filterElementMap[filterType];
    if (elementId) {
        document.getElementById(elementId).value = '';
        filterTasks();
    }
}

function clearAllFilters() {
    document.getElementById('status-filter').value = '';
    document.getElementById('priority-filter').value = '';
    document.getElementById('category-filter').value = '';
    filterTasks();
}

function updateClearButtonVisibility() {
    const hasActiveFilters = 
        document.getElementById('status-filter').value ||
        document.getElementById('priority-filter').value ||
        document.getElementById('category-filter').value;
        
    const clearBtn = document.getElementById('clear-filters-btn');
    clearBtn.style.display = hasActiveFilters ? 'flex' : 'none';
}

function toggleFilterCollapse() {
    const content = document.getElementById('filter-content');
    const toggleBtn = document.getElementById('filter-toggle-btn');
    const isCollapsed = content.classList.contains('collapsed');
    
    if (isCollapsed) {
        content.classList.remove('collapsed');
        toggleBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
    } else {
        content.classList.add('collapsed');
        toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
    }
}

// === モーダル管理 ===
function showCreateTaskModal() {
    AppState.editingTask = null;
    document.getElementById('task-modal-title').textContent = '新しいタスク';
    document.getElementById('task-submit-btn').innerHTML = '<i class="fas fa-save"></i> 作成';
    
    // フォームリセット
    document.getElementById('task-form').reset();
    document.getElementById('task-priority').value = 'medium';
    document.getElementById('task-status').value = 'pending';
    
    document.getElementById('task-modal').classList.add('active');
}

function showEditTaskModal() {
    const task = AppState.editingTask;
    document.getElementById('task-modal-title').textContent = 'タスク編集';
    document.getElementById('task-submit-btn').innerHTML = '<i class="fas fa-save"></i> 更新';
    
    // フォームに値を設定
    document.getElementById('task-title').value = task.title;
    document.getElementById('task-description').value = task.description || '';
    document.getElementById('task-priority').value = task.priority;
    document.getElementById('task-status').value = task.status;
    document.getElementById('task-category').value = task.category_id || '';
    document.getElementById('task-due-date').value = Utils.formatDateForInput(task.due_date);
    
    document.getElementById('task-modal').classList.add('active');
}

function closeTaskModal() {
    document.getElementById('task-modal').classList.remove('active');
    AppState.editingTask = null;
}

function showCreateCategoryModal() {
    AppState.editingCategory = null;
    document.getElementById('category-modal-title').textContent = '新しいカテゴリ';
    document.getElementById('category-submit-btn').innerHTML = '<i class="fas fa-save"></i> 作成';
    
    // フォームリセット
    document.getElementById('category-form').reset();
    document.getElementById('category-color').value = '#007bff';
    
    document.getElementById('category-modal').classList.add('active');
}

function showEditCategoryModal() {
    const category = AppState.editingCategory;
    document.getElementById('category-modal-title').textContent = 'カテゴリ編集';
    document.getElementById('category-submit-btn').innerHTML = '<i class="fas fa-save"></i> 更新';
    
    // フォームに値を設定
    document.getElementById('category-name').value = category.name;
    document.getElementById('category-description').value = category.description || '';
    document.getElementById('category-color').value = category.color;
    
    document.getElementById('category-modal').classList.add('active');
}

function closeCategoryModal() {
    document.getElementById('category-modal').classList.remove('active');
    AppState.editingCategory = null;
}

// === 認証UI ===
function showLogin() {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById('login-form').classList.add('active');
}

function showRegister() {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById('register-form').classList.add('active');
}

// === テーマ切り替え ===
function toggleTheme() {
    const body = document.body;
    const themeBtn = document.getElementById('theme-btn');
    
    if (body.dataset.theme === 'dark') {
        body.dataset.theme = 'light';
        themeBtn.innerHTML = '<i class="fas fa-moon"></i>';
        localStorage.setItem('theme', 'light');
    } else {
        body.dataset.theme = 'dark';
        themeBtn.innerHTML = '<i class="fas fa-sun"></i>';
        localStorage.setItem('theme', 'dark');
    }
}

// === その他のグローバル関数 ===
function logout() {
    Auth.logout();
}

// === イベントリスナー ===
document.addEventListener('DOMContentLoaded', () => {
    // テーマ初期化
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.dataset.theme = savedTheme;
    document.getElementById('theme-btn').innerHTML = savedTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    
    // ナビゲーション
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            switchView(item.dataset.view);
        });
    });
    
    // モーダル外クリックで閉じる
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
    
    // カラーピッカー更新
    document.getElementById('category-color').addEventListener('input', (e) => {
        document.getElementById('color-preview').style.backgroundColor = e.target.value;
    });
    
    // フィルターヘッダークリックイベント
    const filterHeader = document.querySelector('.filter-header');
    if (filterHeader) {
        filterHeader.addEventListener('click', (e) => {
            // コントロールボタンをクリックした場合は無視
            if (!e.target.closest('.filter-controls')) {
                toggleFilterCollapse();
            }
        });
    }
    
    // 認証状態チェック
    Auth.checkAuthentication();
});

// === レスポンシブ対応 ===
function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('open');
}

// モバイル用のハンバーガーメニュー（必要に応じて追加）
if (window.innerWidth <= 768) {
    // モバイル用の追加機能をここに実装
}