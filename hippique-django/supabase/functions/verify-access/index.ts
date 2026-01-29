// ===== VERIFY ACCESS - SUPABASE EDGE FUNCTION =====
// Vérifie si un device a un abonnement actif

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// ===== CONFIGURATION =====
const SUPABASE_URL = Deno.env.get('SUPABASE_URL') || 'https://qfkyzljqykymahlpmdnu.supabase.co';
const SUPABASE_ANON_KEY = Deno.env.get('SUPABASE_ANON_KEY') || '';
const PAYMENT_LINK = Deno.env.get('PAYMENT_LINK') ||
  'https://sumb.cyberschool.ga/?productId=KzIfBGUYU6glnH3JlsbZ&operationAccountCode=ACC_6835C458B85FF&maison=moov&amount=100';

// ===== TYPES =====
interface VerifyRequest {
  device_id: string;
  jwt_token?: string;
}

interface VerifyResponse {
  has_access: boolean;
  subscription_status: string | null;
  expiry_date: string | null;
  message: string;
  payment_link?: string;
}

// ===== EDGE FUNCTION HANDLER =====

serve(async (req) => {
  // Gérer les requêtes OPTIONS (CORS)
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
      }
    });
  }

  // Gérer uniquement les requêtes POST
  if (req.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
  }

  try {
    const requestData: VerifyRequest = await req.json();

    const { device_id, jwt_token } = requestData;

    // Vérifier que device_id est fourni
    if (!device_id) {
      const response: VerifyResponse = {
        has_access: false,
        subscription_status: null,
        expiry_date: null,
        message: 'Device ID requis',
        payment_link: PAYMENT_LINK
      };
      return new Response(JSON.stringify(response), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        status: 400
      });
    }

    console.log(`🔍 Vérification accès pour device_id: ${device_id.substring(0, 8)}...`);

    // Créer le client Supabase
    const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

    // Rechercher l'abonnement actif
    const now = new Date().toISOString();
    const { data: subscription, error } = await supabase
      .from('subscriptions')
      .select('*')
      .eq('device_id', device_id)
      .gte('expiry_date', now) // expiry_date >= maintenant
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle();

    if (error) {
      console.error('❌ Erreur vérification abonnement:', error);
    }

    // Pas d'abonnement trouvé
    if (!subscription) {
      const response: VerifyResponse = {
        has_access: false,
        subscription_status: 'none',
        expiry_date: null,
        message: 'Aucun abonnement actif trouvé. Veuillez effectuer un paiement.',
        payment_link: PAYMENT_LINK
      };
      console.log('❌ Aucun abonnement actif');
      return new Response(JSON.stringify(response), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        status: 403
      });
    }

    // Vérifier le statut de paiement
    if (subscription.payment_status !== 'active') {
      const response: VerifyResponse = {
        has_access: false,
        subscription_status: subscription.payment_status,
        expiry_date: subscription.expiry_date,
        message: `Abonnement ${subscription.payment_status}. Veuillez effectuer un paiement.`,
        payment_link: PAYMENT_LINK
      };
      console.log(`❌ Abonnement non actif: ${subscription.payment_status}`);
      return new Response(JSON.stringify(response), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        status: 403
      });
    }

    // Vérifier si JWT correspond (si fourni)
    if (jwt_token && subscription.jwt_token !== jwt_token) {
      const response: VerifyResponse = {
        has_access: false,
        subscription_status: 'invalid_token',
        expiry_date: subscription.expiry_date,
        message: 'Token invalide. Veuillez vous reconnecter.',
        payment_link: PAYMENT_LINK
      };
      console.log('❌ Token JWT invalide');
      return new Response(JSON.stringify(response), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        status: 403
      });
    }

    // Abonnement actif valide
    const expiryDate = new Date(subscription.expiry_date);
    const response: VerifyResponse = {
      has_access: true,
      subscription_status: subscription.payment_status,
      expiry_date: subscription.expiry_date,
      message: `Accès autorisé. Expire le ${expiryDate.toLocaleString('fr-FR')}`
    };
    console.log(`✅ Accès autorisé, expire le ${expiryDate.toLocaleString('fr-FR')}`);

    return new Response(JSON.stringify(response), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      status: 200
    });

  } catch (error) {
    console.error('❌ Erreur vérification accès:', error);

    const response: VerifyResponse = {
      has_access: false,
      subscription_status: 'error',
      expiry_date: null,
      message: 'Erreur lors de la vérification de l\'abonnement',
      payment_link: PAYMENT_LINK
    };

    return new Response(JSON.stringify(response), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      status: 500
    });
  }
});
