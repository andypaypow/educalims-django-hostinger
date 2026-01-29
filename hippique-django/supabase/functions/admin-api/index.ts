// ===== ADMIN API - SUPABASE EDGE FUNCTION =====
// API pour l'administration FiltreExpert

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get('SUPABASE_URL') || 'https://qfkyzljqykymahlpmdnu.supabase.co';
const SUPABASE_SERVICE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || '';
const ADMIN_PASSWORD = Deno.env.get('ADMIN_PASSWORD') || 'admin';

// ===== TYPES =====
interface Subscription {
  id: string;
  device_id: string;
  payment_status: string;
  transaction_id: string;
  phone_number: string;
  amount: number;
  payment_date: string;
  expiry_date: string;
  created_at: string;
}

interface Stats {
  total_subscriptions: number;
  active_subscriptions: number;
  total_revenue: number;
  today_revenue: number;
  today_subscriptions: number;
}

// ===== VÉRIFICATION AUTH =====
function verifyAuth(req: Request): boolean {
  const authHeader = req.headers.get('Authorization');
  if (!authHeader) return false;

  const base64Credentials = authHeader.split(' ')[1];
  const credentials = atob(base64Credentials);
  const [, password] = credentials.split(':');

  return password === ADMIN_PASSWORD;
}

// ===== EDGE FUNCTION HANDLER =====

serve(async (req) => {
  // CORS
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
      }
    });
  }

  const url = new URL(req.url);
  const path = url.pathname;

  console.log(`📊 Admin API: ${req.method} ${path}`);

  try {
    // Vérifier l'authentification
    if (!verifyAuth(req)) {
      return new Response(JSON.stringify({
        error: 'Unauthorized',
        message: 'Mot de passe incorrect'
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        status: 401
      });
    }

    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

    // GET /stats - Statistiques
    if (req.method === 'GET' && path === '/stats') {
      const { data: subscriptions, error } = await supabase
        .from('subscriptions')
        .select('*');

      if (error) throw error;

      const now = new Date();
      const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).toISOString();

      const stats: Stats = {
        total_subscriptions: subscriptions.length,
        active_subscriptions: subscriptions.filter((s: Subscription) =>
          s.payment_status === 'active' && new Date(s.expiry_date) > now
        ).length,
        total_revenue: subscriptions.reduce((sum: number, s: Subscription) => sum + (s.amount || 0), 0),
        today_revenue: subscriptions
          .filter((s: Subscription) => s.payment_date >= todayStart)
          .reduce((sum: number, s: Subscription) => sum + (s.amount || 0), 0),
        today_subscriptions: subscriptions.filter((s: Subscription) => s.payment_date >= todayStart).length
      };

      return new Response(JSON.stringify(stats), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        status: 200
      });
    }

    // GET /subscriptions - Liste des abonnements
    if (req.method === 'GET' && path === '/subscriptions') {
      const limit = parseInt(url.searchParams.get('limit') || '50');
      const offset = parseInt(url.searchParams.get('offset') || '0');

      const { data, error } = await supabase
        .from('subscriptions')
        .select('*')
        .order('created_at', { ascending: false })
        .range(offset, offset + limit - 1);

      if (error) throw error;

      return new Response(JSON.stringify({
        subscriptions: data,
        count: data.length
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        status: 200
      });
    }

    // GET /subscriptions/:id - Détails d'un abonnement
    if (req.method === 'GET' && path.startsWith('/subscriptions/')) {
      const id = path.split('/')[2];
      const { data, error } = await supabase
        .from('subscriptions')
        .select('*')
        .eq('id', id)
        .single();

      if (error) throw error;

      return new Response(JSON.stringify(data), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        status: 200
      });
    }

    // PATCH /config - Modifier la configuration
    if (req.method === 'PATCH' && path === '/config') {
      const body = await req.json();
      const { payment_link } = body;

      if (!payment_link) {
        return new Response(JSON.stringify({
          error: 'Missing required field: payment_link'
        }), {
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          },
          status: 400
        });
      }

      // Stocker en environment variable (simulé ici)
      // En production, utiliser Supabase Secrets ou une table config

      return new Response(JSON.stringify({
        success: true,
        message: 'Configuration mise à jour',
        payment_link
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        status: 200
      });
    }

    // GET /config - Récupérer la configuration
    if (req.method === 'GET' && path === '/config') {
      const config = {
        payment_link: Deno.env.get('PAYMENT_LINK') ||
          'https://sumb.cyberschool.ga/?productId=KzIfBGUYU6glnH3JlsbZ&operationAccountCode=ACC_6835C458B85FF&maison=moov&amount=100',
        telegram_bot: '@Filtrexpert_bot',
        telegram_chat_id: '1646298746'
      };

      return new Response(JSON.stringify(config), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        status: 200
      });
    }

    // DELETE /subscriptions/:id - Supprimer un abonnement
    if (req.method === 'DELETE' && path.startsWith('/subscriptions/')) {
      const id = path.split('/')[2];

      const { error } = await supabase
        .from('subscriptions')
        .delete()
        .eq('id', id);

      if (error) throw error;

      return new Response(JSON.stringify({
        success: true,
        message: 'Abonnement supprimé'
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        status: 200
      });
    }

    return new Response(JSON.stringify({
      error: 'Not Found',
      message: 'Endpoint non trouvé'
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      status: 404
    });

  } catch (error: any) {
    console.error('❌ Erreur Admin API:', error);

    return new Response(JSON.stringify({
      error: 'Internal Server Error',
      message: error.message || 'Erreur lors du traitement'
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      status: 500
    });
  }
});
