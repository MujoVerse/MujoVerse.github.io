// The six assemble regions in the desktop museum's reset_towers function, centered on the lab.
export const towers = [
	{ id: 'oak', x: -4, z: -2.5, height: 6, color: '#c89959' },
	{ id: 'brick', x: 0, z: -2.5, height: 5, color: '#af5747' },
	{ id: 'spruce', x: 4, z: -2.5, height: 4, color: '#836547' },
	{ id: 'stone', x: -4, z: 2.5, height: 3, color: '#7b8b90' },
	{ id: 'copper', x: 0, z: 2.5, height: 4, color: '#d47a49' },
	{ id: 'concrete', x: 4, z: 2.5, height: 5, color: '#dae0da' },
];

export const timestep = 0.002;
const swingSteps = 30;
const xml = `<mujoco model="Museum rigid-body towers">
	<option timestep="${timestep}" gravity="0 0 -9.81" integrator="implicitfast"/>
	<default><geom density="700" friction="0.8 0.005 0.0001"/></default>
	<worldbody>
		<geom name="floor" type="plane" size="0 0 0.1"/>
		${towers.map(({ id, x, z, height }) => `<body name="${id}" pos="${x} ${-z} ${height / 2}">
			<freejoint/><geom type="box" size="1 1 ${height / 2}"/>
		</body>`).join('')}
	</worldbody>
</mujoco>`;

export function createTowerSimulation(mj) {
	const model = mj.MjModel.from_xml_string(xml);
	const data = new mj.MjData(model);
	const remaining = new Int32Array(towers.length);
	const forces = new Float64Array(towers.length);
	const mass = Float64Array.from(model.body_mass);
	const dirX = 0.18;
	const dirY = Math.sqrt(1 - dirX ** 2);
	mj.mj_forward(model, data);

	return {
		step() {
			const applied = data.xfrc_applied;
			const positions = data.xpos;
			for (let index = 0; index < towers.length; index++) {
				const offset = (index + 1) * 6;
				const force = remaining[index] > 0 ? forces[index] : 0;
				const heightOffset = positions[(index + 1) * 3 + 2] > 1.5 ? towers[index].height * 0.32 : 0;
				applied[offset] = dirX * force;
				applied[offset + 1] = dirY * force;
				// Apply the matching torque for a hit above the center of mass.
				applied[offset + 3] = -heightOffset * dirY * force;
				applied[offset + 4] = heightOffset * dirX * force;
				if (remaining[index] > 0) remaining[index]--;
			}
			mj.mj_step(model, data);
		},
		strike(index, strength) {
			if (!towers[index] || remaining[index] > 0) return false;
			const fraction = Math.min(1, Math.max(0.25, strength / 100));
			const speed = fraction * 5.5 * (mass[1] / mass[index + 1]) ** 0.25;
			forces[index] = mass[index + 1] * speed / (swingSteps * timestep);
			remaining[index] = swingSteps;
			return true;
		},
		reset() {
			remaining.fill(0);
			mj.mj_resetData(model, data);
			mj.mj_forward(model, data);
		},
		get positions() { return data.xpos; },
		get rotations() { return data.xquat; },
		dispose() {
			data.delete();
			model.delete();
		},
	};
}

export function isToppled(rotation, offset) {
	// The body's local up axis, projected onto the world up axis.
	return 1 - 2 * (rotation[offset + 1] ** 2 + rotation[offset + 2] ** 2) < 0.5;
}
