import { writable } from 'svelte/store';

export const PLAYER_MAX_HP = 20;

function createPlayerHP() {
  const { subscribe, set, update } = writable(PLAYER_MAX_HP);

  return {
    subscribe,
    damage: (amount: number = 5) =>
      update((v) => Math.max(0, v - Math.abs(amount))),
    heal: (amount: number = 5) => update((v) => Math.min(PLAYER_MAX_HP, v + Math.abs(amount))),
    reset: () => set(PLAYER_MAX_HP),
  };
}

export const playerHP = createPlayerHP();
