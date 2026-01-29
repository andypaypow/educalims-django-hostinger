// ===== CREATE SUBSCRIPTIONS TABLE - TEMPORARY FUNCTION =====
// Crée la table subscriptions si elle n'existe pas via connexion PostgreSQL directe

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { Client } from "https://deno.land/x/postgres@v0.17.0/mod.ts";

const SUPABASE_URL = Deno.env.get('SUPABASE_URL') || 'https://qfkyzljqykymahlpmdnu.supabase.co';
const DATABASE_URL = Deno.env.get('DATABASE_URL') || '';

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
      }
    });
  }

  if (req.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
  }

  let client: Client | null = null;

  try {
    console.log('🔗 Connexion à PostgreSQL...');

    // Créer le client PostgreSQL
    client = new Client(DATABASE_URL);
    await client.connect();

    console.log('✅ Connecté à PostgreSQL');

    // Créer la table subscriptions
    console.log('📊 Création de la table subscriptions...');
    await client.queryObject(`
      CREATE TABLE IF NOT EXISTS subscriptions (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        device_id TEXT UNIQUE NOT NULL,
        jwt_token TEXT UNIQUE NOT NULL,
        payment_status TEXT DEFAULT 'pending',
        transaction_id TEXT,
        phone_number TEXT,
        amount NUMERIC DEFAULT 100,
        payment_date TIMESTAMP WITH TIME ZONE,
        expiry_date TIMESTAMP WITH TIME ZONE,
        fingerprint_data JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      );
    `);
    console.log('✅ Table subscriptions créée');

    // Créer les index
    console.log('📇 Création des index...');

    try {
      await client.queryObject(`CREATE INDEX IF NOT EXISTS idx_subscriptions_device_id ON subscriptions(device_id);`);
      console.log('✅ Index device_id créé');
    } catch (e: any) {
      console.log('⚠️ Index device_id:', e.message);
    }

    try {
      await client.queryObject(`CREATE INDEX IF NOT EXISTS idx_subscriptions_jwt_token ON subscriptions(jwt_token);`);
      console.log('✅ Index jwt_token créé');
    } catch (e: any) {
      console.log('⚠️ Index jwt_token:', e.message);
    }

    try {
      await client.queryObject(`CREATE INDEX IF NOT EXISTS idx_subscriptions_expiry ON subscriptions(expiry_date);`);
      console.log('✅ Index expiry_date créé');
    } catch (e: any) {
      console.log('⚠️ Index expiry_date:', e.message);
    }

    // Vérifier que la table existe
    const result = await client.queryObject(`
      SELECT COUNT(*) as count FROM subscriptions;
    `);
    console.log(`📊 Table subscriptions contient ${result.rows[0].count} enregistrements`);

    await client.end();

    return new Response(JSON.stringify({
      success: true,
      message: 'Table subscriptions créée avec succès !',
      count: result.rows[0].count
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      status: 200
    });

  } catch (error: any) {
    console.error('❌ Erreur:', error);

    if (client) {
      try {
        await client.end();
      } catch (e) {
        // Ignore
      }
    }

    return new Response(JSON.stringify({
      success: false,
      error: error.message || 'Erreur lors de la création de la table',
      details: error.stack
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      status: 500
    });
  }
});
