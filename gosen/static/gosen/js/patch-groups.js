// Patch for compact parsed groups display - loaded AFTER main.js
(function() {
    // Override the function that renders parsed groups
    const originalParse = window.handlePronosticsTextareaChange;
    
    // We'll override the entire function for compact display
    window.handlePronosticsTextareaChange = function() {
        const textarea = document.getElementById('pronostics');
        const parsedGroupsDiv = document.getElementById('parsed-groups');
        const rawText = textarea.value.trim();
        
        if (!rawText) {
            currentRawGroups = [];
            parsedGroupsDiv.innerHTML = '';
            updatePronosticsSyntheses([]);
            return;
        }
        
        const lines = rawText.split('
').filter(line => line.trim());
        const rawGroups = [];
        
        lines.forEach((line, index) => {
            const match = line.match(/^([^:]+):\s*(.+)$/);
            if (match) {
                const name = match[1].trim();
                const horsesStr = match[2].trim();
                const horses = parseHorsesRange(horsesStr);
                rawGroups.push({ name, horses, id: index });
            } else {
                const horses = parseHorsesRange(line);
                if (horses.length > 0) {
                    rawGroups.push({ name: `Groupe ${index + 1}`, horses, id: index });
                }
            }
        });
        
        currentRawGroups = rawGroups;
        
        // Render with COMPACT layout - everything on one line
        parsedGroupsDiv.innerHTML = rawGroups.map((group, index) => `
            <div class="group" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:8px 12px;background:var(--bg-card);border:1px solid var(--border-color);border-radius:8px;margin-bottom:8px;">
                <span class="group-title" style="color:var(--gabon-green);font-weight:600;">${group.name}:</span>
                <span style="color:var(--text-primary);font-family:monospace;">[${group.horses.join(', ')}]</span>
                <span class="group-filter-inline" style="display:flex;align-items:center;gap:5px;margin-left:auto;font-size:0.85rem;color:var(--text-secondary);">
                    <span>Min:</span>
                    <input type="number" class="group-min" value="0" min="0" max="${group.horses.length}" 
                           style="width:50px;padding:4px 8px;border:1px solid var(--border-color);border-radius:4px;background:var(--bg-input);color:var(--text-primary);text-align:center;"
                           data-group-id="${index}">
                    <span style="color:var(--border-color);">|</span>
                    <span>Max:</span>
                    <input type="number" class="group-max" value="${group.horses.length}" min="0" max="${group.horses.length}" 
                           style="width:50px;padding:4px 8px;border:1px solid var(--border-color);border-radius:4px;background:var(--bg-input);color:var(--text-primary);text-align:center;"
                           data-group-id="${index}">
                </span>
            </div>`).join('');
        
        // Attach event listeners to min/max inputs
        parsedGroupsDiv.querySelectorAll('.group-min, .group-max').forEach(input => {
            input.addEventListener('change', function() {
                const groupId = parseInt(this.dataset.groupId);
                const group = currentRawGroups[groupId];
                if (!group) return;
                
                const minInput = parsedGroupsDiv.querySelectorAll(`.group-min[data-group-id="${groupId}"]`)[0];
                const maxInput = parsedGroupsDiv.querySelectorAll(`.group-max[data-group-id="${groupId}"]`)[0];
                
                let minVal = parseInt(minInput.value) || 0;
                let maxVal = parseInt(maxInput.value) || group.horses.length;
                
                if (minVal < 0) minVal = 0;
                if (maxVal > group.horses.length) maxVal = group.horses.length;
                if (minVal > maxVal) minVal = maxVal;
                
                minInput.value = minVal;
                maxInput.value = maxVal;
            });
        });
        
        updatePronosticsSyntheses(rawGroups);
        updateTotalCombinations();
        checkParsedGroupsComplete();
    };
    
    console.log('Compact parsed groups patch loaded');
})();
