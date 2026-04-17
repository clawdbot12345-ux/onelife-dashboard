import { redirect } from "next/navigation";

// From Pass 3: root opens the app. /design remains reachable for audit.
export default function Root() {
  redirect("/home");
}
