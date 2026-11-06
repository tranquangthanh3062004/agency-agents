let currentDivision = 'engineering';
let currentAgentSlug = '';
let appMode = 'single'; // 'single' or 'pipeline'
let currentResultMarkdown = '';
let allAgentsList = [];

document.addEventListener('DOMContentLoaded', () => {
    loadDivisions();
    setupEventListeners();
    
    // Load cached API key if exists
    const savedKey = localStorage.getItem('agency_router_key');
    if (savedKey) document.getElementById('apiKeyInput').value = savedKey;

    // Check if task transferred from Admin Portal
    const autoTask = localStorage.getItem('agency_auto_task');
    if (autoTask) {
        document.getElementById('taskInput').value = autoTask;
        localStorage.removeItem('agency_auto_task');
    }
});

function setupEventListeners() {
    // Mode switcher
    document.getElementById('btnModeSingle').addEventListener('click', () => switchMode('single'));
    document.getElementById('btnModePipeline').addEventListener('click', () => switchMode('pipeline'));

    // Cache key
    document.getElementById('apiKeyInput').addEventListener('change', (e) => {
        localStorage.setItem('agency_router_key', e.target.value.trim());
    });

    document.getElementById('agentSelect').addEventListener('change', (e) => {
        currentAgentSlug = e.target.value;
    });

    document.getElementById('pipelinePresetSelect').addEventListener('change', (e) => {
        const customBox = document.getElementById('customPipelineBox');
        if (e.target.value === 'custom') {
            customBox.style.display = 'flex';
            populateCustomSelects();
        } else {
            customBox.style.display = 'none';
        }
    });

    // Execute button
    document.getElementById('btnRun').addEventListener('click', handleExecute);

    // Modal
    document.getElementById('btnViewPrompt').addEventListener('click', viewAgentPrompt);
    document.getElementById('btnCloseModal').addEventListener('click', () => {
        document.getElementById('promptModal').style.display = 'none';
    });

    // Tabs
    document.getElementById('tabDoc').addEventListener('click', () => switchTab('doc'));
    document.getElementById('tabPreview').addEventListener('click', () => {
        switchTab('preview');
        renderLivePreview(currentResultMarkdown);
    });
    document.getElementById('tabPipelineSteps').addEventListener('click', () => switchTab('pipelineSteps'));
    document.getElementById('btnRefreshPreview').addEventListener('click', () => renderLivePreview(currentResultMarkdown));

    // Copy & Download
    document.getElementById('btnCopy').addEventListener('click', copyResult);
    document.getElementById('btnDownload').addEventListener('click', downloadMarkdown);
    document.getElementById('btnRefine').addEventListener('click', handleRefine);
}

