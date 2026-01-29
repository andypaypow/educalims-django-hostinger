// ===== TURBOQUINTE BACKTEST - SUPABASE EDGE FUNCTION =====
// Analyse d'arrivée par rapport aux combinaisons filtrées

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// ===== CONFIGURATION =====
const SUPABASE_URL = Deno.env.get('SUPABASE_URL') || 'https://qfkyzljqykymahlpmdnu.supabase.co';
const SUPABASE_ANON_KEY = Deno.env.get('SUPABASE_ANON_KEY') || '';
const PAYMENT_LINK = Deno.env.get('PAYMENT_LINK') ||
  'https://sumb.cyberschool.ga/?productId=KzIfBGUYU6glnH3JlsbZ&operationAccountCode=ACC_6835C458B85FF&maison=moov&amount=100';

// ===== TYPES =====

interface Group {
  name: string;
  horses: number[];
  min: number;
  max: number;
}

interface BacktestRequest {
  arrival: number[];
  combinations: number[][];
  groups: Group[];
  device_id?: string;
  jwt_token?: string;
}

interface BacktestResponse {
  arrival: number[];
  isPresent: boolean;
  combinationIndex?: number;
  matchingCombination?: number[];
  groupAnalysis: GroupAnalysis[];
  statistics: BacktestStatistics;
}

interface GroupAnalysis {
  groupName: string;
  groupHorses: number[];
  arrivalMatches: number[];
  matchCount: number;
  withinRange: boolean;
}

interface BacktestStatistics {
  totalArrivalHorses: number;
  matchedHorsesInCombination: number;
  matchPercentage: number;
}

// ===== VÉRIFICATION ABONNEMENT =====

async function verifySubscription(deviceId: string, jwtToken?: string): Promise<{ hasAccess: boolean; message: string }> {
  if (!deviceId) {
    return { hasAccess: false, message: 'Device ID requis. Veuillez effectuer un paiement.' };
  }

  const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  const now = new Date().toISOString();

  const { data: subscription, error } = await supabase
    .from('subscriptions')
    .select('*')
    .eq('device_id', deviceId)
    .gte('expiry_date', now)
    .order('created_at', { ascending: false })
    .limit(1)
    .maybeSingle();

  if (error || !subscription) {
    return { hasAccess: false, message: 'Aucun abonnement actif. Veuillez effectuer un paiement.' };
  }

  if (subscription.payment_status !== 'active') {
    return { hasAccess: false, message: `Abonnement ${subscription.payment_status}. Veuillez effectuer un paiement.` };
  }

  if (jwtToken && subscription.jwt_token !== jwtToken) {
    return { hasAccess: false, message: 'Token invalide. Reconnectez-vous.' };
  }

  return { hasAccess: true, message: 'Accès autorisé' };
}

// ===== FONCTIONS D'ANALYSE =====

function analyzeGroupCoverage(
  arrival: number[],
  combination: number[],
  group: Group
): GroupAnalysis {
  const arrivalSet = new Set(arrival);
  const combinationSet = new Set(combination);

  const arrivalMatches = group.horses.filter(horse => arrivalSet.has(horse));
  const combinationMatches = group.horses.filter(horse => combinationSet.has(horse));
  const matchCount = combinationMatches.length;
  const withinRange = matchCount >= group.min && matchCount <= group.max;

  return {
    groupName: group.name,
    groupHorses: group.horses,
    arrivalMatches,
    matchCount,
    withinRange
  };
}

function calculateBacktestStatistics(
  arrival: number[],
  combination: number[]
): BacktestStatistics {
  const arrivalSet = new Set(arrival);
  const combinationSet = new Set(combination);

  const matchedHorses = combination.filter(horse => arrivalSet.has(horse));
  const matchPercentage = (matchedHorses.length / arrival.length) * 100;

  return {
    totalArrivalHorses: arrival.length,
    matchedHorsesInCombination: matchedHorses.length,
    matchPercentage: Math.round(matchPercentage * 100) / 100
  };
}

