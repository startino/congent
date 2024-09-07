<script>
	import { onMount } from 'svelte';
  
  // Make sure to use onMount and render deep-chat on load
	onMount(async () => {
		await import("deep-chat");
        isLoaded = true;
	});

    import type { Checkpoint, Tables } from '$lib/supabase';
	import SvelteMarkdown from 'svelte-markdown';
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

		result.push({
			id: uuidv4(),
			session_id: profile.id,
			created_at: new Date().toISOString(),
			content: streamingContent,
			message_object: {},
			event_type: 'ai',
			sources: {},
			name: 'ai'
		});

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

  let isLoaded = false;
	const history = [
		{ role: "user", text: "Hey, how are you today?" },
		{ role: "ai", text: "I am doing very well!" }
	];
</script>

<main>
	<h1>Deep Chat</h1>
  {#if isLoaded}
    <!-- demo/textInput are examples of passing an object directly into a property -->
    <!-- history is an example of passing an object from script into a property -->
    <deep-chat
      demo={true}
      connect='{
        "url":"http://localhost:8000/chat",
        "method": "POST",
        "headers": {
				'Content-Type': 'application/json',
				'Connection': 'keep-alive',
			},
        "body": JSON.stringify({
            session_id: profile.id,
            user_message: reply,
        }),
  }'
      textInput={{"placeholder":{"text": "Welcome to the demo!"}}}
      history={history}
    />
  {/if}
</main>

<style>
  main {
    font-family: sans-serif;
    text-align: center;
    justify-content: center;
    display: grid;
  }
</style>