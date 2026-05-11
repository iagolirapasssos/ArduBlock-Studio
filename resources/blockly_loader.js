// ============================================================
// LAZY LOADING BLOCK MANAGER
// ============================================================

class LazyBlockLoader {
    constructor() {
        self.loadedCategories = new Set();
        self.pendingLoads = [];
        self.isLoading = false;
        self.blockCache = new Map();
        this.init();
    }
    
    init() {
        // Define block categories and their dependencies
        this.categories = {
            'core': {
                priority: 1,
                blocks: ['ab_program', 'ab_comment', 'controls_if', 'ab_while', 'ab_for'],
                script: null  // Already in main
            },
            'digital': {
                priority: 2,
                blocks: ['ab_pin_mode', 'ab_digital_write', 'ab_digital_read'],
                script: null
            },
            'analog': {
                priority: 2,
                blocks: ['ab_analog_write', 'ab_analog_read', 'ab_pwm_set'],
                script: null
            },
            'time': {
                priority: 2,
                blocks: ['ab_delay_ms', 'ab_delay_sec', 'ab_millis', 'ab_micros'],
                script: null
            },
            'serial': {
                priority: 3,
                blocks: ['ab_serial_begin', 'ab_serial_print', 'ab_serial_println', 
                        'ab_serial_available', 'ab_serial_read'],
                script: null
            },
            'math': {
                priority: 3,
                blocks: ['ab_number', 'ab_arithmetic', 'ab_map', 'ab_constrain', 
                        'ab_random', 'ab_abs'],
                script: null
            },
            'logic': {
                priority: 3,
                blocks: ['ab_compare', 'ab_logic_op', 'ab_not', 'ab_bool'],
                script: null
            },
            'variables': {
                priority: 3,
                blocks: ['ab_global_var', 'ab_local_var', 'ab_var_set', 'ab_var_get', 'ab_text'],
                script: null
            },
            'functions': {
                priority: 4,
                blocks: ['procedures_defnoreturn', 'procedures_defreturn', 
                        'procedures_callnoreturn', 'ab_return'],
                script: null
            },
            'leds': {
                priority: 4,
                blocks: ['ab_led_on', 'ab_led_off', 'ab_tone', 'ab_notone'],
                script: null
            },
            'servo': {
                priority: 4,
                blocks: ['ab_servo_attach', 'ab_servo_write', 'ab_servo_read'],
                script: null
            },
            'sensors': {
                priority: 4,
                blocks: ['ab_ultrasonic', 'ab_dht', 'ab_ldr', 'ab_button'],
                script: null
            }
        };
        
        // Register lazy loading for toolbox
        this.hijackToolbox();
        
        // Start loading high priority blocks
        this.loadPriorityBlocks();
    }
    
