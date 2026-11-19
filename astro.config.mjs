// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
	site: 'https://mujoverse.github.io',
	integrations: [
		starlight({
			title: 'MujoVerse',
			description: 'Real robots, real MuJoCo physics, in Minecraft.',
			defaultLocale: 'root',
			locales: {
				root: { label: '简体中文', lang: 'zh-CN' },
				en: { label: 'English', lang: 'en' },
			},
			logo: { src: './src/assets/avatar-64.png', replacesTitle: false },
			favicon: '/favicon-48.png',
			head: [{ tag: 'link', attrs: { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' } }],
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/MujoVerse' }],
			customCss: [
				'@fontsource/unbounded/600.css',
				'@fontsource/unbounded/800.css',
				'@fontsource/ibm-plex-sans/400.css',
				'@fontsource/ibm-plex-sans/600.css',
				'@fontsource/ibm-plex-mono/400.css',
				'./src/styles/theme.css',
			],
			sidebar: [
				{
					label: '玩家指南', translations: { en: 'Player guide' },
					items: [
						{ slug: 'guide/install' },
						{ slug: 'guide/robots' },
						{ slug: 'guide/driving' },
						{ slug: 'guide/fpv' },
						{ slug: 'guide/physics' },
						{ slug: 'guide/exhibits' },
						{ slug: 'guide/football' },
						{ slug: 'guide/museum' },
					],
				},
				{
					label: '研究者', translations: { en: 'Researchers' },
					items: [
						{ slug: 'research/quickstart' },
						{ slug: 'research/python' },
						{ slug: 'research/recording' },
						{ slug: 'research/worldedit' },
						{ slug: 'research/protocol' },
					],
				},
				{
					label: '模组开发者', translations: { en: 'Mod developers' },
					items: [{ slug: 'dev/build' }, { slug: 'dev/api' }, { slug: 'dev/exhibits' }],
				},
				{
					label: '验证', translations: { en: 'Verification' },
					items: [{ slug: 'verify' }],
				},
				{
					label: '关于', translations: { en: 'About' },
					items: [{ slug: 'about/licenses' }, { slug: 'about/roadmap' }],
				},
			],
		}),
	],
});
