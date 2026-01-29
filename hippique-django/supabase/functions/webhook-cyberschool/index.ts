// ===== WEBHOOK CYBERSCHOOL - SUPABASE EDGE FUNCTION =====
// Reçoit les notifications de paiement Cyberschool et crée les abonnements

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// ===== CONFIGURATION =====
const SUPABASE_URL = Deno.env.get('SUPABASE_URL') || 'https://qfkyzljqykymahlpmdnu.supabase.co';
const SUPABASE_SERVICE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || '';
const TELEGRAM_BOT_TOKEN = Deno.env.get('TELEGRAM_BOT_TOKEN') || '8547430409:AAGx2LxGxP6fBd9mn13LSmRbU4y3wlopIq4';
const TELEGRAM_CHAT_ID = Deno.env.get('TELEGRAM_CHAT_ID') || '1646298746';
const JWT_SECRET = Deno.env.get('JWT_SECRET') || 'filtreexpert-jwt-secret-2026';

// ===== TYPES =====
interface CyberschoolWebhook {
  status: string;
  transaction_id?: string;
  phone_number?: string;
  amount?: string;
  custom_data?: string;
  device_id?: string;
  [key: string]: any;
}

interface Subscription {
  id: string;
  device_id: string;
  jwt_token: string;
  payment_status: string;
  transaction_id: string;
  phone_number: string;
  amount: number;
  payment_date: string;
  expiry_date: string;
  fingerprint_data: any;
}

// ===== FONCTIONS UTILITAIRES =====

function generateJWT(deviceId: string): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify({
    device_id: deviceId,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 heures
  }));
  const signature = btoa(`${header}.${payload}.${JWT_SECRET}`);
  return `${header}.${payload}.${signature}`;
}

function calculateExpiryDate(): string {
  const now = new Date();
  // Expirer à 23h59 le jour du paiement
  const expiry = new Date(now);
  expiry.setHours(23, 59, 59, 999);
  return expiry.toISOString();
}

async function sendTelegramNotification(subscription: Subscription): Promise<void> {
  if (!TELEGRAM_CHAT_ID) {
    console.warn('⚠️ TELEGRAM_CHAT_ID non défini, notification non envoyée');
    return;
  }

  const message = `
🎉 NOUVEL ABONNEMENT FILTREEXPERT

💰 Montant: ${subscription.amount} F
📱 Tel: ${subscription.phone_number || 'N/A'}
🔐 Device ID: ${subscription.device_id.substring(0, 8)}...
⏰ Expire: ${new Date(subscription.expiry_date).toLocaleString('fr-FR')}

Transaction ID: ${subscription.transaction_id}
  `.trim();

  try {
    const response = await fetch(
      `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: TELEGRAM_CHAT_ID,
          text: message,
          parse_mode: 'HTML'
        })
      }
    );

    if (response.ok) {
      console.log('✅ Notification Telegram envoyée');
    } else {
      const error = await response.text();
      console.error(`❌ Erreur Telegram: ${error}`);
    }
  } catch (error) {
    console.error(`❌ Erreur envoi Telegram: ${error.message}`);
  }
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
    const webhookData: CyberschoolWebhook = await req.json();

    console.log('📊 Webhook reçu:', JSON.stringify(webhookData, null, 2));

    // Vérifier le statut de paiement (code "200" = succès)
    if (webhookData.status !== '200') {
      console.log(`⚠️ Paiement non valide (status: ${webhookData.status})`);
      return new Response(JSON.stringify({
        success: false,
        message: 'Paiement non validé'
      }), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        status: 400
      });
    }

    // Récupérer ou générer le device_id
    const deviceId = webhookData.device_id ||
                     webhookData.custom_data ||
                     `manual-${Date.now()}-${Math.random().toString(36).substring(7)}`;

    // Générer le JWT
    const jwtToken = generateJWT(deviceId);

    // Calculer la date d'expiration (23h59 le jour du paiement)
    const expiryDate = calculateExpiryDate();

    // Créer le client Supabase
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

    // Vérifier si un abonnement existe déjà pour ce device
    const { data: existingSub, error: checkError } = await supabase
      .from('subscriptions')
      .select('*')
      .eq('device_id', deviceId)
      .single();

    if (checkError && checkError.code !== 'PGRST116') {
      // PGRST116 = no rows returned, c'est normal
      console.error('❌ Erreur vérification abonnement:', checkError);
    }

    if (existingSub) {
      // Mettre à jour l'abonnement existant
      const { data: updatedSub, error: updateError } = await supabase
        .from('subscriptions')
        .update({
          payment_status: 'active',
          transaction_id: webhookData.transaction_id || existingSub.transaction_id,
          phone_number: webhookData.phone_number || existingSub.phone_number,
          amount: parseFloat(webhookData.amount || '100'),
          payment_date: new Date().toISOString(),
          expiry_date: expiryDate,
          jwt_token: jwtToken
        })
        .eq('device_id', deviceId)
        .select()
        .single();

      if (updateError) {
        console.error('❌ Erreur mise à jour abonnement:', updateError);
        throw updateError;
      }

      console.log('✅ Abonnement mis à jour:', updatedSub.id);

      // Envoyer notification Telegram
      await sendTelegramNotification(updatedSub as Subscription);

      return new Response(JSON.stringify({
        success: true,
        message: 'Abonnement mis à jour',
        subscription_id: updatedSub.id
      }), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        status: 200
      });
    }

    // Créer un nouvel abonnement
    const newSubscription = {
      device_id: deviceId,
      jwt_token: jwtToken,
      payment_status: 'active',
      transaction_id: webhookData.transaction_id || `TX-${Date.now()}`,
      phone_number: webhookData.phone_number || '',
      amount: parseFloat(webhookData.amount || '100'),
      payment_date: new Date().toISOString(),
      expiry_date: expiryDate,
      fingerprint_data: {
        user_agent: req.headers.get('user-agent'),
        ip: req.headers.get('x-forwarded-for') || 'unknown'
      }
    };

    const { data: subscription, error: insertError } = await supabase
      .from('subscriptions')
      .insert(newSubscription)
      .select()
      .single();

    if (insertError) {
      console.error('❌ Erreur création abonnement:', insertError);
      throw insertError;
    }

    console.log('✅ Nouvel abonnement créé:', subscription.id);

    // Envoyer notification Telegram
    await sendTelegramNotification(subscription as Subscription);

    return new Response(JSON.stringify({
      success: true,
      message: 'Abonnement créé avec succès',
      subscription_id: subscription.id,
      device_id: deviceId,
      jwt_token: jwtToken,
      expiry_date: expiryDate
    }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      status: 200
    });

  } catch (error) {
    console.error('❌ Erreur webhook:', error);

    return new Response(JSON.stringify({
      success: false,
      error: error.message || 'Erreur lors du traitement du webhook',
      details: error.stack
    }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      status: 500
    });
  }
});
