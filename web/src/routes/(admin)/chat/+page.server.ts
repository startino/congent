import { error, fail, redirect } from "@sveltejs/kit"
import type { LayoutServerLoad } from "./$types"
import { NodeHtmlMarkdown } from "node-html-markdown"
import { superValidate } from "sveltekit-superforms"
import { zod } from "sveltekit-superforms/adapters"
import { messageSchema } from "$lib/schema"

export const load: LayoutServerLoad = async ({
  params,
  locals: { supabase, user },
}) => {
  const forms = {
    message: await superValidate(zod(messageSchema)),
  }

  const { data: profile, error: eProfile } = await supabase
    .from("profiles")
    .select("*")
    .eq("id", user.id)
    .single()

  if (!profile || eProfile) {
    const message = `Error getting profile: ${JSON.stringify(eProfile, null, 2)}`
    console.error(message)
    throw redirect(303, "/")
  }

  const { data: events, error: eEvents } = await supabase
    .from("events")
    .select(`*`)
    .eq("session_id", profile.id)

  if (!events || eEvents) {
    const message = `Error getting events: ${JSON.stringify(eEvents, null, 2)}`
    console.error(message)
    throw error(500, "Error getting events.")
  }

  return {
    events: events,
    profile,
    forms,
  }
}

export const actions = {
  send: async ({ request }) => {
    const form = await superValidate(request, zod(messageSchema))

    if (!form.valid) {
      return fail(400, { form })
    }

    const content = NodeHtmlMarkdown.translate(form.data.content)

    return { form, content }
  },
}
