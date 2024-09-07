import { z } from 'zod';

export const messageSchema = z.object({
	profile_id: z.string().uuid(),
	content: z.string().min(1).max(2000),
});

const genericSchema = z.object({
	label: z.string(),
	value: z.string(),
	description: z.string(),
});

export const profileSchema = z.object({
	id: z.string().uuid(),
	first_name: z.string().min(1).max(20),
	last_name: z.string().min(1).max(40),
});

export type MessageSchema = typeof messageSchema;
