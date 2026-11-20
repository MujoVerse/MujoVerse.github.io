import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { towers } from './tower-simulation.js';

function texture(draw, repeatX, repeatY) {
	const canvas = document.createElement('canvas');
	canvas.width = canvas.height = 32;
	draw(canvas.getContext('2d'));
	const map = new THREE.CanvasTexture(canvas);
	map.colorSpace = THREE.SRGBColorSpace;
	map.wrapS = map.wrapT = THREE.RepeatWrapping;
	map.repeat.set(repeatX, repeatY);
	map.magFilter = THREE.NearestFilter;
	return map;
}

function blockTexture(tower, cap) {
	return texture((ctx) => {
		ctx.fillStyle = tower.color;
		ctx.fillRect(0, 0, 32, 32);
		let seed = 121;
		const random = () => ((seed = (1664525 * seed + 1013904223) >>> 0) / 2 ** 32);
		for (let y = 0; y < 32; y += 2) {
			for (let x = 0; x < 32; x += 2) {
				ctx.fillStyle = random() < 0.5 ? '#fff' : '#151419';
				ctx.globalAlpha = random() * 0.16;
				ctx.fillRect(x, y, 2 + Math.floor(random() * 2), 2);
			}
		}
		const wood = tower.id === 'oak' || tower.id === 'spruce';
		const brick = tower.id === 'brick' || tower.id === 'stone';
		ctx.fillStyle = '#232121';
		ctx.globalAlpha = wood || brick ? 0.36 : 0.18;
		if (!cap && (wood || brick)) {
			for (let y = 0; y < 32; y += wood ? 8 : 16) {
				ctx.fillRect(0, y, 32, 1);
				if (brick) ctx.fillRect(y ? 17 : 3, y, 1, 16);
			}
		} else {
			ctx.fillRect(0, 0, 32, 1);
			ctx.fillRect(0, 0, 1, 32);
		}
	}, 2, cap ? 2 : tower.height);
}

