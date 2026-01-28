// ===== TURBOQUINTE BACKTEST - SUPABASE EDGE FUNCTION =====
// Analyse d'arrivée par rapport aux combinaisons filtrées

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

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
