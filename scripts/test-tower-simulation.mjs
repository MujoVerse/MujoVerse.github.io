import assert from 'node:assert/strict';
import { test } from 'node:test';
import loadMujoco from '@mujoco/mujoco';
import { createTowerSimulation, isToppled, towers } from '../src/museum/tower-simulation.js';

test('six desktop towers settle, react to strike strength, collide, and reset', async () => {
	const mj = await loadMujoco();
	assert.equal(mj.mj_versionString(), '3.8.0');
	const sim = createTowerSimulation(mj);
	const toppled = (i) => isToppled(sim.rotations, (i + 1) * 4);
	const advance = (steps) => { for (let i = 0; i < steps; i++) sim.step(); };
	try {
		const start = [-4, 2.5, 3, 0, 2.5, 2.5, 4, 2.5, 2, -4, -2.5, 1.5, 0, -2.5, 2, 4, -2.5, 2.5];
		assert.deepEqual(Array.from(sim.positions.slice(3)), start);
		advance(500);
		assert.ok(towers.every((_, i) => !toppled(i)));

		assert.ok(sim.strike(0, 25));
		assert.equal(sim.strike(0, 25), false, 'do not stack strikes during the same swing');
		advance(1000);
		assert.ok(!toppled(0));
		sim.reset();
		assert.ok(sim.strike(0, 100));
		advance(1000);
		assert.ok(toppled(0));

		sim.reset();
		assert.ok(sim.strike(5, 70));
		advance(1000);
		assert.ok(toppled(2), 'the front tower transfers momentum to the rear tower');

		sim.reset();
		advance(500);
		assert.ok(towers.every((_, i) => !toppled(i)));
		assert.ok(sim.positions.slice(3).every((value, i) => Math.abs(value - start[i]) < 0.001));
	} finally {
		sim.dispose();
	}
});
