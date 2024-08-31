import { messageSchema } from '$lib/schema';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';

export const load = async ({ url, locals: { session }, cookies }) => {
	const forms = {
		message: await superValidate(zod(messageSchema)),
	};

	return {
		session,
		forms,
	};
};
