import type { Checkpoint as Row} from "./supabase"
import type {
  Checkpoint,
  CheckpointMetadata,
  CheckpointTuple,
  SerializerProtocol,
} from "@langchain/langgraph";


type Message = {
  sender: string;
  content: string;
  type: string;
};

export const checkpointsToMessages = (checkpoints: Row[]): Message[] => {

  let checkpointsMetadata: CheckpointMetadata[] = checkpoints
    .map((checkpoint: Row) => checkpoint.metadata as unknown as CheckpointMetadata)
    .filter(metadata => metadata.writes); // Filter out undefined values

  let messages: Message[] = [];
  for (const metadata of checkpointsMetadata) {
    if (metadata.writes?.agent) {
      const writes = metadata.writes;
      // usually "tools", "agent", "__start__"
      const writesChild: string = Object.keys(writes)[0];
      const uglyMessageObject: any = writes[writesChild];
      // Add the children to the messages array
      messages.push({
        sender: uglyMessageObject.kwargs.name,
        content: uglyMessageObject.kwargs.content,
        type: uglyMessageObject.kwargs.type,
      });
    }


  return messages;
}