    hijackToolbox() {
        // Intercept toolbox category clicks
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    const categories = document.querySelectorAll('.blocklyTreeRow');
                    categories.forEach(cat => {
                        if (!cat.dataset.lazyRegistered) {
                            cat.dataset.lazyRegistered = 'true';
                            cat.addEventListener('click', (e) => {
                                const categoryName = cat.querySelector('.blocklyTreeLabel')?.textContent;
                                if (categoryName) {
                                    this.loadCategory(categoryName);
                                }
                            });
                        }
                    });
                }
            });
        });
        
        observer.observe(document.querySelector('.blocklyToolboxDiv'), {
            childList: true,
            subtree: true
        });
    }
    
    loadPriorityBlocks() {
        // Load all priority 1 and 2 blocks immediately
        const highPriority = ['core', 'digital', 'analog', 'time'];
        highPriority.forEach(cat => {
            if (this.categories[cat]) {
                this.loadCategoryBlocks(cat);
            }
        });
    }
    
    loadCategory(categoryName) {
        // Map category name to internal category key
        const categoryMap = {
            'Structure': 'core',
            'Digital Pins': 'digital',
            'Analog Pins': 'analog',
            'Time': 'time',
            'Serial Monitor': 'serial',
            'Mathematics': 'math',
            'Logic': 'logic',
            'Variables': 'variables',
            'Functions': 'functions',
            'LEDs and Outputs': 'leds',
            'Servo Motor': 'servo',
            'Sensors': 'sensors'
        };
        
        const key = categoryMap[categoryName];
        if (key && !this.loadedCategories.has(key)) {
            this.loadCategoryBlocks(key);
        }
    }
    
    loadCategoryBlocks(categoryKey) {
        if (this.loadedCategories.has(categoryKey)) return;
        
        this.pendingLoads.push(categoryKey);
        this.processQueue();
    }
    
    async processQueue() {
        if (this.isLoading || this.pendingLoads.length === 0) return;
        
        this.isLoading = true;
        const category = this.pendingLoads.shift();
        
        // Show loading indicator
        this.showLoadingIndicator(category);
        
        // Simulate async loading (or actual network request)
        await this.delay(10);
        
        // Mark as loaded
        this.loadedCategories.add(category);
        this.hideLoadingIndicator(category);
        
        // Update toolbox to show loaded blocks
        this.updateToolboxCategory(category);
        
        this.isLoading = false;
        this.processQueue();
    }
    
    showLoadingIndicator(category) {
        const categoryElement = this.findCategoryElement(category);
        if (categoryElement) {
            const loadingSpan = document.createElement('span');
            loadingSpan.className = 'category-loading';
            loadingSpan.textContent = ' ⏳';
            categoryElement.appendChild(loadingSpan);
        }
    }
    
    hideLoadingIndicator(category) {
        const categoryElement = this.findCategoryElement(category);
        if (categoryElement) {
            const loading = categoryElement.querySelector('.category-loading');
            if (loading) loading.remove();
            
            // Add checkmark
            const checkmark = document.createElement('span');
            checkmark.className = 'category-loaded';
            checkmark.textContent = ' ✓';
            checkmark.style.color = '#00ff88';
            categoryElement.appendChild(checkmark);
            setTimeout(() => checkmark.remove(), 1500);
        }
    }
    
    findCategoryElement(categoryKey) {
        const categoryMap = {
            'digital': 'Digital Pins',
            'analog': 'Analog Pins',
            'time': 'Time',
            'serial': 'Serial Monitor',
            'math': 'Mathematics',
            'logic': 'Logic',
            'variables': 'Variables',
            'functions': 'Functions',
            'leds': 'LEDs and Outputs',
            'servo': 'Servo Motor',
            'sensors': 'Sensors'
        };
        
        const categoryName = categoryMap[categoryKey];
        if (!categoryName) return null;
        
        const categories = document.querySelectorAll('.blocklyTreeRow');
        for (let cat of categories) {
            const label = cat.querySelector('.blocklyTreeLabel');
            if (label && label.textContent === categoryName) {
                return cat;
            }
        }
        return null;
    }
    
    updateToolboxCategory(categoryKey) {
        // This would refresh the toolbox to show loaded blocks
        // For now, we just mark as loaded
        console.log(`Category ${categoryKey} loaded`);
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // Check if a block type is available
    isBlockAvailable(blockType) {
        for (const [cat, info] of Object.entries(this.categories)) {
            if (info.blocks.includes(blockType)) {
                return this.loadedCategories.has(cat);
            }
        }
        return true; // Assume core is always available
    }
    
    // Preload categories used in current workspace
    preloadUsedCategories(workspace) {
        const usedBlockTypes = new Set();
        workspace.getAllBlocks(true).forEach(block => {
            usedBlockTypes.add(block.type);
        });
        
        for (const [cat, info] of Object.entries(this.categories)) {
            const hasBlock = info.blocks.some(blockType => usedBlockTypes.has(blockType));
            if (hasBlock && !this.loadedCategories.has(cat)) {
                this.loadCategoryBlocks(cat);
            }
        }
    }
}

let lazyLoader = null;

function initLazyLoader(workspace) {
    lazyLoader = new LazyBlockLoader();
    // Preload categories from existing blocks
    setTimeout(() => lazyLoader.preloadUsedCategories(workspace), 100);
}

// Override workspace creation to include lazy loader
if (typeof originalWorkspaceCreate === 'undefined') {
    const originalCreate = Blockly.inject;
    Blockly.inject = function(container, config) {
        const workspace = originalCreate.call(this, container, config);
        initLazyLoader(workspace);
        return workspace;
    };
}