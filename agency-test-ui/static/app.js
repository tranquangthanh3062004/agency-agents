let currentDivision = 'engineering';
let currentAgentSlug = '';

document.addEventListener('DOMContentLoaded', () => {
    loadDivisions();
    setupEventListeners();
    
    // Load cached API key if exists
    const savedKey = localStorage.getItem('agency_router_key');
    if (savedKey) document.getElementById('apiKeyInput').value = savedKey;
});

function setupEventListeners() {
    document.getElementById('apiKeyInput').addEventListener('change', (e) => {
        localStorage.setItem('agency_router_key', e.target.value.trim());
    });

    document.getElementById('agentSelect').addEventListener('change', (e) => {
        currentAgentSlug = e.target.value;
    });

    document.getElementById('btnRun').addEventListener('click', executeAgentTask);
    document.getElementById('btnViewPrompt').addEventListener('click', viewAgentPrompt);
    document.getElementById('btnCloseModal').addEventListener('click', () => {
        document.getElementById('promptModal').style.display = 'none';
    });
}

async function loadDivisions() {
    try {
        const res = await fetch('/api/divisions');
        const data = await res.json();
        const container = document.getElementById('divisionsList');
        container.innerHTML = '';

        data.divisions.forEach((div, index) => {
            const item = document.createElement('div');
            item.className = `div-item ${index === 0 ? 'active' : ''}`;
            item.innerHTML = `
                <span>${div.label}</span>
                <span class="div-badge">${div.agent_count}</span>
            `;
            item.addEventListener('click', () => {
                document.querySelectorAll('.div-item').forEach(el => el.classList.remove('active'));
                item.classList.add('active');
                currentDivision = div.id;
                loadAgents(div.id);
            });
            container.appendChild(item);
        });

        if (data.divisions.length > 0) {
            currentDivision = data.divisions[0].id;
            loadAgents(currentDivision);
        }
    } catch (e) {
        console.error('Lỗi tải divisions:', e);
    }
}

async function loadAgents(divisionId) {
    try {
        const select = document.getElementById('agentSelect');
        select.innerHTML = '<option value="">Đang tải danh sách agents...</option>';
        
        const res = await fetch(`/api/agents/${divisionId}`);
        const data = await res.json();
        
        select.innerHTML = '';
        data.agents.forEach(agent => {
            const opt = document.createElement('option');
            opt.value = agent.slug;
            opt.textContent = agent.title;
            select.appendChild(opt);
        });

        if (data.agents.length > 0) {
            currentAgentSlug = data.agents[0].slug;
            select.value = currentAgentSlug;
        }
    } catch (e) {
        console.error('Lỗi tải agents:', e);
    }
}

async function viewAgentPrompt() {
    if (!currentDivision || !currentAgentSlug) {
        alert('Vui lòng chọn 1 Agent trước!');
        return;
    }

    try {
        const res = await fetch(`/api/agent-detail/${currentDivision}/${currentAgentSlug}`);
        const data = await res.json();
        
        document.getElementById('modalTitle').textContent = `System Prompt: ${currentAgentSlug}.md`;
        document.getElementById('modalContent').textContent = data.content;
        document.getElementById('promptModal').style.display = 'flex';
    } catch (e) {
        alert('Không thể tải file agent: ' + e);
    }
}

async function executeAgentTask() {
    const apiKey = document.getElementById('apiKeyInput').value.trim();
    const routerBaseUrl = document.getElementById('routerUrlSelect').value;
    const modelName = document.getElementById('modelSelect').value;
    const taskPrompt = document.getElementById('taskInput').value.trim();
    const resultBox = document.getElementById('resultBox');
    const loader = document.getElementById('loader');
    const statusMeta = document.getElementById('statusMeta');

    if (!apiKey) {
        alert('Vui lòng nhập API Key (OpenRouter hoặc Omni Router) để tiếp tục!');
        document.getElementById('apiKeyInput').focus();
        return;
    }

    if (!taskPrompt) {
        alert('Vui lòng nhập yêu cầu công việc cho Agent!');
        return;
    }

    // UI Loading state
    loader.style.display = 'inline-block';
    resultBox.innerHTML = '<p style="color: #94a3b8;">Agent đang suy nghĩ và thực thi theo quy trình chuyên môn...</p>';
    statusMeta.textContent = 'Đang gọi API...';

    try {
        const res = await fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                division: currentDivision,
                agent_slug: currentAgentSlug,
                task_prompt: taskPrompt,
                api_key: apiKey,
                router_base_url: routerBaseUrl,
                model_name: modelName
            })
        });

        const data = await res.json();
        loader.style.display = 'none';

        if (!data.success) {
            resultBox.innerHTML = `<div style="color: #f87171; padding: 12px; background: rgba(239,68,68,0.1); border-radius: 6px;">
                <strong>⚠️ Lỗi:</strong> ${data.error}
            </div>`;
            statusMeta.textContent = 'Thất bại';
            return;
        }

        // Render Markdown safely
        if (window.marked) {
            resultBox.innerHTML = marked.parse(data.result);
        } else {
            resultBox.textContent = data.result;
        }

        statusMeta.textContent = `Model: ${data.model_used} | Tokens: ${data.usage?.total_tokens || 'N/A'}`;
    } catch (e) {
        loader.style.display = 'none';
        resultBox.innerHTML = `<p style="color: #f87171;">Lỗi gửi request: ${e}</p>`;
        statusMeta.textContent = 'Lỗi kết nối';
    }
}

