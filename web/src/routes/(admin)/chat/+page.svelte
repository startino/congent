<script lang="ts">
  import Chat from "./Chat.svelte"
  import { Skeleton } from "$lib/components/ui/skeleton"
  import { BaseMessage, AIMessage } from "@langchain/core/messages"
  import type { Tables } from "$lib/supabase"
  export let data

  let {
    profile,
    events,
  }: { profile: Tables["profiles"]["Row"]; events: Tables["events"]["Row"][] } = data
  
</script>

<main class="flex h-full w-full flex-col items-center justify-center">
  <div
    class="items-between flex h-screen w-full max-w-2xl flex-col justify-between"
  >

    {#await events}
      <div class="flex w-full flex-col items-center justify-start gap-4 p-8">
        {#each Array.from({ length: 4 }) as _}
          <div class="flex h-12 w-full gap-2 pl-16">
            <Skeleton class="h-full w-full" />
            <Skeleton class="size-12 rounded-full" />
          </div>
          <div class="flex h-12 w-full gap-2 pr-16">
            <Skeleton class="size-12 rounded-full" />
            <Skeleton class="h-full w-full" />
          </div>
        {/each}
      </div>
      <Skeleton class="m-4 h-12 w-full" />
    {:then events}
      {#if events}
        <Chat {profile} {events} />
      {:else}
        <p>Error getting events, check console.</p>
      {/if}
    {:catch error}
      <p>Error: {error.event}</p>
    {/await}
  </div>
</main>
