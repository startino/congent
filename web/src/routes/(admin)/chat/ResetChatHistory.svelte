<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Trash2 } from 'lucide-svelte';
	import { supabase } from '$lib/supabase';
	import { toast } from 'svelte-sonner';
	import { LoaderCircle } from 'lucide-svelte';

	export let profileId: string;

	let loading = false;

	const resetChatHistory = async () => {
		loading = true;
		const { error } = await supabase.from('events').delete().eq('session_id', profileId);

		if (error) {
			toast.error('Error deleting history');
			console.error('Error deleting history:', JSON.stringify(error, null, 2));
			return;
		}
		else {
			toast.success('Chat history deleted');
		}
		loading = false;
	};
</script>

{#if loading}
	<div class="fixed inset-0 flex items-center flex-col justify-center bg-black/50 z-50">
		Deleting chat history... unlucky if it was an accident!
		<LoaderCircle class="animate-spin w-32 h-32 text-teal-700" />
	</div>
{/if}

<Button on:click={resetChatHistory} variant="destructive" class="aspect-1 p-1">
	<Trash2 class="h-6 w-6" />
</Button>
