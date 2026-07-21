// Interactive qualifier adjustment system
let qualifierState = {}; // Track current state by event

function initializeQualifierState(eventData) {
    """Initialize state tracking for interactive adjustments"""
    qualifierState = {};
    for (let eventNum in eventData) {
        qualifierState[eventNum] = {
            autoQualifiers: new Set(),
            wildcards: new Set(),
            outList: new Set()
        };
        
        // Populate initial state from eventData
        eventData[eventNum].auto_qual.forEach(entry => {
            qualifierState[eventNum].autoQualifiers.add(entry.id);
        });
        eventData[eventNum].wildcard_pool.forEach(entry => {
            qualifierState[eventNum].wildcards.add(entry.id);
        });
    }
}

function attachQualifierClickHandlers() {
    """Attach click handlers to swimmer rows for interactive adjustment"""
    document.querySelectorAll('.swimmer-row').forEach(row => {
        row.addEventListener('click', handleSwimmerClick);
    });
}

function handleSwimmerClick(event) {
    const row = event.currentTarget;
    const eventNum = parseInt(row.dataset.eventNum);
    const swimmerId = row.dataset.swimmerId;
    const currentStatus = row.dataset.status;
    
    if (currentStatus === 'auto-qual') {
        // Scratch this auto-qualifier
        row.classList.remove('auto-qual');
        row.classList.add('out');
        row.dataset.status = 'out';
        
        // Update badge
        const badge = row.querySelector('.qual-badge');
        badge.classList.remove('badge-auto');
        badge.classList.add('badge-out');
        badge.innerText = 'OUT';
        
        qualifierState[eventNum].autoQualifiers.delete(swimmerId);
        qualifierState[eventNum].outList.add(swimmerId);
        
        // Try to promote the next swimmer from OUT or wildcards
        promoteNextSwimmer(eventNum, row);
    }
}

function promoteNextSwimmer(eventNum, clickedRow) {
    """Promote the next available swimmer to replace scratched auto-qualifier"""
    const allRows = document.querySelectorAll(`[data-event-num="${eventNum}"]`);
    
    // Find first OUT swimmer and promote them to wildcard
    for (let row of allRows) {
        if (row.dataset.status === 'out') {
            row.classList.remove('out');
            row.classList.add('wildcard');
            row.dataset.status = 'wildcard';
            
            const badge = row.querySelector('.qual-badge');
            badge.classList.remove('badge-out');
            badge.classList.add('badge-wildcard');
            badge.innerText = 'WILDCARD';
            
            const swimmerId = row.dataset.swimmerId;
            qualifierState[eventNum].outList.delete(swimmerId);
            qualifierState[eventNum].wildcards.add(swimmerId);
            break;
        }
    }
}

function getCurrentQualifierState() {
    """Return the current state of qualifiers for export"""
    return qualifierState;
}
