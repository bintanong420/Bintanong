import { DefaultChatTransport } from "ai";
import { z } from "zod";
import { answerMetadataSchema, confirmedSchema, choiceSchema, curriculaSchema, sourceIdSchema, sourceSchema, uploadIdSchema, uploadSchema,
  StudentTransportError, type StudentAnswer, type StudentChoice, type StudentRequest, type StudentScope, type StudentSourceSummary } from "./student-contracts.ts";

type Options = { signal: AbortSignal; onText: (text: string) => void; onProgress?: (code: string) => void; fetch?: typeof fetch };
export async function boundedJSON(response: Response, limit = 1048576) {
  if (!response.body) throw new StudentTransportError("invalid_response");
  const reader = response.body.getReader(), chunks: Uint8Array[] = [];
  let bytes = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      bytes += value.byteLength;
      if (bytes > limit) throw new StudentTransportError("invalid_response");
      chunks.push(value);
    }
  } finally { await reader.cancel().catch(() => {}); reader.releaseLock(); }
  const result = new Uint8Array(bytes); let offset = 0;
  for (const chunk of chunks) { result.set(chunk, offset); offset += chunk.byteLength; }
  return JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(result));
}

async function checkedFetch(url: RequestInfo | URL, init: RequestInit, fetcher = fetch) {
  let response: Response;
  try { response = await fetcher(url, { ...init, cache: "no-store", credentials: "same-origin" }); }
  catch (error) { if (init.signal?.aborted) throw error; throw new StudentTransportError("connection_failed", 503); }
  if (!response.ok) {
    let code = "request_failed";
    try { const value = await boundedJSON(response, 8192); if (/^[a-z_]{1,64}$/.test(value?.error)) code = value.error; } catch {}
    throw new StudentTransportError(code, response.status);
  }
  return response;
}

export async function getStudentCurricula(signal: AbortSignal, fetcher = fetch) {
  return curriculaSchema.parse(await boundedJSON(await checkedFetch("/api/curricula", { signal }, fetcher))).curricula;
}
export async function clearStudentSession(signal: AbortSignal, fetcher = fetch) {
  await checkedFetch("/api/session", { method: "DELETE", signal }, fetcher);
}
export async function getStudentSource(sourceId: string, signal: AbortSignal, fetcher = fetch) {
  sourceIdSchema.parse(sourceId);
  const source = sourceSchema.parse(await boundedJSON(await checkedFetch("/api/sources/" + sourceId, { signal }, fetcher)));
  if (source.sourceId !== sourceId) throw new StudentTransportError("source_identity_mismatch");
  return source;
}
export async function uploadStudentFile(file: File, scope: StudentScope, signal: AbortSignal, fetcher = fetch) {
  if (!/\.pdf$/i.test(file.name) || file.size < 1 || file.size > 15 * 1024 * 1024) throw new StudentTransportError("choose_supported_pdf", 422);
  const query = new URLSearchParams({ programId: scope.programId, curriculumId: scope.curriculumId });
  return uploadSchema.parse(await boundedJSON(await checkedFetch("/api/uploads?" + query, {
    method: "POST", signal, headers: { "Content-Type": "application/octet-stream" }, body: file,
  }, fetcher)));
}
export async function confirmStudentFile(uploadId: string, decisions: StudentChoice[], signal: AbortSignal, fetcher = fetch) {
  uploadIdSchema.parse(uploadId);
  const body = { decisions: z.array(choiceSchema).min(1).max(256).parse(decisions) };
  return confirmedSchema.parse(await boundedJSON(await checkedFetch("/api/uploads/" + uploadId + "/confirm", {
    method: "POST", signal, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  }, fetcher)));
}
export async function removeStudentFile(uploadId: string, signal: AbortSignal, fetcher = fetch) {
  uploadIdSchema.parse(uploadId);
  await checkedFetch("/api/uploads/" + uploadId, { method: "DELETE", signal }, fetcher);
}

export async function sendStudentMessage(request: StudentRequest, options: Options): Promise<StudentAnswer> {
  const transport = new DefaultChatTransport({ api: "/api/chat", credentials: "same-origin",
    prepareSendMessagesRequest: () => ({ body: {
      id: "current", trigger: "submit-message", messages: [{ id: request.id, role: "user", parts: [{ type: "text", text: request.text }] }],
      ...(request.programId && request.curriculumId ? { programId: request.programId, curriculumId: request.curriculumId } : {}),
    } }),
    fetch: async (url, init) => {
      const response = await checkedFetch(url, init ?? {}, options.fetch ?? fetch);
      if (!response.body || !response.headers.get("content-type")?.startsWith("text/event-stream")) throw new StudentTransportError("invalid_stream");
      let size = 0;
      return new Response(response.body.pipeThrough(new TransformStream<Uint8Array, Uint8Array>({ transform(chunk, controller) {
        size += chunk.byteLength;
        if (size > 524288) throw new StudentTransportError("invalid_stream");
        controller.enqueue(chunk);
      } })), { headers: response.headers });
    },
  });
  const stream = await transport.sendMessages({ chatId: "current", trigger: "submit-message", messageId: undefined, messages: [], abortSignal: options.signal });
  const reader = stream.getReader(), sources: StudentSourceSummary[] = [];
  let text = "", summary: ReturnType<typeof answerMetadataSchema.parse> | undefined, finished = false, count = 0;
  let textId: string | null = null, textEnded = false;
  try {
    while (true) {
      const { done, value: chunk } = await reader.read();
      if (done) break;
      if (++count > 256 || finished) throw new StudentTransportError("invalid_stream");
      switch (chunk.type) {
        case "error": throw new StudentTransportError(/^[a-z_]{1,64}$/.test(chunk.errorText) ? chunk.errorText : "answer_unavailable");
        case "data-status": {
          const data = z.strictObject({ stage: z.enum(["waiting", "understanding", "writing"]) }).parse(chunk.data);
          options.onProgress?.(data.stage); break;
        }
        case "text-start":
          if (textId !== null) throw new StudentTransportError("invalid_stream");
          textId = chunk.id; break;
        case "text-delta":
          if (chunk.id !== textId || textEnded || summary) throw new StudentTransportError("invalid_stream");
          text += chunk.delta;
          if (text.length > 65536) throw new StudentTransportError("invalid_stream");
          options.onText(chunk.delta); break;
        case "text-end":
          if (chunk.id !== textId || textEnded) throw new StudentTransportError("invalid_stream");
          textEnded = true; break;
        case "source-document":
          sourceIdSchema.parse(chunk.sourceId);
          if (sources.length >= 64 || sources.some(s => s.sourceId === chunk.sourceId) || chunk.title.length > 2048) throw new StudentTransportError("invalid_stream");
          sources.push({ sourceId: chunk.sourceId, title: chunk.title }); break;
        case "data-answer":
          if (summary || !textEnded) throw new StudentTransportError("invalid_stream");
          summary = answerMetadataSchema.parse(chunk.data); break;
        case "finish": finished = true; break;
        case "start": break;
        default: throw new StudentTransportError("invalid_stream");
      }
    }
    if (!finished || !summary || !textEnded || !text) throw new StudentTransportError("incomplete_response");
    return { ...summary, text, sources };
  } finally { await reader.cancel().catch(() => {}); reader.releaseLock(); }
}
