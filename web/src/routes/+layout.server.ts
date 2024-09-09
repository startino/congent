import { messageSchema } from "$lib/schema"
import { error } from "@sveltejs/kit"
import { message, superValidate } from "sveltekit-superforms"
import { zod } from "sveltekit-superforms/adapters"

export const load = async ({ cookies, locals: { user, supabase } }) => {
  const forms = {
    message: await superValidate(zod(messageSchema)),
  }

  return {
    forms,
  }
}
