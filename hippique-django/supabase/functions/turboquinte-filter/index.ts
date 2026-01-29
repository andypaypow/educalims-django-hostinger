// ===== TURBOQUINTE FILTER - SUPABASE EDGE FUNCTION =====
// Logique de filtrage des combinaisons hippiques

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// ===== CONFIGURATION =====
const SUPABASE_URL = Deno.env.get('SUPABASE_URL') || 'https://qfkyzljqykymahlpmdnu.supabase.co';
const SUPABASE_ANON_KEY = Deno.env.get('SUPABASE_ANON_KEY') || '';
const PAYMENT_LINK = Deno.env.get('PAYMENT_LINK') ||
  'https://sumb.cyberschool.ga/?productId=KzIfBGUYU6glnH3JlsbZ&operationAccountCode=ACC_6835C458B85FF&maison=moov&amount=100';

// ===== TYPES =====
interface BaseConfig {
  numPartants: number;
  tailleCombinaison: number;
}

interface Group {
  name: string;
  horses: number[];
  min: number;
  max: number;
}

interface StandardFilter {
  chevauxMin: number;
  groupesMin: number;
}

interface AdvancedFilter {
  chevauxMin: number;
  groupesMin: number;
}

interface WeightFilter {
  source: 'default' | 'manual' | 'citation' | 'position' | 'results' | 'expert';
  min: number;
  max: number;
  manualWeights?: number[];
}

interface StatisticFilters {
  evenOddFilters?: Array<{ min: number; max: number }>;
  smallLargeFilters?: Array<{ limit: number; min: number; max: number }>;
  consecutiveFilters?: Array<{ min: number; max: number }>;
}

interface AlternanceFilter {
  source: 'default' | 'manual' | 'citation' | 'position' | 'results' | 'expert';
  sourceArray?: number[];
  min: number;
  max: number;
}

interface FilterRequest {
  config: BaseConfig;
  groups: Group[];
  standardFilters: StandardFilter[];
  advancedFilters: AdvancedFilter[];
  weightFilters: WeightFilter[];
  evenOddFilters: Array<{ min: number; max: number }>;
  smallLargeFilters: Array<{ limit: number; min: number; max: number }>;
  consecutiveFilters: Array<{ min: number; max: number }>;
  alternanceFilters: AlternanceFilter[];
  device_id?: string;
  jwt_token?: string;
}

interface SynthesisData {
  citation: [number, number][];
  position: [number, number][];
  results: [number, number][];
  expert: [number, number][];
}

interface FilterResponse {
  filteredCombinations: number[][];
  totalCount: number;
  filteredCount: number;
  reductionRate: number;
  synthesis: SynthesisData;
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

// ===== FONCTIONS DE GÉNÉRATION =====

function* combinationGenerator(arr: number[], k: number): Generator<number[]> {
  if (k === 0) { yield []; return; }
  for (let i = 0; i <= arr.length - k; i++) {
    for (const c of combinationGenerator(arr.slice(i + 1), k - 1)) {
      yield [arr[i], ...c];
    }
  }
}

function combinationsCount(n: number, k: number): number {
  if (k < 0 || k > n) return 0;
  if (k === 0 || k === n) return 1;
  if (k > n / 2) k = n - k;
  let res = 1;
  for (let i = 1; i <= k; i++) {
    res = res * (n - i + 1) / i;
  }
  return Math.round(res);
}

// ===== FILTRES =====

function filterByGroupMinMax(combination: number[], groups: Group[]): boolean {
  for (const group of groups) {
    const horsesInGroup = combination.filter(horse =>
      group.horses.includes(horse)
    ).length;

    if (horsesInGroup < group.min || horsesInGroup > group.max) {
      return false;
    }
  }
  return true;
}

function filterStandardOR(combination: number[], groups: Group[], filter: StandardFilter): boolean {
  const matchingGroups = groups.filter(group => {
    const horsesInGroup = combination.filter(horse =>
      group.horses.includes(horse)
    ).length;
    return horsesInGroup >= filter.chevauxMin;
  });

  return matchingGroups.length >= filter.groupesMin;
}

function filterAdvancedAND(combination: number[], groups: Group[], filter: AdvancedFilter): boolean {
  const horseGroupCount: Record<number, number> = {};

  combination.forEach(horse => {
    horseGroupCount[horse] = 0;
    groups.forEach(group => {
      if (group.horses.includes(horse)) {
        horseGroupCount[horse]++;
      }
    });
  });

  const commonHorses = Object.keys(horseGroupCount).filter(
    horse => horseGroupCount[parseInt(horse)] >= filter.groupesMin
  );

  return commonHorses.length >= filter.chevauxMin;
}

function buildWeightMap(filter: WeightFilter, numPartants: number, synthesisData: SynthesisData): Map<string, number> {
  const weightMap = new Map<string, number>();

  // Initialiser tous les chevaux avec une pénalité
  for (let i = 1; i <= numPartants; i++) {
    weightMap.set(i.toString(), numPartants + 1);
  }

  switch (filter.source) {
    case 'default':
      for (let i = 1; i <= numPartants; i++) {
        weightMap.set(i.toString(), i);
      }
      break;

    case 'manual':
      filter.manualWeights?.forEach((horse, index) => {
        weightMap.set(horse.toString(), index + 1);
      });
      break;

    case 'citation':
      synthesisData.citation.forEach(([horse, _], index) => {
        weightMap.set(horse.toString(), index + 1);
      });
      break;

    case 'position':
      synthesisData.position.forEach(([horse, _], index) => {
        weightMap.set(horse.toString(), index + 1);
      });
      break;

    case 'results':
      synthesisData.results.forEach(([horse, _], index) => {
        weightMap.set(horse.toString(), index + 1);
      });
      break;

    case 'expert':
      synthesisData.expert.forEach(([horse, _], index) => {
        weightMap.set(horse.toString(), index + 1);
      });
      break;
  }

  return weightMap;
}

function filterByWeight(combination: number[], weightMap: Map<string, number>, filter: WeightFilter): boolean {
  const totalWeight = combination.reduce((sum, horse) => {
    return sum + (weightMap.get(horse.toString()) || 0);
  }, 0);

  return totalWeight >= filter.min && totalWeight <= filter.max;
}

function filterByEvenOdd(combination: number[], filter: { min: number; max: number }): boolean {
  const evenCount = combination.filter(num => num % 2 === 0).length;
  return evenCount >= filter.min && evenCount <= filter.max;
}

function filterBySmallLarge(combination: number[], filter: { limit: number; min: number; max: number }): boolean {
  const smallCount = combination.filter(num => num <= filter.limit).length;
  return smallCount >= filter.min && smallCount <= filter.max;
}

function getLongestConsecutive(arr: number[]): number {
  if (arr.length < 2) return arr.length;

  const sorted = [...arr].sort((a, b) => a - b);
  let maxLen = 1;
  let currentLen = 1;

  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i] === sorted[i - 1] + 1) {
      currentLen++;
    } else {
      maxLen = Math.max(maxLen, currentLen);
      currentLen = 1;
    }
  }

  return Math.max(maxLen, currentLen);
}

