// ===== ADMIN - FILTREEXPERT =====
// Configuration API
const API_BASE = 'https://qfkyzljqykymahlpmdnu.supabase.co/functions/v1/admin-api';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFma3l6bGpxeWt5bWFobHBtZG51Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk2Mjc1NzIsImV4cCI6MjA4NTIwMzU3Mn0.g_Rmxo8lY8KAnrQqyzcz0PLh03T1M7_RuBUQT6ObtXg';

// État de l'application
let authPassword = null;

// ===== AUTHENTIFICATION =====

function getAuthHeaders() {
    const credentials = btoa(`admin:${authPassword}`);
    return {
        'Content-Type': 'application/json',
        'Authorization': `Basic ${credentials}`,
        'apikey': SUPABASE_ANON_KEY
    };
}

async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const response = await fetch(url, {
        ...options,
        headers: {
            ...getAuthHeaders(),
            ...options.headers
        }
    });

    if (response.status === 401) {
        logout();
        throw new Error('Non autorisé');
    }

    return response.json();
}

// ===== LOGIN =====

const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const loginSection = document.getElementById('login-section');
const adminDashboard = document.getElementById('admin-dashboard');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const password = document.getElementById('password').value;

    // Stocker le mot de passe
    authPassword = password;

    try {
        // Tenter de récupérer les stats pour vérifier l'auth
        const stats = await apiCall('/stats');
        showDashboard();
        loadStats();
        loadConfig();
        loadSubscriptions();
    } catch (error) {
        loginError.textContent = 'Mot de passe incorrect';
        authPassword = null;
    }
});

function showDashboard() {
    loginSection.style.display = 'none';
    adminDashboard.style.display = 'block';
}

function logout() {
    authPassword = null;
    sessionStorage.removeItem('admin_password');
    adminDashboard.style.display = 'none';
    loginSection.style.display = 'block';
    document.getElementById('password').value = '';
}

document.getElementById('logout-btn').addEventListener('click', logout);

// ===== STATS =====

async function loadStats() {
    try {
        const stats = await apiCall('/stats');

        document.getElementById('stat-total').textContent = stats.total_subscriptions;
        document.getElementById('stat-active').textContent = stats.active_subscriptions;
        document.getElementById('stat-revenue').textContent = formatCurrency(stats.total_revenue);
        document.getElementById('stat-today').textContent = formatCurrency(stats.today_revenue);
    } catch (error) {
        console.error('Erreur chargement stats:', error);
    }
}

function formatCurrency(amount) {
    return amount.toLocaleString('fr-FR') + ' F';
}

// ===== CONFIGURATION =====

async function loadConfig() {
    try {
        const config = await apiCall('/config');

        document.getElementById('payment-link').value = config.payment_link || '';
        document.getElementById('telegram-bot').value = config.telegram_bot || '';
    } catch (error) {
        console.error('Erreur chargement config:', error);
    }
}

document.getElementById('save-config-btn').addEventListener('click', async () => {
    const paymentLink = document.getElementById('payment-link').value;

    if (!paymentLink) {
        alert('Veuillez entrer un lien de paiement valide');
        return;
    }

    try {
        await apiCall('/config', {
            method: 'PATCH',
            body: JSON.stringify({ payment_link: paymentLink })
        });

        alert('✅ Configuration enregistrée avec succès !');
    } catch (error) {
        console.error('Erreur sauvegarde config:', error);
        alert('❌ Erreur lors de la sauvegarde: ' + error.message);
    }
});

// ===== SUBSCRIPTIONS =====

async function loadSubscriptions() {
    const listDiv = document.getElementById('subscriptions-list');

    try {
        listDiv.innerHTML = '<div class="loading">Chargement...</div>';

        const data = await apiCall('/subscriptions?limit=20');

        if (!data.subscriptions || data.subscriptions.length === 0) {
            listDiv.innerHTML = '<div class="empty">Aucun abonnement trouvé</div>';
            return;
        }

        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Device ID</th>
                        <th>Téléphone</th>
                        <th>Montant</th>
                        <th>Statut</th>
                        <th>Expiration</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.subscriptions.forEach(sub => {
            const date = new Date(sub.created_at).toLocaleString('fr-FR');
            const expiry = new Date(sub.expiry_date).toLocaleString('fr-FR');
            const statusClass = sub.payment_status === 'active' ? 'active' : 'expired';
            const deviceIdShort = sub.device_id.substring(0, 12) + '...';

            html += `
                <tr>
                    <td>${date}</td>
                    <td title="${sub.device_id}">${deviceIdShort}</td>
                    <td>${sub.phone_number || '-'}</td>
                    <td>${sub.amount} F</td>
                    <td><span class="status ${statusClass}">${sub.payment_status}</span></td>
                    <td>${expiry}</td>
                    <td>
                        <div class="actions">
                            <button class="btn-small btn-view" onclick="viewSubscription('${sub.id}')">Voir</button>
                            <button class="btn-small btn-delete" onclick="deleteSubscription('${sub.id}')">Supprimer</button>
                        </div>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        listDiv.innerHTML = html;
    } catch (error) {
        console.error('Erreur chargement abonnements:', error);
        listDiv.innerHTML = '<div class="error">Erreur lors du chargement des abonnements</div>';
    }
}

async function viewSubscription(id) {
    try {
        const sub = await apiCall(`/subscriptions/${id}`);

        const details = `
ID: ${sub.id}
Device ID: ${sub.device_id}
Transaction ID: ${sub.transaction_id}
Téléphone: ${sub.phone_number || 'N/A'}
Montant: ${sub.amount} F
Statut: ${sub.payment_status}
Date de paiement: ${new Date(sub.payment_date).toLocaleString('fr-FR')}
Expiration: ${new Date(sub.expiry_date).toLocaleString('fr-FR')}
Créé le: ${new Date(sub.created_at).toLocaleString('fr-FR')}
        `;

        alert(details);
    } catch (error) {
        alert('Erreur lors du chargement des détails: ' + error.message);
    }
}

async function deleteSubscription(id) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet abonnement ?')) {
        return;
    }

    try {
        await apiCall(`/subscriptions/${id}`, {
            method: 'DELETE'
        });

        alert('✅ Abonnement supprimé');
        loadSubscriptions();
        loadStats();
    } catch (error) {
        alert('❌ Erreur lors de la suppression: ' + error.message);
    }
}

// ===== AUTO-REFRESH =====

// Rafraîchir les stats toutes les 60 secondes
setInterval(() => {
    if (authPassword) {
        loadStats();
    }
}, 60000);

// ===== SESSION =====

// Vérifier s'il y a une session existante
const storedPassword = sessionStorage.getItem('admin_password');
if (storedPassword) {
    authPassword = storedPassword;
    showDashboard();
    loadStats();
    loadConfig();
    loadSubscriptions();
}
