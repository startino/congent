import type { Checkpoint } from "./supabase"
import type {
  BaseCheckpointSaver,
  Checkpoint,
  CheckpointMetadata,
  CheckpointTuple,
  SerializerProtocol,
} from "@langchain/langgraph";


export type Message = {
  id: string[]
  lc: number
  type: string
  kwargs: {
    id: string
    name?: string
    type: string
    status?: string
    content: string
    tool_call_id?: string
    tool_calls?: any[]
    usage_metadata?: {
      input_tokens: number
      total_tokens: number
      output_tokens: number
    }
    additional_kwargs?: {
      refusal?: any
    }
    response_metadata?: {
      logprobs?: any
      model_name: string
      token_usage: {
        total_tokens: number
        prompt_tokens: number
        completion_tokens: number
      }
      finish_reason: string
      system_fingerprint: string
    }
    invalid_tool_calls?: any[]
  }
}

export type WriteObject = {
  messages: Message[]
}

export type Writes = {
  tools?: WriteObject
  agent?: WriteObject
  __start__?: {
    messages: [string, string][]
  }
  [key: string]: any
}

export type CheckpointMetadata = {
  step: number
  source: string
  writes: Writes | null
  parents: Record<string, any>
}

export const checkpointsToMessages = (checkpoints: Checkpoint[]): Message[] => {
  let checkPointsMetadata: CheckpointMetadata[] = checkpoints.map(
    (checkpoint: Checkpoint) => checkpoint.metadata as CheckpointMetadata,
  )
  const messages: Message[] = []
  checkPointsMetadata.forEach((metadata) => {
    if (metadata.writes) {
      if (metadata.writes.agent) {
        messages.push(...metadata.writes.agent.messages)
      }
      if (metadata.writes.tools) {
        messages.push(...metadata.writes.tools.messages)
      }
    }
  })

  return messages
}
