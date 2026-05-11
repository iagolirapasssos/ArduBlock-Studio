/**
 * Dynamic Toolbox Manager
 * Gerencia a toolbox dinamicamente sem recarregar a página
 */

class DynamicToolbox {
    constructor(workspace) {
        this.workspace = workspace;
        this.toolbox = document.getElementById('toolbox');
        this.categories = new Map();
        this.init();
    }
    
    init() {
        // Carrega categorias existentes        this.loadCategories();
        
        // Observa mudanças na toolbox
        this.observeToolbox();
    }
    
    loadCategories() {
        const categories = this.toolbox.querySelectorAll('category');
        categories.forEach(cat => {
            const name = cat.getAttribute('name');
            this.categories.set(name, cat);
        });
    }
    
    observeToolbox() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    // Atualiza o workspace se houver mudanças
                    if (this.workspace) {
                        this.workspace.updateToolbox(this.toolbox);
                    }
                }
            });
        });
        
        observer.observe(this.toolbox, {
            childList: true,
            subtree: true
        });
    }
    
    addCategory(name, colour, icon = '') {
        if (this.categories.has(name)) {
            return this.categories.get(name);
        }
        
        const category = document.createElement('category');
        category.setAttribute('name', name);
        category.setAttribute('colour', colour);
        if (icon) {
            category.setAttribute('icon', icon);
        }
        
        this.toolbox.appendChild(category);
        this.categories.set(name, category);
        
        if (this.workspace) {
            this.workspace.updateToolbox(this.toolbox);
        }
        
        return category;
    }
    
    addSubcategory(parentName, name, colour, icon = '') {
        const parent = this.categories.get(parentName);
        if (!parent) return null;
        
        // Verifica se já existe
        let existing = parent.querySelector(`category[name="${name}"]`);
        if (existing) return existing;
        
        const subcategory = document.createElement('category');
        subcategory.setAttribute('name', name);
        subcategory.setAttribute('colour', colour);
        if (icon) {
            subcategory.setAttribute('icon', icon);
        }
        
        parent.appendChild(subcategory);
        
        if (this.workspace) {
            this.workspace.updateToolbox(this.toolbox);
        }
        
        return subcategory;
    }
    
    addBlock(categoryName, blockType, subcategoryName = '') {
        let targetCategory = this.categories.get(categoryName);
        
        if (subcategoryName && targetCategory) {
            const subcat = targetCategory.querySelector(`category[name="${subcategoryName}"]`);
            if (subcat) targetCategory = subcat;
        }
        
        if (!targetCategory) return false;
        
        // Verifica se bloco já existe
        const existingBlock = targetCategory.querySelector(`block[type="${blockType}"]`);
        if (existingBlock) return false;
        
        const block = document.createElement('block');
        block.setAttribute('type', blockType);
        
        targetCategory.appendChild(block);
        
        if (this.workspace) {
            this.workspace.updateToolbox(this.toolbox);
        }
        
        return true;
    }
    
    addSeparator(categoryName) {
        const category = this.categories.get(categoryName);
        if (!category) return false;
        
        const sep = document.createElement('sep');
        category.appendChild(sep);
        
        if (this.workspace) {
            this.workspace.updateToolbox(this.toolbox);
        }
        
        return true;
    }
    
    removeCategory(name) {
        const category = this.categories.get(name);
        if (category) {
            category.remove();
            this.categories.delete(name);
            
            if (this.workspace) {
                this.workspace.updateToolbox(this.toolbox);
            }
            return true;
        }
        return false;
    }
    
    reorderCategories(orderList) {
        orderList.forEach(catName => {
            const category = this.categories.get(catName);
            if (category) {
                this.toolbox.appendChild(category);
            }
        });
        
        if (this.workspace) {
            this.workspace.updateToolbox(this.toolbox);
        }
    }
}

// Inicializa o gerenciador quando o workspace estiver pronto
let dynamicToolbox = null;

function initDynamicToolbox(workspace) {
    dynamicToolbox = new DynamicToolbox(workspace);
    window.dynamicToolbox = dynamicToolbox;
}