function filterByConsecutive(combination: number[], filter: { min: number; max: number }): boolean {
  const longest = getLongestConsecutive(combination);
  return longest >= filter.min && longest <= filter.max;
}

function calculateAlternances(combination: number[], sourceArray: number[]): number {
  if (sourceArray.length === 0) return 0;

  const combinationSet = new Set(combination.map(String));
  let alternances = 0;

  for (let i = 0; i < sourceArray.length - 1; i++) {
    const currentIn = combinationSet.has(sourceArray[i].toString());
    const nextIn = combinationSet.has(sourceArray[i + 1].toString());

    if (currentIn !== nextIn) {
      alternances++;
    }
  }

  return alternances;
}

function filterByAlternance(combination: number[], filter: AlternanceFilter, synthesisData: SynthesisData): boolean {
  let sourceArray: number[] = [];

  switch (filter.source) {
    case 'default':
      sourceArray = Array.from({ length: 16 }, (_, i) => i + 1);
      break;
    case 'manual':
      sourceArray = filter.sourceArray || [];
      break;
    case 'citation':
      sourceArray = synthesisData.citation.map(([h]) => h);
      break;
    case 'position':
      sourceArray = synthesisData.position.map(([h]) => h);
      break;
    case 'results':
      sourceArray = synthesisData.results.map(([h]) => h);
      break;
    case 'expert':
      sourceArray = synthesisData.expert.map(([h]) => h);
      break;
  }

  const alternanceCount = calculateAlternances(combination, sourceArray);
  return alternanceCount >= filter.min && alternanceCount <= filter.max;
}

