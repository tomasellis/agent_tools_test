import * as v from "valibot";
import "dotenv/config";

export const server_env_schema = v.object(
  {
    DATABASE_URL: v.string(),
    DATABASE_AUTH_TOKEN: v.optional(v.string()),
    OPENAI_API_KEY: v.string(),
    LANGCHAIN_SERVER_URL: v.string(),
  },
  [
    v.forward(
      v.custom(({ DATABASE_URL, DATABASE_AUTH_TOKEN }) => {
        const file_url = DATABASE_URL.startsWith("file:");
        return file_url ? true : DATABASE_AUTH_TOKEN != null;
      }, "DATABASE_AUTH_TOKEN is required when DATABASE_URL is not a 'file:' URL"),
      ["DATABASE_AUTH_TOKEN"]
    ),
  ]
);

export const server_env = (() => {
  const res = v.safeParse(server_env_schema, process.env);
  if (res.success) return res.output;

  const msgs = res.issues
    .map((issue) => {
      const path = issue.path
        ?.map((p) => p.key)
        .join(".")
        .concat(": ");
      return `❌ ${path}${issue.message}`;
    })
    .join("\n");

  console.error(`Found the following issues with server_env:\n${msgs}`);
  throw new Error("Invalid server_env");
})();
