<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Trash2 } from 'lucide-svelte';
	import supabase from '$lib/supabase';
	import { toast } from 'svelte-sonner';

	export let profileId: string;

	const resetCheckpoins = async () => {
		const { error } = await supabase.from('checkpoints').delete().eq('', profileId);

		if (error) {
			toast.error('Error deleting history');
			console.error('Error deleting history:', JSON.stringify(error, null, 2));
			return;
		}

		location.reload();
	};
</script>

<Button on:click={resetCheckpoins} variant="destructive" class="aspect-1 p-1">
	<Trash2 class="h-6 w-6" />
</Button>
