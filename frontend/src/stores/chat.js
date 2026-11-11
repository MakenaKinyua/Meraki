import { defineStore } from "pinia";
import { queryOptions } from "@tanstack/vue-query";
import {
  ApiError,
  createConversation,
  fetchConversation,
  fetchConversations,
} from "@/api/conversations";
import { queryClient } from "@/lib/query-client";

const STORAGE_KEY = "meraki-conversation-id";
const NEW_TITLE = "New conversation";
const ERROR_TEXT = "Something went wrong. Try again.";

const conversationsQuery = () =>
  queryOptions({
    queryKey: ["conversations"],
    queryFn: fetchConversations,
  });

const conversationQuery = (id) =>
  queryOptions({
    queryKey: ["conversations", id],
    queryFn: () => fetchConversation(id),
  });

const toMessages = (conversation) =>
  conversation.messages.map((m) => ({
    id: m.id,
    role: m.role,
    parts: [{ type: "text", content: m.content }],
    createdAt: new Date(m.created_at),
  }));

export const useChatStore = defineStore("chat", {
  state: () => ({
    conversationId: localStorage.getItem(STORAGE_KEY) || "",
    conversationTitle: NEW_TITLE,
    conversations: [],
    messages: [],
    error: "",
    isLoading: false,
    isInitializing: true,
    isOnline: true,
    streamInterrupted: false,
  }),
  actions: {
    setConversation(id, title = NEW_TITLE) {
      this.conversationId = id;
      this.conversationTitle = title;
      if (id) localStorage.setItem(STORAGE_KEY, id);
      else localStorage.removeItem(STORAGE_KEY);
    },
    setOnline(value) {
      this.isOnline = value;
      if (!value && this.isLoading) this.streamInterrupted = true;
    },
    async loadConversations() {
      try {
        this.conversations = await queryClient.query(conversationsQuery());
      } catch (error) {
        this.handleConnectionError(error);
      }
      return this.conversations;
    },
    async loadConversation(id = this.conversationId) {
      if (!id) {
        this.setConversation("");
        this.messages = [];
        return [];
      }
      try {
        const conversation = await queryClient.query(conversationQuery(id));
        this.setConversation(id, conversation.title || NEW_TITLE);
        this.messages = toMessages(conversation);
        return this.messages;
      } catch (error) {
        if (error instanceof ApiError && error.status === 404) {
          this.setConversation("");
          this.messages = [];
          return [];
        }
        const cached = queryClient.getQueryData(conversationQuery(id).queryKey);
        if (cached) {
          this.setConversation(id, cached.title || NEW_TITLE);
          this.messages = toMessages(cached);
          return this.messages;
        }
        this.handleConnectionError(error);
        return null;
      }
    },
    async createConversation() {
      const conversation = await createConversation();
      this.setConversation(conversation.id);
      queryClient.setQueryData(
        conversationQuery(conversation.id).queryKey,
        conversation,
      );
      queryClient.setQueryData(conversationsQuery().queryKey, (old = []) => [
        conversation,
        ...old,
      ]);
      return conversation.id;
    },
    startNewChat() {
      this.clearStreamInterrupted();
      this.setConversation("");
      this.messages = [];
    },
    handleConnectionError(error) {
      if (!this.isOnline) return;
      if (error?.status) this.error = ERROR_TEXT;
      else this.markStreamInterrupted();
    },
    markStreamInterrupted() {
      this.streamInterrupted = true;
      this.error = "Connection lost. Sync to check for new messages.";
    },
    clearStreamInterrupted() {
      this.streamInterrupted = false;
      this.error = "";
    },
  },
});
