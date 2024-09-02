<script lang="ts">

	import { Toaster } from '$lib/components/ui/sonner';
	import { invalidate } from '$app/navigation';
	import { onMount } from 'svelte';
	import { cn } from '$lib/utils';
	export let data;

	$: ({ user, supabase } = data);

	onMount(() => {
		const { data } = supabase.auth.onAuthStateChange((_, newUser) => {
			if (newUser?.expires_at !== user?.expires_at) {
				invalidate('supabase:auth');
			}
		});

		return () => data.subscription.unsubscribe();
	});


</script>

<Toaster />

<slot />