export function createTowerScene(host, onSelect) {
	const scene = new THREE.Scene();
	const background = 0x20282b;
	scene.background = new THREE.Color(background);
	scene.fog = new THREE.Fog(background, 24, 63);

	const camera = new THREE.PerspectiveCamera(37, 1, 0.1, 100);
	const renderer = new THREE.WebGLRenderer({ antialias: true });
	renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
	renderer.shadowMap.enabled = true;
	renderer.shadowMap.type = THREE.PCFShadowMap;
	renderer.toneMapping = THREE.ACESFilmicToneMapping;
	renderer.toneMappingExposure = 1.2;
	const canvas = renderer.domElement;
	canvas.setAttribute('aria-hidden', 'true');
	host.append(canvas);

	const controls = new OrbitControls(camera, canvas);
	controls.enableDamping = true;
	controls.enablePan = false;
	controls.minPolarAngle = 0.24;
	controls.maxPolarAngle = Math.PI / 2 - 0.02;

	scene.add(new THREE.HemisphereLight(0xe2f2ff, 0x685449, 2.1));
	const light = new THREE.DirectionalLight(0xffebce, 2.7);
	light.position.set(-8, 18, 12);
	light.castShadow = true;
	Object.assign(light.shadow.camera, { left: -16, right: 16, top: 14, bottom: -14, near: 1, far: 48 });
	light.shadow.mapSize.set(1024, 1024);
	light.shadow.normalBias = 0.035;
	scene.add(light);
	const fill = new THREE.DirectionalLight(0x9ec2cd, 0.85);
	fill.position.set(6, 7, -12);
	scene.add(fill);

	function groundPlane(width, depth, height, material) {
		const mesh = new THREE.Mesh(new THREE.PlaneGeometry(width, depth), material);
		mesh.rotation.x = -Math.PI / 2;
		mesh.position.y = height;
		mesh.receiveShadow = true;
		scene.add(mesh);
	}

	const tile = (base, line, repeatsX, repeatsY) => texture((ctx) => {
		ctx.fillStyle = base;
		ctx.fillRect(0, 0, 32, 32);
		ctx.fillStyle = line;
		ctx.fillRect(0, 0, 32, 1);
		ctx.fillRect(0, 0, 1, 32);
	}, repeatsX, repeatsY);
	groundPlane(120, 120, -0.04, new THREE.MeshStandardMaterial({ map: tile('#3b4649', '#48575a', 60, 60) }));
	groundPlane(13, 11, -0.024, new THREE.MeshStandardMaterial({ color: 0xe9a73b }));
	groundPlane(11, 9, -0.015, new THREE.MeshStandardMaterial({ map: tile('#687576', '#7d8988', 11, 9) }));

	// MuJoCo's Z-up pose is mapped to the renderer's Y-up frame as a group.
	const bodies = new THREE.Group();
	bodies.rotation.x = -Math.PI / 2;
	scene.add(bodies);
	const outlineMaterial = new THREE.LineBasicMaterial({ color: 0xffda85, toneMapped: false });
	const blocks = towers.map((tower, index) => {
		const geometry = new THREE.BoxGeometry(2, 2, tower.height);
		const side = new THREE.MeshStandardMaterial({ map: blockTexture(tower, false), roughness: 0.83 });
		const cap = new THREE.MeshStandardMaterial({ map: blockTexture(tower, true), roughness: 0.83 });
		const mesh = new THREE.Mesh(geometry, [side, side, side, side, cap, cap]);
		mesh.castShadow = mesh.receiveShadow = true;
		mesh.userData.index = index;
		const outline = new THREE.LineSegments(new THREE.EdgesGeometry(geometry), outlineMaterial);
		outline.visible = false;
		mesh.add(outline);
		bodies.add(mesh);
		return { mesh, outline };
	});

	let aspect = 1;
	let cameraInitialized = false;
	function resetCamera() {
		const distance = aspect < 1.25 ? 1.25 / Math.max(aspect, 0.75) : 1;
		controls.target.set(0, 1.7, 0);
		camera.position.copy(controls.target).add(new THREE.Vector3(9.5, 9, 18).multiplyScalar(distance));
		controls.minDistance = 8;
		controls.maxDistance = Math.max(34, camera.position.distanceTo(controls.target) * 1.25);
		const damping = controls.enableDamping;
		controls.enableDamping = false;
		controls.update();
		controls.enableDamping = damping;
	}

	function resize() {
		const { clientWidth: width, clientHeight: height } = host;
		if (!width || !height) return;
		aspect = width / height;
		camera.aspect = aspect;
		camera.updateProjectionMatrix();
		renderer.setSize(width, height, false);
		if (!cameraInitialized) {
			resetCamera();
			cameraInitialized = true;
		}
	}
	const observer = new ResizeObserver(resize);
	observer.observe(host);
	resize();

	const ray = new THREE.Raycaster();
	const cursor = new THREE.Vector2();
	const clickable = blocks.map(({ mesh }) => mesh);
	let pointer;
	canvas.addEventListener('pointerdown', (event) => {
		pointer = event.isPrimary && event.button === 0 ? [event.clientX, event.clientY] : undefined;
	});
	canvas.addEventListener('pointercancel', () => { pointer = undefined; });
	canvas.addEventListener('pointerup', (event) => {
		const start = pointer;
		pointer = undefined;
		if (!start || !event.isPrimary || Math.hypot(event.clientX - start[0], event.clientY - start[1]) > 7) return;
		const rect = canvas.getBoundingClientRect();
		cursor.set(2 * (event.clientX - rect.left) / rect.width - 1, 1 - 2 * (event.clientY - rect.top) / rect.height);
		ray.setFromCamera(cursor, camera);
		const hit = ray.intersectObjects(clickable, false)[0];
		if (hit) onSelect(hit.object.userData.index);
	});

	return {
		canvas,
		select(index) {
			blocks.forEach(({ outline }, i) => { outline.visible = i === index; });
		},
		render(simulation) {
			const positions = simulation.positions;
			const rotations = simulation.rotations;
			blocks.forEach(({ mesh }, i) => {
				const p = (i + 1) * 3;
				const q = (i + 1) * 4;
				mesh.position.fromArray(positions, p);
				mesh.quaternion.set(rotations[q + 1], rotations[q + 2], rotations[q + 3], rotations[q]);
			});
			controls.update();
			renderer.render(scene, camera);
		},
		resetCamera,
		dispose() {
			observer.disconnect();
			controls.dispose();
			scene.traverse((object) => {
				object.geometry?.dispose();
				for (const material of [object.material].flat()) {
					material?.map?.dispose();
					material?.dispose();
				}
			});
			light.shadow.dispose();
			renderer.dispose();
			canvas.remove();
		},
	};
}
