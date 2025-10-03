import { writable } from 'svelte/store';

export const ENEMY_MAX_HP = 100;
export const HIT_DAMAGE = 1;

function createEnemyHP() {
  const { subscribe, set, update } = writable<number>(ENEMY_MAX_HP);

  return {
    subscribe,
    reset: () => set(ENEMY_MAX_HP),
    damage: (amount: number) => update((v) => Math.max(0, v - amount)),
    set,
  };
}

export const enemyHP = createEnemyHP();
export default enemyHP;
