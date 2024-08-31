import { error, fail, redirect } from "@sveltejs/kit"
import type { LayoutServerLoad } from "./$types"
import { NodeHtmlMarkdown } from 'node-html-markdown';
import { superValidate } from "sveltekit-superforms";
import { zod } from 'sveltekit-superforms/adapters';
import { messageSchema } from "$lib/schema";

export const load: LayoutServerLoad = async ({params,
  locals: { supabase, session },
}) => {

  const forms = {
		message: await superValidate(zod(messageSchema)),
	};

  const { data: profile, error: eProfile } = await supabase
		.from('profiles')
		.select('*')
		.eq('id', session.user.id)
		.single();

	if (!profile || eProfile) {
		const message = `Error getting profile: ${JSON.stringify(eProfile, null, 2)}`;
		console.error(message);
		throw redirect(303, '/');
	}

  const { data: checkpoints, error: eCheckpoints } = await supabase.from("checkpoints").select(`*`).eq("thread_id", profile.id)	

	if (!checkpoints || eCheckpoints) {
		const message = `Error getting events: ${JSON.stringify(eCheckpoints, null, 2)}`;
		console.error(message);
		throw error(500, 'Error getting events.');
	}

	return {
		checkpoints,
		profile,
		forms,
	};
}


export const actions = {
	send: async ({ request }) => {
		const form = await superValidate(request, zod(messageSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const content = NodeHtmlMarkdown.translate(form.data.content);

		//await run(form.data.profile_id, content, form.data.useExamplePrompts);

		return { form };
	},
};
