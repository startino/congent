<script lang="ts">
	import ChatBox from './ChatBox.svelte';
	import type { Tables } from '$lib/supabase';
	import SvelteMarkdown from 'svelte-markdown';
	import * as Avatar from "$lib/components/ui/avatar/index.js";
	import { onMount } from 'svelte';
	import { BaseMessage, AIMessage, ToolMessage } from '@langchain/core/messages';
  	import { supabase } from '$lib/supabase';

	import {v4 as uuidv4} from 'uuid';

	export let events: Tables['events']['Row'][] = [];
	export let profile: Tables['profiles']['Row'];

	let isTyping = false;
	let streamingContent = '';

	function splitEvents(events: Tables['events']['Row'][]): Tables['events']['Row'][] {
		const result: Tables['events']['Row'][] = [];

		for (const event of events) {
			if (!event.content) {
				event.content = "NO CONTENT";
			}

			result.push(event);

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
			}
		)
		.on(
			'postgres_changes',
			{ event: 'DELETE', schema: 'public', table: 'events' },
			(payload) => {

				events = [...events, payload.new as Tables['events']['Row']];
			}
		)
		.subscribe();


	let shownEvents: Tables['events']['Row'][] = [];
	$: {
		let eventsWithStreaming = [...events,{
			id: uuidv4(),
			session_id: profile.id,
			created_at: new Date().toISOString(),
			content: streamingContent,
			message_object: {},
			event_type: 'ai',
			sources: {},
			name: 'ai'
		} as Tables['events']['Row']];

		shownEvents = splitEvents(
			eventsWithStreaming
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
	}

</script>

<div class="items-between flex flex-col justify-start gap-2 overflow-y-scroll px-2 pt-2">
	{#each shownEvents as msg, i (i)}
		{#if msg != null}
			<div class={`flex my-2 ${msg.event_type === 'user' ? 'ml-16 justify-end' : 'mr-16 justify-start'}`}>
				{#if msg.event_type === "ai"}
				<Avatar.Root class="mt-auto mr-2 aspect-square">
					<Avatar.Image src="favicon.png" alt="@shadcn" />
					<Avatar.Fallback>CN</Avatar.Fallback>
				  </Avatar.Root>
				{/if}
				<p
					class="prose prose-main text-white rounded-lg border border-primary/30 bg-primary-container/10 px-2 py-1 text-primary-container-on marker:text-primary"
				>
				
					<SvelteMarkdown bind:source={msg.content} />
				</p>

			</div>
		{/if}
	{/each}

	{#if isTyping}
		<div class="mr-16 flex animate-pulse justify-start">
			<p
				class="rounded-lg border border-primary/30 bg-primary-container/10 px-2 py-1 text-primary-container-on animate-pulse"
			>
				I'm cooking bro, hol'up...
			</p>
		</div>
	{/if}
</div>
<div class="items-between flex flex-col justify-end gap-2">
	<hr class="mt-2 border-primary/10" />
	<ChatBox bind:isTyping bind:events bind:streamingContent {profile} />
</div>
