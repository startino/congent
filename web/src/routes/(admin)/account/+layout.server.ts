import { redirect } from "@sveltejs/kit"
import type { LayoutServerLoad } from "./$types"

export const load: LayoutServerLoad = async ({
  cookies, locals: { supabase, user },
}) => {

  const { data: profile } = await supabase
    .from("profiles")
    .select(`*`)
    .eq("id", user.id)
    .single()

  	return {
      user,
      cookies: cookies.getAll(),
    }  
}
