import { Workspace } from "@/components/workspace/workspace";
import { cookies } from "next/headers";
import { authConfiguration, authCookieName } from "@/lib/server-auth";

export default async function Chat() {
  const jar = await cookies(), config = authConfiguration();
  const key = config ? authCookieName(config.url) : null;
  // This only chooses UI controls. Every supplied token is verified again by the API.
  const signedIn = jar.getAll().some(({ name }) => key
    ? name === key || name.startsWith(key + ".") : /^sb-.+-auth-token(?:\.\d+)?$/.test(name));
  return <Workspace signedIn={signedIn} />;
}