function findMatchingCombination(
  arrival: number[],
  combinations: number[][]
): { index: number; combination: number[] } | null {
  // Chercher une correspondance exacte
  for (let i = 0; i < combinations.length; i++) {
    if (arraysEqual(arrival, combinations[i])) {
      return { index: i, combination: combinations[i] };
    }
  }

  // Chercher une correspondance partielle (au moins 50% des chevaux)
  const arrivalSet = new Set(arrival);
  const threshold = Math.ceil(arrival.length * 0.5);

  for (let i = 0; i < combinations.length; i++) {
    const matchCount = combinations[i].filter(horse => arrivalSet.has(horse)).length;
    if (matchCount >= threshold) {
      return { index: i, combination: combinations[i] };
    }
  }

  return null;
}

function arraysEqual(a: number[], b: number[]): boolean {
  if (a.length !== b.length) return false;
  const sortedA = [...a].sort((x, y) => x - y);
  const sortedB = [...b].sort((x, y) => x - y);
  return sortedA.every((val, idx) => val === sortedB[idx]);
}

// ===== EDGE FUNCTION HANDLER =====

serve(async (req) => {
  // Gérer les requêtes OPTIONS (CORS)
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, apikey'
      }
    });
  }

  // Gérer uniquement les requêtes POST
  if (req.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
  }

  try {
    const request: BacktestRequest = await req.json();

    console.log('📊 Backtest reçu:', JSON.stringify(request, null, 2));

    // ===== VÉRIFICATION ABONNEMENT =====
    const deviceId = request.device_id;
    const jwtToken = request.jwt_token;

    console.log(`🔍 Vérification abonnement pour device: ${deviceId?.substring(0, 8)}...`);

    const accessCheck = await verifySubscription(deviceId, jwtToken);

    if (!accessCheck.hasAccess) {
      console.log(`❌ Accès refusé: ${accessCheck.message}`);
      return new Response(JSON.stringify({
        error: 'Abonnement requis',
        message: accessCheck.message,
        payment_link: PAYMENT_LINK
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        status: 403
      });
    }

    console.log('✅ Abonnement vérifié, traitement du backtest...');

    const { arrival, combinations, groups } = request;

    // Validation des entrées
    if (!arrival || arrival.length === 0) {
      throw new Error('Arrivée invalide : veuillez fournir une combinaison d\'arrivée');
    }

    if (!combinations || combinations.length === 0) {
      throw new Error('Aucune combinaison fournie pour le backtest');
    }

    console.log(`✅ Arrivée: [${arrival.join(', ')}]`);
    console.log(`✅ ${combinations.length} combinaisons à analyser`);

    // Chercher une combinaison correspondante
    const matchResult = findMatchingCombination(arrival, combinations);
    const isPresent = matchResult !== null;

    // Analyser la couverture par groupes
    const groupAnalysis: GroupAnalysis[] = [];

    if (groups && groups.length > 0) {
      // Utiliser la combinaison trouvée ou la première combinaison pour l'analyse
      const combinationToAnalyze = matchResult?.combination || combinations[0];

      for (const group of groups) {
        const analysis = analyzeGroupCoverage(arrival, combinationToAnalyze, group);
        groupAnalysis.push(analysis);
      }
    }

    // Calculer les statistiques
    const combinationToAnalyze = matchResult?.combination || combinations[0];
    const statistics = calculateBacktestStatistics(arrival, combinationToAnalyze);

    const response: BacktestResponse = {
      arrival,
      isPresent,
      groupAnalysis,
      statistics
    };

    if (isPresent && matchResult) {
      response.combinationIndex = matchResult.index;
      response.matchingCombination = matchResult.combination;
    }

    console.log(`✅ Backtest terminé - Présent: ${isPresent}`);

    return new Response(JSON.stringify(response), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      status: 200
    });

  } catch (error) {
    console.error('❌ Erreur lors du backtest:', error);

    return new Response(JSON.stringify({
      error: error.message || 'Erreur lors du backtest',
      details: error.stack
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      status: 400
    });
  }
});
