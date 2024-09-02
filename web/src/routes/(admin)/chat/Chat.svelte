<script lang="ts">
	import ChatBox from './ChatBox.svelte';
	import type { Checkpoint, Tables } from '$lib/supabase';
	import SvelteMarkdown from 'svelte-markdown';
	import { onMount } from 'svelte';
	import { BaseMessage, AIMessage, ToolMessage } from '@langchain/core/messages';
  	import { supabase } from '$lib/supabase';

	export let events: Tables['events']['Row'][] = [];
	export let profile: Tables['profiles']['Row'];

	let isTyping = false;

	function splitEvents(events: Tables['events']['Row'][]): Tables['events']['Row'][] {
		const result: Tables['events']['Row'][] = [];

		for (const event of events) {
			if (!event.content) {
				event.content = "NO CONTENT";
			}
			const parts = event.content.split('\n\n').map((part) => part.trim());

			if (parts.length > 1) {
				// Create new events for each split part
				result.push(
					...parts
						.filter((part) => part !== '')
						.map((part) => ({ ...event, content: part }))
				);
			} else {
				// Keep the original event if no split occurred
				result.push(event);
			}
		}

		return result;
	}

	supabase
		.channel('events-channel')
		.on(
			'postgres_changes',
			{ event: 'INSERT', schema: 'public', table: 'events' },
			(payload) => {
				if (payload.new.session_id !== profile.id) return;
				console.log(`got ${payload.new.event_type} event`);
				if (payload.new.name === 'user' || payload.new.event_type === 'tool') return;

				events = [...events, payload.new as Tables['events']['Row']];
				isTyping = false;
			}
		)
		.subscribe();

	// filter events by session_id
	$: shownEvents = splitEvents(
		events
			.filter((msg) => msg.session_id === profile.id)
			.filter(
				(msg) =>
					msg.event_type === 'ai' ||
					msg.event_type === 'user' ||
					msg.event_type === 'human' // ai messages can be of message_type 'human'. that's why it's distinctly different from 'user'
			)
			.filter((msg) => msg.content !== '')
			.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
	);

</script>

<div class="items-between flex flex-col justify-start gap-2 overflow-y-scroll pt-2">
	{#each shownEvents as msg, i (i)}
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
	<ChatBox bind:isTyping bind:events {profile} />
</div>
