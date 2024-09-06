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

	export let events: Tables['events']['Row'][];
	export let profile: Tables['profiles']['Row'];
	export let isTyping: boolean;

	let reply = '';
	let replyBackup = reply;

	const forms = getContext('forms');
	const form = superForm(forms.message, {
		dataType: 'json',
		validators: zodClient(messageSchema),
		async onSubmit() {

			console.log('onSubmit', JSON.stringify($formData, null, 2));
			isTyping = true;

			$formData.profile_id = profile.id;
			$formData.content = reply;

			const newEventPlaceholder: Tables['events']['Row'] = {
				id: crypto.randomUUID(),
				session_id: $formData.profile_id,
				created_at: Date.now.toString(),
				content: $formData.content,
				message_object: {},
				event_type: 'human',
				sources: {},
				name: 'user'
			};

			events = [...events, newEventPlaceholder];

			replyBackup = reply;
			reply = '<p></p>';

			let chunks = [];

			const res = await fetch('http://localhost:8000/chat', 
				{
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						session_id: $formData.profile_id,
						user_message: $formData.content,
					}),

				});

			const reader = res.body?.getReader();

			reader.read().then(function processText({ done, value }) {
				console.log("value: ", value);
				if (done) {
				console.log("Stream complete");
				console.log("done value: ", value);
				return;
				}
			
			});
			console.log("chunks: ", chunks);
		},
		onResult(result) {
			console.log('onResult', JSON.stringify($formData, null, 2));
			console.log('chunks', result.result.data.streaming.chunks);
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
	
	onMount(() => {
		const urlParams = new URLSearchParams(window.location.search);
		debug = urlParams.has('debug');
	});

	const sendMessage = async () => {
		await fetch('http://localhost:8080/chat', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				session_id: profile.id,
				user_message: content,
			}),
		})
		.then((res) => res.json())
		.then((json) => {
			console.log(json);
		})
	}	

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
