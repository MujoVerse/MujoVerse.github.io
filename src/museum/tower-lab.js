import loadMujoco from '@mujoco/mujoco';
import wasmUrl from '@mujoco/mujoco/mujoco.wasm?url';
import { createTowerSimulation, isToppled, timestep } from './tower-simulation.js';
import { createTowerScene } from './tower-scene.js';

export async function startTowerLab(lab) {
	const message = lab.querySelector('[data-message]');
	const poster = lab.querySelector('[data-poster]');
	const strike = lab.querySelector('[data-strike]');
	const reset = lab.querySelector('[data-reset]');
	const camera = lab.querySelector('[data-camera]');
	const strength = lab.querySelector('[data-strength]');
	const strengthValue = lab.querySelector('[data-strength-value]');
	const choices = [...lab.querySelectorAll('[data-tower]')];
	const target = lab.querySelector('[data-target]');
	const hits = lab.querySelector('[data-hits]');
	const fallen = lab.querySelector('[data-fallen]');
	const live = lab.querySelector('[data-live]');
	const controls = [strike, reset, camera, strength, ...choices];
	let simulation;
	let scene;
	let frame;
	let selected = 0;
	let hitCount = 0;
	let fallenCount = 0;
	let lastTime;
	let accumulator = 0;

	function fail(error) {
		cancelAnimationFrame(frame);
		scene?.dispose();
		simulation?.dispose();
		controls.forEach((control) => { control.disabled = true; });
		poster.hidden = false;
		message.textContent = lab.dataset.unavailable;
		message.hidden = false;
		live.textContent = lab.dataset.offline;
		lab.dataset.state = 'unavailable';
		console.error('Museum lab unavailable:', error);
	}

	function select(index) {
		selected = index;
		choices.forEach((choice, i) => choice.setAttribute('aria-pressed', String(i === index)));
		target.textContent = choices[index].getAttribute('aria-label');
		scene.select(index);
	}

	function render(time) {
		const elapsed = lastTime === undefined ? 0 : (time - lastTime) / 1000;
		lastTime = time;
		accumulator = Math.min(accumulator + elapsed, 0.05);
		while (accumulator >= timestep) {
			simulation.step();
			accumulator -= timestep;
		}
		scene.render(simulation);
		const rotations = simulation.rotations;
		const count = choices.filter((_, i) => isToppled(rotations, (i + 1) * 4)).length;
		if (fallenCount !== count) {
			fallenCount = count;
			fallen.textContent = `${count} / ${choices.length}`;
		}
		frame = requestAnimationFrame(render);
	}

	try {
		const mj = await loadMujoco({ locateFile: () => wasmUrl });
		simulation = createTowerSimulation(mj);
		scene = createTowerScene(lab.querySelector('[data-canvas]'), select);
		scene.canvas.addEventListener('webglcontextlost', () => fail(new Error('WebGL context lost')), { once: true });
		select(0);
		scene.render(simulation);
	} catch (error) {
		fail(error);
		return;
	}

	choices.forEach((choice, i) => choice.addEventListener('click', () => select(i)));
	strength.addEventListener('input', () => { strengthValue.textContent = `${strength.value}%`; });
	strike.addEventListener('click', () => {
		if (simulation.strike(selected, strength.valueAsNumber)) hits.textContent = String(++hitCount);
	});
	reset.addEventListener('click', () => {
		simulation.reset();
		hitCount = fallenCount = accumulator = 0;
		hits.textContent = '0';
		fallen.textContent = `0 / ${choices.length}`;
	});
	camera.addEventListener('click', scene.resetCamera);
	controls.forEach((control) => { control.disabled = false; });
	poster.hidden = message.hidden = true;
	live.textContent = lab.dataset.running;
	lab.dataset.state = 'ready';
	frame = requestAnimationFrame(render);

	document.addEventListener('visibilitychange', () => {
		if (lab.dataset.state !== 'ready') return;
		if (document.hidden) cancelAnimationFrame(frame);
		else {
			lastTime = undefined;
			frame = requestAnimationFrame(render);
		}
	});
}
