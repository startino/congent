import {
  PUBLIC_SUPABASE_ANON_KEY,
  PUBLIC_SUPABASE_URL,
} from "$env/static/public"
import type { RequestEvent } from "@sveltejs/kit"
import type { Database } from "."
import { createServerClient } from "@supabase/ssr"
import { createClient } from "@supabase/supabase-js"
export const createSupabase = (
  event: RequestEvent<Partial<Record<string, string>>, string | null>,
) => {
  return createServerClient<Database>(
    PUBLIC_SUPABASE_URL,
    PUBLIC_SUPABASE_ANON_KEY,
    {
      cookies: {
        get: (key) => event.cookies.get(key),
        /**
         * Note: You have to add the `path` variable to the
         * set and remove method due to sveltekit's cookie API
         * requiring this to be set, setting the path to an empty string
         * will replicate previous/standard behaviour (https://kit.svelte.dev/docs/types#public-types-cookies)
         */
        set: (key, value, options) => {
          event.cookies.set(key, value, { ...options, path: "/" })
        },
        remove: (key, options) => {
          event.cookies.delete(key, { ...options, path: "/" })
        },
      },
    },
  )
}

export const supabase = createClient<Database>(
  PUBLIC_SUPABASE_URL,
  PUBLIC_SUPABASE_ANON_KEY,
)
