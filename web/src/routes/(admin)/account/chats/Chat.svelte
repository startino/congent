<script lang="ts">
	import ChatBox from './ChatBox.svelte';
	import type { Checkpoint, Tables } from '$lib/supabase';
	import SvelteMarkdown from 'svelte-markdown';
	import { onMount } from 'svelte';
	import { checkpointsToMessages } from '$lib/checkpoints';

	export let checkpoints: Checkpoint[];
	export let profile: Tables['profiles']['Row'];

	let isTyping = false;

	let messages = checkpointsToMessages(checkpoints);

	onMount(() => {});
</script>

<div class="items-between flex flex-col justify-start gap-2 overflow-y-scroll pt-2">
	{#each messages as msg, i (i)}
		<div class={`flex ${msg.name === 'user' ? 'ml-16 justify-end' : 'mr-16 justify-start'}`}>
			<p
				class="prose prose-main text-white rounded-lg border border-primary/30 bg-primary-container/10 px-2 py-1 text-primary-container-on marker:text-primary"
			>
				<SvelteMarkdown bind:source={msg.content} />
			</p>
			<div class="relative flex flex-col">
				
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
	<ChatBox bind:isTyping bind:checkpoints {profile} />
</div>
