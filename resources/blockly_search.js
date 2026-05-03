// ============================================================
// BLOCK SEARCHER WITH HIGHLIGHT
//
// FIX: Substituído self. por this. no constructor.
// 'self' em contexto de classe JS refere-se ao objeto global (window),
// não à instância — as propriedades eram criadas em window em vez de
// na instância, quebrando completamente a classe.
// ============================================================

class BlockSearcher {
    constructor(workspace) {
        this.workspace        = workspace;
        this.searchInput      = null;
        this.searchPanel      = null;      // FIX: era self.searchPanel
        this.currentHighlights = [];       // FIX: era self.currentHighlights
        this.currentIndex     = -1;        // FIX: era self.currentIndex
        this.currentResults   = [];
        this.panel            = null;
        this.init();                       // FIX: era self.init()
    }

    init() {
        this.createSearchPanel();
        this.registerShortcuts();
    }

    createSearchPanel() {
        // Create floating search panel
        const panel = document.createElement('div');
        panel.id = 'block-search-panel';
        panel.innerHTML = `
            <div class="search-header">
                <span class="material-icons">search</span>
                <span>Search Blocks</span>
                <button class="search-close" onclick="blockSearcher.hide()">×</button>
            </div>
            <div class="search-body">
                <input type="text" id="block-search-input" placeholder="Type to search blocks..." autocomplete="off">
                <div class="search-stats">
                    <span id="search-results-count">0</span> blocks found
                </div>
                <div class="search-navigation">
                    <button class="search-nav-btn" onclick="blockSearcher.prevResult()">← Previous</button>
                    <button class="search-nav-btn" onclick="blockSearcher.nextResult()">Next →</button>
                </div>
                <div class="search-options">
                    <label>
                        <input type="checkbox" id="search-fields"> Search field values
                    </label>
                    <label>
                        <input type="checkbox" id="search-case-sensitive"> Case sensitive
                    </label>
                </div>
            </div>
        `;

        document.body.appendChild(panel);

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            #block-search-panel {
                position: fixed;
                top: 60px;
                right: 380px;
                width: 320px;
                background: linear-gradient(135deg, #0f1729, #162040);
                border: 2px solid #00d2ff;
                border-radius: 12px;
                z-index: 10000;
                box-shadow: 0 8px 32px rgba(0,0,0,0.4);
                font-family: 'Nunito', sans-serif;
                backdrop-filter: blur(8px);
            }
            .search-header {
                padding: 12px 16px;
                background: rgba(0,210,255,0.1);
                border-bottom: 1px solid #1e3058;
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: bold;
                color: #00d2ff;
                border-radius: 10px 10px 0 0;
            }
            .search-close {
                margin-left: auto;
                background: none;
                border: none;
                color: #5a7aa0;
                font-size: 20px;
                cursor: pointer;
                padding: 0 4px;
            }
            .search-close:hover { color: #ff4d6d; }
            .search-body { padding: 16px; }
            #block-search-input {
                width: 100%;
                padding: 10px 12px;
                background: #0d1117;
                border: 1px solid #1e3058;
                border-radius: 8px;
                color: #d8eaff;
                font-size: 14px;
                margin-bottom: 12px;
                box-sizing: border-box;
            }
            #block-search-input:focus {
                outline: none;
                border-color: #00d2ff;
            }
            .search-stats {
                font-size: 11px;
                color: #5a7aa0;
                margin-bottom: 12px;
                text-align: center;
            }
            .search-navigation {
                display: flex;
                gap: 8px;
                margin-bottom: 12px;
            }
            .search-nav-btn {
                flex: 1;
                padding: 6px;
                background: #1e3058;
                border: none;
                border-radius: 6px;
                color: #d8eaff;
                cursor: pointer;
                font-weight: bold;
            }
            .search-nav-btn:hover {
                background: #00d2ff;
                color: #0f1729;
            }
            .search-options {
                display: flex;
                gap: 16px;
                font-size: 11px;
                color: #5a7aa0;
                margin-top: 8px;
            }
            .search-options label {
                display: flex;
                align-items: center;
                gap: 4px;
                cursor: pointer;
            }
            .block-highlight {
                animation: blockPulse 0.6s ease-in-out 3;
                box-shadow: 0 0 0 3px #00ff88, 0 0 20px rgba(0,255,136,0.5);
                border-radius: 8px;
            }
            @keyframes blockPulse {
                0%, 100% {
                    box-shadow: 0 0 0 3px #00ff88, 0 0 20px rgba(0,255,136,0.5);
                    filter: brightness(1);
                }
                50% {
                    box-shadow: 0 0 0 6px #00ff88, 0 0 30px rgba(0,255,136,0.8);
                    filter: brightness(1.2);
                }
            }
        `;
        document.head.appendChild(style);

        this.searchInput = document.getElementById('block-search-input');
        this.searchInput.addEventListener('input', () => this.search());
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.nextResult();
            if (e.key === 'Escape') this.hide();
        });

        this.panel = panel;
        this.panel.style.display = 'none';
    }

    show() {
        this.panel.style.display = 'block';
        this.searchInput.focus();
        this.showShortcutHint();
    }

    hide() {
        this.panel.style.display = 'none';
        this.clearHighlights();
    }

    registerShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+F or Cmd+F to open search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                this.show();
            }
            // ESC to close
            if (e.key === 'Escape' && this.panel && this.panel.style.display === 'block') {
                this.hide();
            }
            // F3 to next result
            if (e.key === 'F3') {
                e.preventDefault();
                if (this.panel && this.panel.style.display === 'block') {
                    e.shiftKey ? this.prevResult() : this.nextResult();
                } else {
                    this.show();
                }
            }
        });
    }

    showShortcutHint() {
        const hint = document.createElement('div');
        hint.className = 'shortcut-hint';
        hint.innerHTML = '⌘/Ctrl+F to search | F3 next | ESC close';
        hint.style.cssText = `
            position: fixed;
            bottom: 10px;
            right: 400px;
            background: rgba(0,0,0,0.7);
            color: #5a7aa0;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 10px;
            z-index: 10001;
            pointer-events: none;
        `;
        document.body.appendChild(hint);
        setTimeout(() => hint.remove(), 3000);
    }

    search() {
        const query = this.searchInput.value.trim();
        const searchFields = document.getElementById('search-fields').checked;
        const caseSensitive = document.getElementById('search-case-sensitive').checked;

        if (!query) {
            this.clearHighlights();
            document.getElementById('search-results-count').textContent = '0';
            return;
        }

        const searchTerm = caseSensitive ? query : query.toLowerCase();
        const blocks = this.workspace.getAllBlocks(true);
        const results = [];

        blocks.forEach(block => {
            let match = false;
            let matchText = '';

            // Search block type name
            let typeName = block.type;
            if (!caseSensitive) typeName = typeName.toLowerCase();
            if (typeName.includes(searchTerm)) {
                match = true;
                matchText = block.type;
            }

            // Search field values
            if (searchFields && !match) {
                try {
                    const fields = block.getFields ? block.getFields() : {};
                    for (const [key, field] of Object.entries(fields)) {
                        let value = field.getValue ? field.getValue() : '';
                        if (typeof value === 'string') {
                            if (!caseSensitive) value = value.toLowerCase();
                            if (value.includes(searchTerm)) {
                                match = true;
                                matchText = `${key}: ${field.getValue()}`;
                                break;
                            }
                        }
                    }
                } catch (e) { /* ignore field access errors */ }
            }

            // Search input labels (for value inputs)
            if (searchFields && !match) {
                try {
                    const inputs = block.getInputs ? block.getInputs(true) : [];
                    for (const input of inputs) {
                        if (!input.connection) continue;
                        const target = input.connection.targetBlock();
                        if (target && target.type === 'ab_number') {
                            let numVal = String(target.getFieldValue('NUM') || '');
                            if (!caseSensitive) numVal = numVal.toLowerCase();
                            if (numVal.includes(searchTerm)) {
                                match = true;
                                matchText = `value: ${target.getFieldValue('NUM')}`;
                                break;
                            }
                        }
                        if (target && (target.type === 'ab_text' || target.type === 'ab_text_literal')) {
                            let textVal = target.getFieldValue('TEXT') || '';
                            if (!caseSensitive) textVal = textVal.toLowerCase();
                            if (textVal.includes(searchTerm)) {
                                match = true;
                                matchText = `text: ${target.getFieldValue('TEXT')}`;
                                break;
                            }
                        }
                    }
                } catch (e) { /* ignore */ }
            }

            if (match) {
                results.push({ block, matchText });
            }
        });

        this.clearHighlights();
        this.currentResults = results;
        this.currentIndex = results.length > 0 ? 0 : -1;

        document.getElementById('search-results-count').textContent = results.length;

        if (results.length > 0) {
            this.highlightResult(this.currentIndex);
        }
    }

    highlightResult(index) {
        if (index < 0 || !this.currentResults || index >= this.currentResults.length) return;

        this.currentHighlights.forEach(el => el.classList.remove('block-highlight'));
        this.currentHighlights = [];

        const result = this.currentResults[index];
        const block = result.block;

        const blockId = block.id;
        const svg = document.querySelector(`[data-id="${blockId}"]`) ||
                    document.querySelector(`path[data-id="${blockId}"]`) ||
                    (block.getSvgRoot ? block.getSvgRoot() : null);

        if (svg) {
            svg.classList.add('block-highlight');
            this.currentHighlights.push(svg);

            // Scroll to block
            try {
                const bounds = svg.getBoundingClientRect();
                const workspaceScroll = document.querySelector('.blocklyScrollDiv');
                if (workspaceScroll) {
                    workspaceScroll.scrollTo({
                        left: bounds.left + workspaceScroll.scrollLeft - 100,
                        top:  bounds.top  + workspaceScroll.scrollTop  - 100,
                        behavior: 'smooth',
                    });
                }
            } catch (e) { /* scroll errors are non-critical */ }

            this.showMatchTooltip(svg, result.matchText);
        }
    }

    showMatchTooltip(element, matchText) {
        const oldTooltip = document.querySelector('.search-match-tooltip');
        if (oldTooltip) oldTooltip.remove();

        const tooltip = document.createElement('div');
        tooltip.className = 'search-match-tooltip';
        tooltip.innerHTML = `🔍 Matched: "${matchText}"`;
        tooltip.style.cssText = `
            position: absolute;
            background: #00ff88;
            color: #0f1729;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
            font-family: 'Nunito', sans-serif;
            z-index: 10002;
            white-space: nowrap;
            pointer-events: none;
            animation: fadeOut 2s ease-out forwards;
        `;

        try {
            const rect = element.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top  = (rect.top - 25) + 'px';
        } catch (e) {}

        document.body.appendChild(tooltip);
        setTimeout(() => tooltip.remove(), 2000);
    }

    clearHighlights() {
        this.currentHighlights.forEach(el => el.classList.remove('block-highlight'));
        this.currentHighlights = [];
    }

    nextResult() {
        if (!this.currentResults || this.currentResults.length === 0) return;
        this.currentIndex = (this.currentIndex + 1) % this.currentResults.length;
        this.highlightResult(this.currentIndex);
    }

    prevResult() {
        if (!this.currentResults || this.currentResults.length === 0) return;
        this.currentIndex = (this.currentIndex - 1 + this.currentResults.length) % this.currentResults.length;
        this.highlightResult(this.currentIndex);
    }
}

let blockSearcher = null;

function initBlockSearcher(workspace) {
    blockSearcher = new BlockSearcher(workspace);
}

// Add search button to header
function addSearchButton() {
    const header = document.getElementById('header');
    if (!header) return;
    if (document.getElementById('block-search-btn')) return; // already added

    const spacer = header.querySelector('.spacer');

    const searchBtn = document.createElement('button');
    searchBtn.id = 'block-search-btn';
    searchBtn.className = 'btn btn-refresh';
    searchBtn.innerHTML = '<span class="material-icons">search</span> Search (Ctrl+F)';
    searchBtn.onclick = () => blockSearcher && blockSearcher.show();
    searchBtn.style.marginRight = '8px';

    if (spacer) spacer.parentNode.insertBefore(searchBtn, spacer);
    else header.appendChild(searchBtn);
}

// Integrate with existing initBlockly
if (typeof originalInitBlockly === 'undefined') {
    const originalInit = typeof initBlockly !== 'undefined' ? initBlockly : null;
    if (originalInit) {
        initBlockly = function() {
            originalInit();
            initBlockSearcher(workspace);
            addSearchButton();
        };
    }
}