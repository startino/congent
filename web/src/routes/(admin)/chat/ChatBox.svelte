<script lang="ts">
	import type { Tables } from '$lib/supabase';
	import { Send } from 'lucide-svelte';
	import * as Form from '$lib/components/ui/form';
	import SuperDebug, { superForm } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import { messageSchema } from '$lib/schema';
	import { getContext } from '$lib/context';
	import { toast } from 'svelte-sonner';
	import { onMount } from 'svelte';	
	import ResetChatHistory from './ResetChatHistory.svelte';
	import Textbubble from '$lib/components/ui/textbubble/textbubble.svelte';
	import { chunkArray } from '@langchain/core/utils/chunk_array'
	import { Button } from '$lib/components/ui/button'
	import {createParser, type ParsedEvent, type ReconnectInterval} from 'eventsource-parser'


	export let events: Tables['events']['Row'][];
	export let profile: Tables['profiles']['Row'];
	export let isTyping: boolean;

	let reply = '';
	let replyBackup = reply;
	
	export let streamingContent: string = "";

	const forms = getContext('forms');
	const form = superForm(forms.message, {
		dataType: 'json',
		validators: zodClient(messageSchema),
		async onSubmit() {

			console.log('onSubmit', JSON.stringify($formData, null, 2));
			isTyping = true;

			sendMessage();

			$formData.profile_id = profile.id;
			$formData.content = reply;

			const newEventPlaceholder: Tables['events']['Row'] = {
				id: crypto.randomUUID(),
				session_id: $formData.profile_id,
				created_at: Date.now.toString(),
				content: $formData.content,
				message_object: {},
				event_type: 'user',
				sources: {},
				name: 'user'
			};

			const messageBeingStreamed: Tables['events']['Row'] = {
				id: crypto.randomUUID(),
				session_id: $formData.profile_id,
				created_at: Date.now.toString(),
				content: streamingContent,
				message_object: {},
				event_type: 'ai',
				sources: {},
				name: null
			};

			events = [...events, newEventPlaceholder];

			replyBackup = reply;
			reply = '<p></p>';

			
		},
		onResult(result) {
			console.log('onResult', JSON.stringify($formData, null, 2));
			isTyping = false;
		},
		onError() {
			isTyping = false;
			reply = replyBackup;
			toast.error('Error sending message.');
		}
	});

	const { form: formData, enhance } = form;

	let debug = false;


	function onParse(event: ParsedEvent | ReconnectInterval) {
	if (event.type === 'event') {
		// console.log('Received event!')
		// console.log('id: %s', event.id || '<none>')
		// console.log('data: %s', event.data)
		streamingContent += event.data
	} else if (event.type === 'reconnect-interval') {
		console.log('We should set reconnect interval to %d milliseconds', event.value)
	}
	}

	const parser = createParser(onParse)

	const sendMessage = async () => {

		const res = await fetch('http://localhost:8000/chat', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Connection': 'keep-alive',
			},
			body: JSON.stringify({
				session_id: profile.id,
				user_message: reply,
			}),
		})
		.then(response => {
        const stream = response.body;
        const reader = stream?.getReader();
        const readChunk = () => {
            reader?.read()
                .then(({
                    value,
                    done
                }) => {
                    if (done) {
                        console.log('Stream finished');		
						streamingContent = "";
						// get and add the new event to the events list to
						// remove the slight glitch onthe frontend
                        return;
                    }
					// maybe this code can be improved:
					// const eventStream = response.body
					// .pipeThrough(new TextDecoderStream())
					// .pipeThrough(new EventSourceParserStream())

                    const chunkData = new TextDecoder().decode(value);

					parser.feed(chunkData)

                    readChunk();
                })
                .catch(error => {
                    console.error(error);
                });
        };
        readChunk();
    })
    .catch(error => {
        // Log the error
        console.error(error);
    });
	};

	onMount(() => {
		const urlParams = new URLSearchParams(window.location.search);
		debug = urlParams.has('debug');	
	});


</script>

{#if debug}
	<div class="fixed bottom-5 left-5 flex flex-col opacity-30">
		<SuperDebug data={$formData}></SuperDebug>
		<p class="rounded-lg bg-primary-container/10 p-2 text-primary-container-on">
			Reply: {reply}
		</p>
	</div>
{/if}

<div class="flex w-full flex-row">
	<form class="m-2 w-full items-center" method="POST" action="?/send" use:enhance>
		{#if isTyping}
			<small class="text-md animate-pulse self-start p-2">Agent is Typing...</small>
		{/if}
		<div class="flex w-full items-end justify-center gap-2">
			<ResetChatHistory profileId={profile.id} />
			<Form.Field {form} name="content" class="flex-1 space-y-0">
				<Form.Control let:attrs>
					<Form.FieldErrors />
					<Textbubble
						{...attrs}
						on:enter={() => form.submit()}
						class="min-w-screen flex-1 rounded-lg border border-primary/50 bg-primary-container/10 px-3 py-2 text-base text-primary-container-on marker:text-primary"
						bind:content={reply}
					/>
				</Form.Control>
			</Form.Field>
			<Form.Button disabled={isTyping} variant="secondary" class="aspect-1 p-1" type="submit">
				<Send />
			</Form.Button>
		</div>
	</form>
</div>
