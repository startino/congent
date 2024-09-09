import {
  getContext as getSvelteContext,
  setContext as setSvelteContext,
} from "svelte"
import type { Infer, SuperValidated } from "sveltekit-superforms"
import type { MessageSchema } from "$lib/schema"
import type { Writable } from "svelte/store"

export function setContext<K extends keyof ContextMap>(
  key: K,
  value: ContextMap[K],
) {
  return setSvelteContext(key, value)
}

export function getContext<K extends keyof ContextMap>(key: K): ContextMap[K] {
  console.log("KEY", key)
  const svelteContext = getSvelteContext<ContextMap[K]>(key)
  console.log("svelteContext: ", svelteContext)
  return svelteContext
}

export interface ContextMap {
  forms: FormsContext
}

// Contexts:

export interface FormsContext {
  message: SuperValidated<Infer<MessageSchema>>
}
