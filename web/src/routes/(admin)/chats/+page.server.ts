import { redirect } from "@sveltejs/kit"
import type { LayoutServerLoad } from "./$types"

export const load: LayoutServerLoad = async ({
  locals: { supabase, safeGetSession },
}) => {
  const { session } = await safeGetSession()

  if (!session) {
    redirect(303, "/login")
  }

  const { data: profile } = await supabase
    .from("profiles")
    .select(`*`)
    .eq("id", session.user.id)
    .single()

  const { data: checkpoints } = await supabase.from("checkpoints").select(`*`).eq("thread_id", profile.id)
  return { session, profile, checkpoints }
}