function calculateSynthesisData(groups: Group[], combinations: number[][]): SynthesisData {
  // Synthèse par citation
  const citationCounts: Record<number, number> = {};
  groups.forEach(group => {
    group.horses.forEach(horse => {
      citationCounts[horse] = (citationCounts[horse] || 0) + 1;
    });
  });
  const citation = Object.entries(citationCounts)
    .sort((a, b) => b[1] - a[1])
    .map(([horse, count]) => [parseInt(horse), count]);

  // Synthèse par position
  const positionScores: Record<number, number> = {};
  groups.forEach(group => {
    group.horses.forEach((horse, index) => {
      positionScores[horse] = (positionScores[horse] || 0) + (group.horses.length - index);
    });
  });
  const position = Object.entries(positionScores)
    .sort((a, b) => b[1] - a[1])
    .map(([horse, score]) => [parseInt(horse), score]);

  // Synthèse des résultats
  const horseCounts: Record<number, number> = {};
  combinations.flat().forEach(horse => {
    horseCounts[horse] = (horseCounts[horse] || 0) + 1;
  });
  const results = Object.entries(horseCounts)
    .sort((a, b) => b[1] - a[1])
    .map(([horse, count]) => [parseInt(horse), count]);

  // Synthèse expert
  const weights = { citation: 1.0, position: 1.5, results: 2.0 };
  const allHorses = new Set([
    ...citation.map(h => h[0]),
    ...position.map(h => h[0]),
    ...results.map(h => h[0])
  ]);

  const rankPoints = {
    citation: new Map(citation.map(([h, _], i) => [h, citation.length - i])),
    position: new Map(position.map(([h, _], i) => [h, position.length - i])),
    results: new Map(results.map(([h, _], i) => [h, results.length - i]))
  };

  const finalScores: Record<number, number> = {};
  allHorses.forEach(horse => {
    const pCitation = rankPoints.citation.get(horse) || 0;
    const pPosition = rankPoints.position.get(horse) || 0;
    const pResults = rankPoints.results.get(horse) || 0;

    finalScores[horse] =
      (pCitation * weights.citation) +
      (pPosition * weights.position) +
      (pResults * weights.results);
  });

  const expert = Object.entries(finalScores)
    .sort((a, b) => b[1] - a[1])
    .map(([horse, score]) => [parseInt(horse), score]);

  return { citation, position, results, expert };
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
    const request: FilterRequest = await req.json();

    console.log('📊 Reçu:', JSON.stringify(request, null, 2));

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

    console.log('✅ Abonnement vérifié, traitement du filtrage...');

    const { config, groups, standardFilters, advancedFilters, weightFilters,
            evenOddFilters, smallLargeFilters, consecutiveFilters, alternanceFilters } = request;

    // Génération de toutes les combinaisons
    const partants = Array.from({ length: config.numPartants }, (_, i) => i + 1);
    const allCombinations: number[][] = [];

    for (const combo of combinationGenerator(partants, config.tailleCombinaison)) {
      allCombinations.push(combo);
    }

    console.log(`✅ ${allCombinations.length} combinaisons générées`);

    // Calculer les synthèses de pronostics
    const synthesisData = calculateSynthesisData(groups, []);

    // Appliquer les filtres
    let filtered = [...allCombinations];

    // Filtres de groupes
    if (groups.length > 0) {
      filtered = filtered.filter(combo => filterByGroupMinMax(combo, groups));
      console.log(`✅ Après filtres groupes: ${filtered.length} combinaisons`);
    }

    // Filtres standard (Expert 1)
    if (standardFilters.length > 0) {
      for (const filter of standardFilters) {
        filtered = filtered.filter(combo => filterStandardOR(combo, groups, filter));
      }
      console.log(`✅ après Expert 1: ${filtered.length} combinaisons`);
    }

    // Filtres avancés (Expert 2)
    if (advancedFilters.length > 0) {
      for (const filter of advancedFilters) {
        filtered = filtered.filter(combo => filterAdvancedAND(combo, groups, filter));
      }
      console.log(`✅ Après Expert 2: ${filtered.length} combinaisons`);
    }

    // Filtres de poids
    if (weightFilters.length > 0) {
      for (const filter of weightFilters) {
        const weightMap = buildWeightMap(filter, config.numPartants, synthesisData);
        filtered = filtered.filter(combo => filterByWeight(combo, weightMap, filter));
      }
      console.log(`✅ Après filtres poids: ${filtered.length} combinaisons`);
    }

    // Filtres statistiques
    if (evenOddFilters.length > 0) {
      for (const filter of evenOddFilters) {
        filtered = filtered.filter(combo => filterByEvenOdd(combo, filter));
      }
    }

    if (smallLargeFilters.length > 0) {
      for (const filter of smallLargeFilters) {
        filtered = filtered.filter(combo => filterBySmallLarge(combo, filter));
      }
    }

    if (consecutiveFilters.length > 0) {
      for (const filter of consecutiveFilters) {
        filtered = filtered.filter(combo => filterByConsecutive(combo, filter));
      }
    }
    console.log(`✅ Après filtres statistiques: ${filtered.length} combinaisons`);

    // Filtres d'alternance
    if (alternanceFilters.length > 0) {
      for (const filter of alternanceFilters) {
        filtered = filtered.filter(combo => filterByAlternance(combo, filter, synthesisData));
      }
      console.log(`✅ Après filtres alternance: ${filtered.length} combinaisons`);
    }

    // Calculer les synthèses finales
    const finalSynthesis = calculateSynthesisData(groups, filtered);

    // Limiter les résultats envoyés
    const maxResults = 1000;
    const filteredCombinations = filtered.slice(0, maxResults);

    const response: FilterResponse = {
      filteredCombinations,
      totalCount: allCombinations.length,
      filteredCount: filtered.length,
      reductionRate: ((allCombinations.length - filtered.length) / allCombinations.length * 100),
      synthesis: finalSynthesis
    };

    console.log(`✅ ${filtered.length}/${allCombinations.length} combinaisons conservées (${((allCombinations.length - filtered.length) / allCombinations.length * 100).toFixed(2)}% de réduction)`);

    return new Response(JSON.stringify(response), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      status: 200
    });

  } catch (error) {
    console.error('❌ Erreur:', error);

    return new Response(JSON.stringify({
      error: error.message || 'Erreur lors du filtrage',
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
