async function filterStats() {
    const periode = document.getElementById('filterPeriode').value;
    const debut = document.getElementById('filterDateDebut').value;
    const fin = document.getElementById('filterDateFin').value;
    const params = new URLSearchParams({periode: periode, date_debut: debut, date_fin: fin});
    try {
        document.getElementById('statsTable').innerHTML = '<p style=\"color:#00C6FF;text-align:center;\">Chargement...</p>';
        const r = await fetch('/api/admin/stats/filter/?' + params, { credentials: 'same-origin' });
        const res = await r.json();
        if (res.success) {
            let html = '<table style=\"width:100%; border-collapse:collapse;\"><thead>';
            if (periode === 'jour') {
                html += '<tr style=\"border-bottom:1px solid #333;\"><th style=\"padding:10px;text-align:left;color:#888;\">Date</th><th style=\"padding:10px;text-align:right;color:#888;\">Appareils</th><th style=\"padding:10px;text-align:right;color:#888;\">Visites</th><th style=\"padding:10px;text-align:center;color:#888;\">Details</th></tr></thead><tbody>';
                res.stats.forEach((s, idx) => {
                    html += '<tr style=\"border-bottom:1px solid #2a2a2a;\"><td style=\"padding:8px;\">' + s.date + '</td><td style=\"padding:8px;text-align:right;color:#00C6FF;\">' + s.appareils_uniques + '</td><td style=\"padding:8px;text-align:right;color:#00FF7F;\">' + s.visites + '</td><td style=\"padding:8px;text-align:center;\"><button onclick=\"showDetails(' + idx + ', \'jour\')\" style=\"background:#333;color:#fff;border:none;padding:5px 10px;border-radius:3px;cursor:pointer;font-size:0.8rem;\">Voir</button></td></tr>';
                    html += '<tr id=\"details-' + idx + '\" style=\"display:none;background:#151515;\"><td colspan=\"4\" style=\"padding:15px;\"><div id=\"details-content-' + idx + '\" style=\"font-size:0.85rem;color:#ccc;\"></div></td></tr>';
                });
            } else if (periode === 'semaine') {
                html += '<tr style=\"border-bottom:1px solid #333;\"><th style=\"padding:10px;text-align:left;color:#888;\">Semaine</th><th style=\"padding:10px;text-align:left;color:#888;\">Du</th><th style=\"padding:10px;text-align:left;color:#888;\">Au</th><th style=\"padding:10px;text-align:right;color:#888;\">Appareils</th><th style=\"padding:10px;text-align:right;color:#888;\">Visites</th><th style=\"padding:10px;text-align:center;color:#888;\">Details</th></tr></thead><tbody>';
                res.stats.forEach((s, idx) => {
                    html += '<tr style=\"border-bottom:1px solid #2a2a2a;\"><td style=\"padding:8px;\">' + s.semaine + '</td><td style=\"padding:8px;\">' + s.du + '</td><td style=\"padding:8px;\">' + s.au + '</td><td style=\"padding:8px;text-align:right;color:#00C6FF;\">' + s.appareils_uniques + '</td><td style=\"padding:8px;text-align:right;color:#00FF7F;\">' + s.visites + '</td><td style=\"padding:8px;text-align:center;\"><button onclick=\"showDetails(' + idx + ', \'semaine\')\" style=\"background:#333;color:#fff;border:none;padding:5px 10px;border-radius:3px;cursor:pointer;font-size:0.8rem;\">Voir</button></td></tr>';
                    html += '<tr id=\"details-' + idx + '\" style=\"display:none;background:#151515;\"><td colspan=\"6\" style=\"padding:15px;\"><div id=\"details-content-' + idx + '\" style=\"font-size:0.85rem;color:#ccc;\"></div></td></tr>';
                });
            } else if (periode === 'mois') {
                html += '<tr style=\"border-bottom:1px solid #333;\"><th style=\"padding:10px;text-align:left;color:#888;\">Mois</th><th style=\"padding:10px;text-align:left;color:#888;\">Annee</th><th style=\"padding:10px;text-align:right;color:#888;\">Appareils</th><th style=\"padding:10px;text-align:right;color:#888;\">Visites</th><th style=\"padding:10px;text-align:center;color:#888;\">Details</th></tr></thead><tbody>';
                res.stats.forEach((s, idx) => {
                    html += '<tr style=\"border-bottom:1px solid #2a2a2a;\"><td style=\"padding:8px;\">' + s.mois + '</td><td style=\"padding:8px;\">' + s.annee + '</td><td style=\"padding:8px;text-align:right;color:#00C6FF;\">' + s.appareils_uniques + '</td><td style=\"padding:8px;text-align:right;color:#00FF7F;\">' + s.visites + '</td><td style=\"padding:8px;text-align:center;\"><button onclick=\"showDetails(' + idx + ', \'mois\')\" style=\"background:#333;color:#fff;border:none;padding:5px 10px;border-radius:3px;cursor:pointer;font-size:0.8rem;\">Voir</button></td></tr>';
                    html += '<tr id=\"details-' + idx + '\" style=\"display:none;background:#151515;\"><td colspan=\"5\" style=\"padding:15px;\"><div id=\"details-content-' + idx + '\" style=\"font-size:0.85rem;color:#ccc;\"></div></td></tr>';
                });
            }
            html += '</tbody></table>';
            document.getElementById('statsTable').innerHTML = html;
            window.currentStats = res.stats;
        } else {
            document.getElementById('statsTable').innerHTML = '<p style=\"color:#ff4448;\">Erreur: ' + (res.error || 'Erreur inconnue') + '</p>';
        }
    } catch(e) {
        console.error(e);
        document.getElementById('statsTable').innerHTML = '<p style=\"color:#ff4448;\">Erreur lors du chargement</p>';
    }
}
async function showDetails(idx, periode) {
    const row = document.getElementById('details-' + idx);
    const content = document.getElementById('details-content-' + idx);
    if (row.style.display === 'none') {
        row.style.display = 'table-row';
        content.innerHTML = '<p style=\"color:#00C6FF;\">Chargement des details...</p>';
        try {
            const s = window.currentStats[idx];
            const params = new URLSearchParams({ periode: periode, idx: idx });
            if (periode === 'jour') {
                params.append('date', s.date_raw);
            } else if (periode === 'semaine') {
                params.append('debut', s.debut_raw);
                params.append('fin', s.fin_raw);
            } else if (periode === 'mois') {
                params.append('mois', s.mois_raw);
                params.append('annee', s.annee);
            }
            const r = await fetch('/api/admin/stats/details/?' + params, { credentials: 'same-origin' });
            const res = await r.json();
            if (res.success) {
                let html = '<h4 style=\"color:#00C6FF;margin-bottom:10px;\">Appareils (' + res.details.length + ')</h4>';
                html += '<table style=\"width:100%;border-collapse:collapse;font-size:0.8rem;\">';
                html += '<thead><tr style=\"border-bottom:1px solid #333;\"><th style=\"padding:5px;text-align:left;\">IP</th><th style=\"padding:5px;text-align:left;\">User-Agent</th><th style=\"padding:5px;text-align:right;\">Visites</th><th style=\"padding:5px;text-align:right;\">Pages</th></tr></thead><tbody>';
                res.details.forEach(d => {
                    html += '<tr style=\"border-bottom:1px solid #2a2a2a;\">';
                    html += '<td style=\"padding:5px;color:#888;\">' + d.ip_address + '</td>';
                    html += '<td style=\"padding:5px;\"><div style=\"max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;\" title=\"' + escapeHtml(d.user_agent || 'N/A') + '\">' + escapeHtml(d.user_agent || 'N/A').substring(0, 50) + '...</div></td>';
                    html += '<td style=\"padding:5px;text-align:right;color:#00FF7F;\">' + d.nombre_visites + '</td>';
                    html += '<td style=\"padding:5px;text-align:right;color:#00C6FF;\">' + d.nombre_pages_vues + '</td>';
                    html += '</tr>';
                });
                html += '</tbody></table>';
                content.innerHTML = html;
            } else {
                content.innerHTML = '<p style=\"color:#ff4448;\">Erreur: ' + (res.error || 'Erreur') + '</p>';
            }
        } catch(e) {
            console.error(e);
            content.innerHTML = '<p style=\"color:#ff4448;\">Erreur de chargement</p>';
        }
    } else {
        row.style.display = 'none';
    }
}
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