function switchMode(mode) {
    appMode = mode;
    const btnSingle = document.getElementById('btnModeSingle');
    const btnPipeline = document.getElementById('btnModePipeline');
    const agentSelect = document.getElementById('agentSelect');
    const pipelinePresetSelect = document.getElementById('pipelinePresetSelect');
    const customBox = document.getElementById('customPipelineBox');
    const btnRunText = document.getElementById('btnRunText');
    const tabPipelineSteps = document.getElementById('tabPipelineSteps');
    const sidebarTitle = document.getElementById('sidebarTitle');

    if (mode === 'single') {
        btnSingle.classList.add('active');
        btnPipeline.classList.remove('active');
        agentSelect.style.display = 'inline-block';
        pipelinePresetSelect.style.display = 'none';
        customBox.style.display = 'none';
        btnRunText.textContent = '🚀 Thực Thi Với Agent';
        tabPipelineSteps.style.display = 'none';
        sidebarTitle.textContent = '18 PHÒNG BAN';
        switchTab('doc');
    } else {
        btnPipeline.classList.add('active');
        btnSingle.classList.remove('active');
        agentSelect.style.display = 'none';
        pipelinePresetSelect.style.display = 'inline-block';
        if (pipelinePresetSelect.value === 'custom') customBox.style.display = 'flex';
        btnRunText.textContent = '👥 Kích Hoạt NEXUS Pipeline';
        tabPipelineSteps.style.display = 'inline-block';
        sidebarTitle.textContent = 'CHỌN ĐỘI HÌNH PHỐI HỢP';
    }
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    if (tabName === 'doc') {
        document.getElementById('tabDoc').classList.add('active');
        document.getElementById('contentDoc').classList.add('active');
    } else if (tabName === 'preview') {
        document.getElementById('tabPreview').classList.add('active');
        document.getElementById('contentPreview').classList.add('active');
    } else if (tabName === 'pipelineSteps') {
        document.getElementById('tabPipelineSteps').classList.add('active');
        document.getElementById('contentPipelineSteps').classList.add('active');
    }
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

        // Cache all agents list for custom pipeline
        fetchAllAgentsForCustomPipeline();
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

async function fetchAllAgentsForCustomPipeline() {
    try {
        const res = await fetch('/api/divisions');
        const divData = await res.json();
        allAgentsList = [];

        for (const div of divData.divisions) {
            const aRes = await fetch(`/api/agents/${div.id}`);
            const aData = await aRes.json();
            aData.agents.forEach(a => {
                allAgentsList.push({
                    division: div.id,
                    slug: a.slug,
                    title: `[${div.label}] ${a.title}`
                });
            });
        }
    } catch (e) {
        console.error('Lỗi load all agents:', e);
    }
}

function populateCustomSelects() {
    const s1 = document.getElementById('customStep1Select');
    const s2 = document.getElementById('customStep2Select');
    s1.innerHTML = '';
    s2.innerHTML = '';

    allAgentsList.forEach(a => {
        const o1 = document.createElement('option');
        o1.value = `${a.division}|${a.slug}`;
        o1.textContent = a.title;
        s1.appendChild(o1);

        const o2 = document.createElement('option');
        o2.value = `${a.division}|${a.slug}`;
        o2.textContent = a.title;
        s2.appendChild(o2);
    });

    if (s2.options.length > 1) s2.selectedIndex = 1;
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

async function handleExecute() {
    if (appMode === 'single') {
        await executeSingleAgent();
    } else {
        await executePipeline();
    }
}

async function executeSingleAgent() {
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

    loader.style.display = 'inline-block';
    resultBox.innerHTML = '<p style="color: #94a3b8;">Chuyên gia AI đang phân tích và thực thi theo chuẩn chuyên môn...</p>';
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

        currentResultMarkdown = data.result;
        resultBox.innerHTML = marked.parse(currentResultMarkdown);
        statusMeta.textContent = `Hoàn thành (${data.model_used})`;
        document.getElementById('refineBar').style.display = 'flex';

        // Check if there's HTML code to show preview indicator
        if (hasHtmlCode(currentResultMarkdown)) {
            document.getElementById('tabPreview').textContent = '🖥️ Live Code Preview (✨ Có sẵn)';
        } else {
            document.getElementById('tabPreview').textContent = '🖥️ Live Code Preview';
        }
    } catch (e) {
        loader.style.display = 'none';
        resultBox.innerHTML = `<p style="color: #f87171;">Lỗi gửi request: ${e}</p>`;
        statusMeta.textContent = 'Lỗi kết nối';
    }
}

async function executePipeline() {
    const apiKey = document.getElementById('apiKeyInput').value.trim();
    const routerBaseUrl = document.getElementById('routerUrlSelect').value;
    const modelName = document.getElementById('modelSelect').value;
    const taskPrompt = document.getElementById('taskInput').value.trim();
    const preset = document.getElementById('pipelinePresetSelect').value;
    const resultBox = document.getElementById('resultBox');
    const loader = document.getElementById('loader');
    const statusMeta = document.getElementById('statusMeta');
    const timeline = document.getElementById('pipelineTimeline');

    if (!apiKey) {
        alert('Vui lòng nhập API Key để chạy Pipeline!');
        document.getElementById('apiKeyInput').focus();
        return;
    }

    if (!taskPrompt) {
        alert('Vui lòng nhập yêu cầu dự án để kích hoạt Pipeline!');
        return;
    }

    // Build steps based on preset
    let steps = [];
    let pipelineName = 'NEXUS Pipeline';

    if (preset === 'dev-qa') {
        pipelineName = 'Dev ➔ QA Reality Check';
        steps = [
            { division: 'engineering', agent_slug: 'engineering-frontend-developer', label: '1. Frontend Developer (Code)' },
            { division: 'testing', agent_slug: 'testing-reality-checker', label: '2. Reality Checker (QA & Thẩm định)' }
        ];
    } else if (preset === 'vn-launch') {
        pipelineName = 'Vietnam Business Launch Protocol';
        steps = [
            { division: 'specialized', agent_slug: 'specialized-vietnamese-legal-compliance', label: '1. Pháp Lý Doanh Nghiệp VN' },
            { division: 'specialized', agent_slug: 'specialized-vietnamese-tax-accounting', label: '2. Kế Toán & Thuế VN' },
            { division: 'specialized', agent_slug: 'specialized-vietnamese-ecommerce-strategist', label: '3. Chiến Lược TMĐT Sàn VN' }
        ];
    } else if (preset === 'marketing-growth') {
        pipelineName = 'Growth & Content Engine';
        steps = [
            { division: 'marketing', agent_slug: 'marketing-content-creator', label: '1. Content Creator (Nội dung)' },
            { division: 'marketing', agent_slug: 'marketing-seo-specialist', label: '2. SEO Specialist (Tối ưu tìm kiếm)' }
        ];
    } else if (preset === 'custom') {
        pipelineName = 'Custom Multi-Agent Pipeline';
        const [div1, slug1] = document.getElementById('customStep1Select').value.split('|');
        const [div2, slug2] = document.getElementById('customStep2Select').value.split('|');
        steps = [
            { division: div1, agent_slug: slug1, label: `1. ${slug1}` },
            { division: div2, agent_slug: slug2, label: `2. ${slug2}` }
        ];
    }

    loader.style.display = 'inline-block';
    statusMeta.textContent = 'Đang khởi chạy NEXUS Pipeline...';
    resultBox.innerHTML = `<p style="color: #38bdf8;">Đang kích hoạt quy trình bàn giao NEXUS giữa ${steps.length} chuyên gia...</p>`;
    timeline.innerHTML = '';

    try {
        const res = await fetch('/api/execute-pipeline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pipeline_name: pipelineName,
                task_prompt: taskPrompt,
                steps: steps,
                api_key: apiKey,
                router_base_url: routerBaseUrl,
                model_name: modelName
            })
        });

        const data = await res.json();
        loader.style.display = 'none';

        if (!data.success) {
            resultBox.innerHTML = `<div style="color: #f87171; padding: 12px; background: rgba(239,68,68,0.1); border-radius: 6px;">
                <strong>⚠️ Lỗi Pipeline:</strong> ${data.error}
            </div>`;
            statusMeta.textContent = 'Pipeline thất bại';
            return;
        }

        // Render final deliverable
        currentResultMarkdown = data.final_result;
        resultBox.innerHTML = marked.parse(currentResultMarkdown);
        statusMeta.textContent = `Pipeline hoàn thành (${steps.length} bước)`;
        document.getElementById('refineBar').style.display = 'flex';

        // Render timeline cards
        timeline.innerHTML = '';
        data.steps.forEach(step => {
            const card = document.createElement('div');
            card.className = 'timeline-card';
            card.innerHTML = `
                <div class="timeline-card-header">
                    <span class="timeline-card-title">${step.label}</span>
                    <span style="font-size: 0.72rem; color: #4ade80;">✓ Đã bàn giao</span>
                </div>
                <div class="timeline-card-body">${escapeHtml(step.output)}</div>
            `;
            timeline.appendChild(card);
        });

        if (hasHtmlCode(currentResultMarkdown)) {
            document.getElementById('tabPreview').textContent = '🖥️ Live Code Preview (✨ Có sẵn)';
        }
    } catch (e) {
        loader.style.display = 'none';
        resultBox.innerHTML = `<p style="color: #f87171;">Lỗi gửi request: ${e}</p>`;
        statusMeta.textContent = 'Lỗi kết nối';
    }
}

