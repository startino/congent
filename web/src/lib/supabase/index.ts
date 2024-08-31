import type { Database, Json } from '$lib/supabase/database.types';
import { supabase } from '$lib/supabase/client';
import { z } from 'zod';

type Tables = Database['public']['Tables'];
type Enums = Database['public']['Enums'];
type Views = Database['public']['Views'];
type Functions = Database['public']['Functions'];
type CompositeTypes = Database['public']['CompositeTypes'];

export default supabase;

export type { Tables, Enums, Views, Functions, CompositeTypes, Json };

type Checkpoint = Tables['checkpoints']['Row'];
type Profile = Tables['profiles']['Row'];

export type { Database, Checkpoint, Profile };
