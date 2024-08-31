<script lang="ts">
	import ChatBox from './ChatBox.svelte';
	import supabase from '$lib/supabase';
	import type { Tables } from '$lib/supabase';
	import SvelteMarkdown from 'svelte-markdown';
	import { onMount } from 'svelte';

	export let events: Tables['events']['Row'][];
	export let profile: Tables['profiles']['Row'];

	let isTyping = false;

	onMount(() => {});
</script>

<div class="items-between flex flex-col justify-start gap-2 overflow-y-scroll pt-2">
	{#each [shownEvents] as msg, i (i)}
		<div class={`flex ${msg.name === 'user' ? 'ml-16 justify-end' : 'mr-16 justify-start'}`}>
			<p
				class="prose prose-main rounded-lg border border-primary/30 bg-primary-container/10 px-2 py-1 text-primary-container-on marker:text-primary"
			>
				<SvelteMarkdown bind:source={msg.content} />
			</p>
			<div class="relative flex flex-col">
				<small class="opacity-30">name: {msg.name}</small>
				<small class="opacity-30">type: {msg.event_type}</small>
			</div>
		</div>
	{/each}
	{#if isTyping}
		<div class="mr-16 flex animate-pulse justify-start">
			<p
				class="rounded-lg border border-primary/30 bg-primary-container/10 px-2 py-1 text-primary-container-on"
			>
				. . .
			</p>
		</div>
	{/if}
</div>
<div class="items-between flex flex-col justify-end gap-2">
	<hr class="mt-2 border-primary/10" />
	<ChatBox bind:isTyping bind:events {profile} />
</div>