// Live Code Preview Sandbox
function hasHtmlCode(md) {
    return md.includes('```html') || md.includes('<!DOCTYPE html>') || md.includes('<html');
}

function renderLivePreview(markdown) {
    const frame = document.getElementById('previewFrame');
    if (!markdown) {
        frame.srcdoc = '<p style="font-family: sans-serif; padding: 20px; color: #64748b;">Chưa có mã HTML để render.</p>';
        return;
    }

    let code = '';
    const htmlBlockRegex = /```html\s*([\s\S]*?)\s*```/i;
    const match = markdown.match(htmlBlockRegex);

    if (match && match[1]) {
        code = match[1];
    } else if (markdown.includes('<html') || markdown.includes('<!DOCTYPE html>')) {
        code = markdown;
    } else {
        frame.srcdoc = '<p style="font-family: sans-serif; padding: 20px; color: #64748b;">Chưa phát hiện khối mã HTML nào trong phản hồi này.</p>';
        return;
    }

    // Inject Tailwind CDN if not present for instant professional styling
    let injectedHtml = code;
    if (!injectedHtml.includes('tailwindcss.com')) {
        injectedHtml = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="p-4 bg-slate-50 text-slate-900">
                ${code}
            </body>
            </html>
        `;
    }

    frame.srcdoc = injectedHtml;
}

function copyResult() {
    if (!currentResultMarkdown) {
        alert('Không có nội dung để sao chép!');
        return;
    }
    navigator.clipboard.writeText(currentResultMarkdown).then(() => {
        alert('Đã sao chép toàn bộ kết quả vào bộ nhớ tạm!');
    });
}

function downloadMarkdown() {
    if (!currentResultMarkdown) {
        alert('Không có nội dung để tải về!');
        return;
    }
    const blob = new Blob([currentResultMarkdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Agency-Deliverable-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function handleRefine() {
    const feedback = document.getElementById('refineInput').value.trim();
    if (!feedback) {
        alert('Vui lòng nhập yêu cầu tinh chỉnh!');
        return;
    }
    if (!currentResultMarkdown) {
        alert('Chưa có sản phẩm nào để tinh chỉnh!');
        return;
    }
    const apiKey = document.getElementById('apiKeyInput').value.trim();
    const routerBaseUrl = document.getElementById('routerUrlSelect').value;
    const modelName = document.getElementById('modelSelect').value;
    const loader = document.getElementById('loader');
    const resultBox = document.getElementById('resultBox');
    const statusMeta = document.getElementById('statusMeta');
    const btnRefine = document.getElementById('btnRefine');

    btnRefine.disabled = true;
    btnRefine.textContent = '⏳ Đang sửa...';
    loader.style.display = 'inline-block';
    statusMeta.textContent = 'Đang tinh chỉnh theo yêu cầu...';

    try {
        const res = await fetch('/api/refine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                current_content: currentResultMarkdown,
                feedback_instruction: feedback,
                api_key: apiKey,
                router_base_url: routerBaseUrl,
                model_name: modelName
            })
        });
        const data = await res.json();
        btnRefine.disabled = false;
        btnRefine.textContent = '⚡ Tinh Chỉnh';
        loader.style.display = 'none';

        if (!data.success) {
            alert('Lỗi chỉnh sửa: ' + data.error);
            return;
        }

        currentResultMarkdown = data.result;
        resultBox.innerHTML = marked.parse(currentResultMarkdown);
        statusMeta.textContent = `Đã tinh chỉnh thành công (${data.model_used})`;
        document.getElementById('refineInput').value = '';

        if (hasHtmlCode(currentResultMarkdown)) {
            document.getElementById('tabPreview').textContent = '🖥️ Live Code Preview (✨ Có sẵn)';
            renderLivePreview(currentResultMarkdown);
        }
    } catch (e) {
        btnRefine.disabled = false;
        btnRefine.textContent = '⚡ Tinh Chỉnh';
        loader.style.display = 'none';
        alert('Lỗi kết nối tinh chỉnh: ' + e);
    }
}

