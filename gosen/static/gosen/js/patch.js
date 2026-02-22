(function() {
    // Override displayResults to use PROD style with combination-item spans
    window.displayResults = function(filtered, total) {
        currentFilteredCombinations = filtered.map(c => c.sort((a, b) => a - b));
        const filteredCount = filtered.length;
        const rate = total > 0 ? ((total - filteredCount) / total * 100).toFixed(2) : 0;
        
        // Use PROD style summary
        resultsSummaryDiv.innerHTML = '<strong>' + filteredCount.toLocaleString('fr-FR') + '</strong> combinaisons conservées sur <strong>' + total.toLocaleString('fr-FR') + '</strong> | Taux de filtrage : <strong>' + rate + '%</strong>';
        
        // Use PROD style: combination-item spans in a scrollable container
        resultsOutputDiv.innerHTML = filtered.map(combi => '<span class="combination-item">' + combi.join(' - ') + '</span>').join('');

        const fc = document.getElementById('floating-counter');
        if (fc) fc.textContent = filteredCount + '/' + total;
    };
    console.log('PROD style results patch loaded');
})();
